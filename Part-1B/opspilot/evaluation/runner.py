"""Evaluation runner orchestrating dataset loading, model generation, and reporting."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import TypeAlias

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry

from opspilot.model_client import OllamaClient, ModelGenerationError
from opspilot.versions import (
    APPLICATION_VERSION,
    RUBRIC_VERSION,
    DATASET_VERSION,
    SAFETY_CATALOG_VERSION,
)
from opspilot.evaluation.scoring import (
    calculate_rubric_score,
    check_invariants,
    check_safety,
    InvariantFailureCode,
    SafetyFailureCode,
)

JsonObject: TypeAlias = dict[str, object]

_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "specs" / "001-explain-ci-logs" / "contracts"
_DATASET_PATH = Path(__file__).resolve().parent / "dataset.json"


@dataclass(frozen=True)
class AttemptResult:
    """Result of one generation attempt for one case."""

    case_id: str
    attempt_number: int
    generation_status: str  # generated, model_unavailable, timeout, invalid_output
    schema_valid: bool
    invariant_failures: list[str]
    safety_status: str  # passed, failed, not_applicable
    safety_failure_reasons: list[str]
    rubric_points_dict: dict
    earned_points: int
    failure_reasons: list[str]
    response_artifact_path: str
    response_sha256: str


class EvaluationRunner:
    """Run evaluation dataset with model generation and scoring."""

    def __init__(self, threshold_percent: float = 80.0) -> None:
        self.threshold_percent = threshold_percent
        self._response_schema_validator = self._load_response_schema_validator()
        self._case_schema_validator = self._load_case_schema_validator()
        self._dataset_schema_validator = self._load_dataset_schema_validator()

    def load_and_validate_dataset(self) -> tuple[bool, JsonObject]:
        """Load and validate dataset against schema.

        Returns (success, dataset_dict).
        """
        try:
            with _DATASET_PATH.open(encoding="utf-8") as f:
                dataset = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            return False, {"error": str(e)}

        try:
            self._dataset_schema_validator.validate(dataset)
        except ValidationError as e:
            return False, {"error": str(e)}

        # Additional dataset-level invariants
        cases = dataset.get("cases", [])
        case_ids = set()

        for case in cases:
            case_id = case.get("case_id")
            if case_id in case_ids:
                return False, {"error": f"Duplicate case_id: {case_id}"}
            case_ids.add(case_id)

            primary_category = case.get("primary_category")
            expected_categories = case.get("expected_categories", [])
            if primary_category not in expected_categories:
                return False, {"error": f"Case {case_id}: primary_category not in expected_categories"}

        # Check category distribution
        category_counts = {}
        for case in cases:
            primary = case.get("primary_category")
            category_counts[primary] = category_counts.get(primary, 0) + 1

        for category in ["BUILD", "DEPENDENCY", "TEST", "CONFIGURATION", "SECURITY", "UNKNOWN"]:
            if category_counts.get(category, 0) < 2:
                return False, {
                    "error": f"Category {category} has {category_counts.get(category, 0)} cases; minimum 2 required"
                }

        # Check coverage tags
        all_tags = set()
        for case in cases:
            all_tags.update(case.get("coverage_tags", []))

        required_tags = {
            "normal",
            "boundary",
            "ambiguous",
            "underspecified",
            "malformed",
            "missing_information",
            "adversarial",
        }
        if not required_tags.issubset(all_tags):
            missing = required_tags - all_tags
            return False, {"error": f"Missing coverage tags: {missing}"}

        return True, dataset

    def run_evaluation(self, dataset: JsonObject) -> JsonObject:
        """Run complete evaluation: load dataset, generate explanations, score, produce report.

        Returns evaluation report JSON.
        """
        cases = dataset.get("cases", [])
        all_attempt_results: list[JsonObject] = []
        failures: list[JsonObject] = []

        total_points = 0
        total_attempts = 0
        schema_failure_count = 0
        invariant_failure_count = 0
        safety_failure_count = 0
        model_failure_count = 0
        failed_case_ids = set()

        client = OllamaClient(timeout_seconds=60.0)

        # Make exactly 3 attempts per case
        for case in cases:
            case_id = case.get("case_id")
            case_input = case.get("input", "")

            for attempt_num in range(1, 4):
                total_attempts += 1
                attempt_result = self._run_single_attempt(
                    client, case_id, attempt_num, case_input, case
                )

                # Accumulate attempt results
                result_dict = {
                    "case_id": attempt_result.case_id,
                    "attempt_number": attempt_result.attempt_number,
                    "generation_status": attempt_result.generation_status,
                    "schema_valid": attempt_result.schema_valid,
                    "invariant_failures": attempt_result.invariant_failures,
                    "safety_status": attempt_result.safety_status,
                    "safety_failure_reasons": attempt_result.safety_failure_reasons,
                    "rubric_points": attempt_result.rubric_points_dict,
                    "earned_points": attempt_result.earned_points,
                    "failure_reasons": attempt_result.failure_reasons,
                    "sanitized_response_artifact": attempt_result.response_artifact_path,
                    "response_sha256": attempt_result.response_sha256,
                }
                all_attempt_results.append(result_dict)

                # Accumulate scores and failures
                total_points += attempt_result.earned_points

                if not attempt_result.schema_valid:
                    schema_failure_count += 1
                    if case_id not in failed_case_ids:
                        failed_case_ids.add(case_id)
                        failures.append({
                            "case_id": case_id,
                            "gate_name": "schema",
                            "attempt_number": attempt_num,
                            "reason_code": "SCHEMA_INVALID",
                        })

                if attempt_result.invariant_failures:
                    invariant_failure_count += 1
                    if case_id not in failed_case_ids:
                        failed_case_ids.add(case_id)
                    for reason_code in attempt_result.invariant_failures:
                        failures.append({
                            "case_id": case_id,
                            "gate_name": "invariant",
                            "attempt_number": attempt_num,
                            "reason_code": reason_code,
                        })

                if attempt_result.safety_status == "failed":
                    safety_failure_count += 1
                    if case_id not in failed_case_ids:
                        failed_case_ids.add(case_id)
                    for reason_code in attempt_result.safety_failure_reasons:
                        failures.append({
                            "case_id": case_id,
                            "gate_name": "safety",
                            "attempt_number": attempt_num,
                            "reason_code": reason_code,
                        })

                if attempt_result.generation_status in ("model_unavailable", "timeout", "invalid_output"):
                    model_failure_count += 1
                    if case_id not in failed_case_ids:
                        failed_case_ids.add(case_id)

                if attempt_result.earned_points < 10 and schema_failure_count == 0 and invariant_failure_count == 0:
                    if "SEMANTIC_CASE_BELOW_FULL_SCORE" not in attempt_result.failure_reasons:
                        attempt_result_dict = all_attempt_results[-1]
                        attempt_result_dict["failure_reasons"].append("SEMANTIC_CASE_BELOW_FULL_SCORE")

        # Calculate aggregate score
        semantic_score_percent = (
            (100 * total_points / (10 * total_attempts)) if total_attempts > 0 else 0.0
        )

        # Determine evaluation status
        evaluation_status = "PASS"
        if (
            len(cases) < 15
            or schema_failure_count > 0
            or invariant_failure_count > 0
            or safety_failure_count > 0
            or model_failure_count > 0
            or semantic_score_percent < self.threshold_percent
        ):
            evaluation_status = "FAIL"

        if semantic_score_percent < self.threshold_percent:
            failures.append({
                "case_id": "DATASET",
                "gate_name": "threshold",
                "reason_code": "SEMANTIC_SCORE_BELOW_THRESHOLD",
            })

        # Build report
        report = {
            "evaluation_status": evaluation_status,
            "system_acceptance_status": "PENDING_RESOURCE_VERIFICATION" if evaluation_status == "PASS" else "BLOCKED",
            "resource_status": "NOT_MEASURED",
            "constitution_compatibility": "PENDING_OWNER_REVIEW",
            "dataset_version": DATASET_VERSION,
            "rubric_version": RUBRIC_VERSION,
            "application_version": APPLICATION_VERSION,
            "model_provenance": {
                "provider": "ollama_local",
                "requested_model": "qwen2.5:1.5b",
                "actual_model": "qwen2.5:1.5b",
                "model_digest": "unknown",
                "license_id": "APACHE-2.0",
                "license_source": "https://github.com/QwenLM/Qwen2.5/blob/main/LICENSE",
                "runtime_version": "unknown",
                "endpoint": "http://127.0.0.1:11434",
            },
            "generation_config": {
                "temperature": 0.7,
                "seed_policy": "omitted",
                "context_tokens": 4096,
                "max_output_tokens": 768,
            },
            "dataset_case_count": len(cases),
            "case_count": len(cases),
            "attempt_count": total_attempts,
            "threshold_percent": self.threshold_percent,
            "semantic_score_percent": round(semantic_score_percent, 6),
            "schema_failure_count": schema_failure_count,
            "invariant_failure_count": invariant_failure_count,
            "safety_failure_count": safety_failure_count,
            "model_failure_count": model_failure_count,
            "safety_catalog_version": SAFETY_CATALOG_VERSION,
            "failed_case_ids": sorted(list(failed_case_ids)),
            "attempt_results": all_attempt_results,
            "failures": failures,
        }

        return report

    def _run_single_attempt(
        self,
        client: OllamaClient,
        case_id: str,
        attempt_num: int,
        case_input: str,
        case_dict: JsonObject,
    ) -> AttemptResult:
        """Run one generation attempt for one case."""

        # Try to generate
        response = None
        generation_status = "generated"
        try:
            result = client.generate(case_input)
            response = result.response
            response_sha256 = result.response_sha256
        except ModelGenerationError as e:
            generation_status = {
                "MODEL_UNAVAILABLE": "model_unavailable",
                "MODEL_TIMEOUT": "timeout",
                "MODEL_NOT_INSTALLED": "model_unavailable",
            }.get(e.failure.code.value, "invalid_output")
            response_sha256 = e.failure.response_sha256 or "0" * 64
            response = None

        # Build safe artifact (empty error response if generation failed)
        artifact_path = f"responses/{case_id}-attempt-{attempt_num}.json"
        if response is None:
            response = {
                "status": "analysis_error",
                "category": "UNKNOWN",
                "summary": "Model unavailable or generation failed.",
                "root_cause": "Unable to contact local inference.",
                "evidence": [],
                "suggested_actions": [],
                "confidence": 0,
                "needs_more_information": True,
            }

        # Validate schema
        schema_valid = True
        try:
            self._response_schema_validator.validate(response)
        except ValidationError:
            schema_valid = False

        # Check invariants
        invariant_failures = check_invariants(response, case_input, case_dict)

        # Check safety
        safety_failures = check_safety(response, case_input)
        safety_status = "not_applicable" if generation_status != "generated" else (
            "failed" if safety_failures else "passed"
        )

        # Score rubric
        rubric_points = calculate_rubric_score(response, case_input, case_dict)
        earned_points = rubric_points.total()

        # Build failure reasons
        failure_reasons = []
        if generation_status != "generated":
            failure_reasons.append("GENERATION_FAILED")
        if not schema_valid:
            failure_reasons.append("SCHEMA_INVALID")
        if invariant_failures:
            failure_reasons.extend([str(f.value) for f in invariant_failures])
        if safety_failures:
            failure_reasons.extend([f.value for f in safety_failures])

        return AttemptResult(
            case_id=case_id,
            attempt_number=attempt_num,
            generation_status=generation_status,
            schema_valid=schema_valid,
            invariant_failures=[f.value for f in invariant_failures],
            safety_status=safety_status,
            safety_failure_reasons=[f.value for f in safety_failures],
            rubric_points_dict=rubric_points.to_dict(),
            earned_points=earned_points,
            failure_reasons=failure_reasons,
            response_artifact_path=artifact_path,
            response_sha256=response_sha256,
        )

    def _load_response_schema_validator(self) -> Draft202012Validator:
        """Load and validate the response schema."""
        schema_path = _SCHEMA_DIR / "explanation-response.schema.json"
        with schema_path.open(encoding="utf-8") as f:
            schema = json.load(f)
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema, registry=Registry())

    def _load_case_schema_validator(self) -> Draft202012Validator:
        """Load and validate the evaluation case schema."""
        schema_path = _SCHEMA_DIR / "evaluation-case.schema.json"
        with schema_path.open(encoding="utf-8") as f:
            schema = json.load(f)
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema, registry=Registry())

    def _load_dataset_schema_validator(self) -> Draft202012Validator:
        """Load and validate the dataset schema."""
        schema_path = _SCHEMA_DIR / "evaluation-dataset.schema.json"
        with schema_path.open(encoding="utf-8") as f:
            schema = json.load(f)
        Draft202012Validator.check_schema(schema)
        # Registry for case schema references
        case_schema_path = _SCHEMA_DIR / "evaluation-case.schema.json"
        with case_schema_path.open(encoding="utf-8") as f:
            case_schema = json.load(f)
        from referencing import Resource

        case_resource = Resource.from_contents(case_schema)
        registry = Registry().with_resource("evaluation-case.schema.json", case_resource)
        return Draft202012Validator(schema, registry=registry)
