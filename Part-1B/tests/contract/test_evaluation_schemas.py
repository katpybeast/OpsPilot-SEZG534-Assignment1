"""T008: Evaluation Schema Contract Tests"""
import json
import pytest
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

SD = Path(__file__).parent.parent.parent / "specs" / "001-explain-ci-logs" / "contracts"
cs = json.load(open(SD / "evaluation-case.schema.json"))
ds = json.load(open(SD / "evaluation-dataset.schema.json"))
rs = json.load(open(SD / "evaluation-report.schema.json"))

cv = Draft202012Validator(cs)
crsc = Resource.from_contents(cs)
drsc = Resource.from_contents(ds)
rrsc = Resource.from_contents(rs)
creg = Registry().with_resource("evaluation-case.schema.json", crsc)
dreg = Registry().with_resource("evaluation-dataset.schema.json", drsc).with_resource("evaluation-case.schema.json", crsc)
rreg = Registry().with_resource("evaluation-report.schema.json", rrsc)
dv = Draft202012Validator(ds, registry=dreg)
rv = Draft202012Validator(rs, registry=rreg)

def vc():
    return {
        "case_id": "t-001",
        "input": "log",
        "primary_category": "BUILD",
        "coverage_tags": ["normal"],
        "expected_status": "ok",
        "expected_categories": ["BUILD"],
        "unknown_partial_credit": False,
        "required_evidence_markers": ["x"],
        "forbidden_evidence_markers": [],
        "required_cause_properties": ["y"],
        "forbidden_cause_properties": [],
        "required_action_properties": ["z"],
        "forbidden_action_properties": [],
        "expected_evidence_empty": False,
        "expected_actions_empty": False,
        "expected_confidence_values": [0.85],
        "expected_needs_more_information": False,
        "safe_uncertainty_partial_credit": False,
        "safety_expectations": {
            "no_execution": True,
            "no_sensitive_echo": True,
            "instruction_isolation": True
        }
    }

class TestCaseRequired:
    def test_valid(self):
        cv.validate(vc())

    def test_no_case_id(self):
        c = vc()
        del c["case_id"]
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_extra_prop(self):
        c = vc()
        c["x"] = 1
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestCaseFieldTypes:
    def test_case_id_not_str(self):
        c = vc()
        c["case_id"] = 1
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_input_empty(self):
        c = vc()
        c["input"] = ""
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_input_too_long(self):
        c = vc()
        c["input"] = "x" * 262145
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestCaseEnums:
    def test_status_ok(self):
        c = vc()
        c["expected_status"] = "ok"
        cv.validate(c)

    def test_status_insuf(self):
        c = vc()
        c["expected_status"] = "insufficient_information"
        c["expected_needs_more_information"] = True
        c["expected_confidence_values"] = [0.5]
        cv.validate(c)

    def test_status_invalid(self):
        c = vc()
        c["expected_status"] = "x"
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_coverage_valid(self):
        for tag in ["normal", "boundary", "ambiguous", "underspecified", "malformed", "missing_information", "adversarial"]:
            c = vc()
            c["coverage_tags"] = [tag]
            cv.validate(c)

    def test_coverage_invalid(self):
        c = vc()
        c["coverage_tags"] = ["bad"]
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestCaseStatusOkConditional:
    def test_ok_confidence_valid(self):
        for conf in [0.7, 0.85, 0.95]:
            c = vc()
            c["expected_status"] = "ok"
            c["expected_confidence_values"] = [conf]
            cv.validate(c)

    def test_ok_confidence_invalid_0_3(self):
        c = vc()
        c["expected_status"] = "ok"
        c["expected_confidence_values"] = [0.3]
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_ok_needs_info_must_be_false(self):
        c = vc()
        c["expected_status"] = "ok"
        c["expected_needs_more_information"] = True
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_ok_evidence_must_be_false(self):
        c = vc()
        c["expected_status"] = "ok"
        c["expected_evidence_empty"] = True
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_ok_actions_must_be_false(self):
        c = vc()
        c["expected_status"] = "ok"
        c["expected_actions_empty"] = True
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestCaseStatusInsufficientConditional:
    def test_insufficient_confidence_valid(self):
        for conf in [0.3, 0.5, 0.65]:
            c = vc()
            c["expected_status"] = "insufficient_information"
            c["expected_confidence_values"] = [conf]
            c["expected_needs_more_information"] = True
            cv.validate(c)

    def test_insufficient_confidence_invalid_0_7(self):
        c = vc()
        c["expected_status"] = "insufficient_information"
        c["expected_confidence_values"] = [0.7]
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_insufficient_needs_info_true(self):
        c = vc()
        c["expected_status"] = "insufficient_information"
        c["expected_needs_more_information"] = True
        c["expected_confidence_values"] = [0.5]
        cv.validate(c)

    def test_insufficient_actions_empty_true(self):
        c = vc()
        c["expected_status"] = "insufficient_information"
        c["expected_actions_empty"] = False
        c["required_action_properties"] = ["x"]
        c["expected_needs_more_information"] = True
        c["expected_confidence_values"] = [0.5]
        cv.validate(c)

    def test_insufficient_actions_empty_false(self):
        c = vc()
        c["expected_status"] = "insufficient_information"
        c["expected_actions_empty"] = False
        c["required_action_properties"] = ["x"]
        c["expected_needs_more_information"] = True
        c["expected_confidence_values"] = [0.5]
        cv.validate(c)

class TestCaseEvidenceConditional:
    def test_evidence_empty_true_no_markers(self):
        c = vc()
        c["expected_status"] = "insufficient_information"
        c["expected_needs_more_information"] = True
        c["expected_confidence_values"] = [0.5]
        c["expected_evidence_empty"] = True
        c["required_evidence_markers"] = []
        c["expected_actions_empty"] = False
        c["required_action_properties"] = ["x"]
        cv.validate(c)

    def test_evidence_empty_true_reject_markers(self):
        c = vc()
        c["expected_evidence_empty"] = True
        c["required_evidence_markers"] = ["x"]
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_evidence_empty_false_has_markers(self):
        c = vc()
        c["expected_evidence_empty"] = False
        c["required_evidence_markers"] = ["x"]
        cv.validate(c)

    def test_evidence_empty_false_no_markers_fails(self):
        c = vc()
        c["expected_evidence_empty"] = False
        c["required_evidence_markers"] = []
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestCaseActionsConditional:
    def test_actions_empty_true_reject_all_statuses(self):
        for status in ["ok", "insufficient_information"]:
            c = vc()
            c["expected_actions_empty"] = True
            c["required_action_properties"] = []
            c["expected_status"] = status
            if status == "insufficient_information":
                c["expected_needs_more_information"] = True
                c["expected_confidence_values"] = [0.5]
            with pytest.raises(ValidationError):
                cv.validate(c)

    def test_actions_empty_true_reject_props(self):
        c = vc()
        c["expected_actions_empty"] = True
        c["required_action_properties"] = ["x"]
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_actions_empty_false_has_props(self):
        c = vc()
        c["expected_actions_empty"] = False
        c["required_action_properties"] = ["x"]
        cv.validate(c)

    def test_actions_empty_false_no_props_fails(self):
        c = vc()
        c["expected_actions_empty"] = False
        c["required_action_properties"] = []
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestCaseUnknownConditional:
    def test_unknown_in_cats_credit_false(self):
        c = vc()
        c["expected_categories"] = ["UNKNOWN", "BUILD"]
        c["unknown_partial_credit"] = False
        cv.validate(c)

    def test_unknown_in_cats_credit_true_fails(self):
        c = vc()
        c["expected_categories"] = ["UNKNOWN"]
        c["unknown_partial_credit"] = True
        with pytest.raises(ValidationError):
            cv.validate(c)

    def test_unknown_not_in_cats_credit_true(self):
        c = vc()
        c["expected_categories"] = ["BUILD"]
        c["unknown_partial_credit"] = True
        cv.validate(c)

class TestCaseConfidenceEnums:
    def test_ok_valid_confidences(self):
        for conf in [0.7, 0.85, 0.95]:
            c = vc()
            c["expected_status"] = "ok"
            c["expected_confidence_values"] = [conf]
            cv.validate(c)

    def test_insufficient_valid_confidences(self):
        for conf in [0.3, 0.5, 0.65]:
            c = vc()
            c["expected_status"] = "insufficient_information"
            c["expected_needs_more_information"] = True
            c["expected_confidence_values"] = [conf]
            cv.validate(c)

    def test_invalid_confidence(self):
        c = vc()
        c["expected_confidence_values"] = [0.42]
        with pytest.raises(ValidationError):
            cv.validate(c)

class TestDatasetMinItems:
    def test_dataset_15_cases(self):
        d = {
            "dataset_version": "1.0",
            "cases": [{**vc(), "case_id": f"case-{i:02d}"} for i in range(15)]
        }
        dv.validate(d)

    def test_dataset_14_cases_fails(self):
        d = {
            "dataset_version": "1.0",
            "cases": [{**vc(), "case_id": f"case-{i:02d}"} for i in range(14)]
        }
        with pytest.raises(ValidationError):
            dv.validate(d)

    def test_dataset_0_cases_fails(self):
        d = {"dataset_version": "1.0", "cases": []}
        with pytest.raises(ValidationError):
            dv.validate(d)

class TestReportBasic:
    def test_report_pass_valid(self):
        r = {
            **{k: valid_report()[k] for k in [
                "evaluation_status", "system_acceptance_status", "resource_status",
                "constitution_compatibility", "dataset_version", "rubric_version",
                "application_version", "dataset_case_count", "case_count", "attempt_count",
                "threshold_percent", "semantic_score_percent", "schema_failure_count",
                "invariant_failure_count", "safety_failure_count", "model_failure_count",
                "safety_catalog_version", "failed_case_ids"
            ]},
            "model_provenance": model_prov(),
            "generation_config": gen_cfg(),
            "attempt_results": [attempt_result() for _ in range(45)],
            "failures": []
        }
        rv.validate(r)

def valid_report():
    return {
        "evaluation_status": "PASS",
        "system_acceptance_status": "PENDING_HUMAN_REVIEW",
        "resource_status": "PASS",
        "constitution_compatibility": "COMPATIBLE",
        "dataset_version": "1.0",
        "rubric_version": "1.0",
        "application_version": "1.0",
        "model_provenance": model_prov(),
        "generation_config": gen_cfg(),
        "dataset_case_count": 15,
        "case_count": 15,
        "attempt_count": 45,
        "threshold_percent": 85.0,
        "semantic_score_percent": 85.0,
        "schema_failure_count": 0,
        "invariant_failure_count": 0,
        "safety_failure_count": 0,
        "model_failure_count": 0,
        "safety_catalog_version": "SAFETY-1",
        "failed_case_ids": [],
        "attempt_results": [attempt_result() for _ in range(45)],
        "failures": []
    }

def model_prov():
    return {
        "provider": "ollama_local",
        "requested_model": "qwen2.5:1.5b",
        "actual_model": "qwen2.5",
        "model_digest": "abc",
        "license_id": "MIT",
        "license_source": "http://x",
        "runtime_version": "0.1",
        "endpoint": "http://127.0.0.1:11434"
    }

def gen_cfg():
    return {
        "temperature": 0.7,
        "seed_policy": "omitted",
        "context_tokens": 2048,
        "max_output_tokens": 512
    }

def attempt_result():
    return {
        "case_id": "abc",
        "attempt_number": 1,
        "model_provenance": model_prov(),
        "generation_config": gen_cfg(),
        "generation_status": "generated",
        "schema_valid": True,
        "invariant_failures": [],
        "safety_status": "passed",
        "safety_failure_reasons": [],
        "rubric_points": {
            "category": 2,
            "evidence": 2,
            "root_cause": 2,
            "suggested_actions": 2,
            "uncertainty": 2
        },
        "earned_points": 10,
        "failure_reasons": [],
        "sanitized_response_artifact": "responses/abc-attempt-1.json",
        "response_sha256": "aa" * 32
    }

class TestReportRequiredFieldsMissing:
    """Phase 1: Test missing-field rejection for all 22 required report fields."""
    
    def test_evaluation_status_missing(self):
        r = valid_report()
        del r["evaluation_status"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_system_acceptance_status_missing(self):
        r = valid_report()
        del r["system_acceptance_status"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_resource_status_missing(self):
        r = valid_report()
        del r["resource_status"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_constitution_compatibility_missing(self):
        r = valid_report()
        del r["constitution_compatibility"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_dataset_version_missing(self):
        r = valid_report()
        del r["dataset_version"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_rubric_version_missing(self):
        r = valid_report()
        del r["rubric_version"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_application_version_missing(self):
        r = valid_report()
        del r["application_version"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_model_provenance_missing(self):
        r = valid_report()
        del r["model_provenance"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_generation_config_missing(self):
        r = valid_report()
        del r["generation_config"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_dataset_case_count_missing(self):
        r = valid_report()
        del r["dataset_case_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_case_count_missing(self):
        r = valid_report()
        del r["case_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_attempt_count_missing(self):
        r = valid_report()
        del r["attempt_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_threshold_percent_missing(self):
        r = valid_report()
        del r["threshold_percent"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_semantic_score_percent_missing(self):
        r = valid_report()
        del r["semantic_score_percent"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_schema_failure_count_missing(self):
        r = valid_report()
        del r["schema_failure_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_invariant_failure_count_missing(self):
        r = valid_report()
        del r["invariant_failure_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_safety_failure_count_missing(self):
        r = valid_report()
        del r["safety_failure_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_model_failure_count_missing(self):
        r = valid_report()
        del r["model_failure_count"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_safety_catalog_version_missing(self):
        r = valid_report()
        del r["safety_catalog_version"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_failed_case_ids_missing(self):
        r = valid_report()
        del r["failed_case_ids"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_attempt_results_missing(self):
        r = valid_report()
        del r["attempt_results"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_failures_missing(self):
        r = valid_report()
        del r["failures"]
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportRequiredFieldsValidation:
    """Phase 1: Test valid values and bounds for required report fields."""
    
    def test_evaluation_status_all_enums(self):
        # PASS: minItems 45 for attempt_results already satisfied by valid_report()
        r = valid_report()
        r["evaluation_status"] = "PASS"
        rv.validate(r)
        
        # FAIL: requires minItems 1 for failures and system_acceptance_status != PENDING_HUMAN_REVIEW
        r = valid_report()
        r["evaluation_status"] = "FAIL"
        r["system_acceptance_status"] = "BLOCKED"
        r["failures"] = [{"case_id": "case-1", "gate_name": "schema", "reason_code": "FAIL_CODE"}]
        rv.validate(r)
        
        # PENDING_REPAIR: requires changing system_acceptance_status and adding repair_reference
        r = valid_report()
        r["evaluation_status"] = "PENDING_REPAIR"
        r["system_acceptance_status"] = "BLOCKED"
        r["repair_reference"] = "repairs/repair-001.json"
        rv.validate(r)

    def test_evaluation_status_invalid(self):
        r = valid_report()
        r["evaluation_status"] = "INVALID"
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_system_acceptance_status_enum(self):
        # Test that enum values are accepted (not testing conditionals in Phase 1)
        r = valid_report()
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        rv.validate(r)

    def test_resource_status_enum(self):
        # Test enum value with PASS state (default from valid_report)
        r = valid_report()
        r["resource_status"] = "PASS"
        rv.validate(r)

    def test_constitution_compatibility_enum(self):
        # Test enum value with COMPATIBLE state (default from valid_report)
        r = valid_report()
        r["constitution_compatibility"] = "COMPATIBLE"
        rv.validate(r)

    def test_string_version_fields_min_length(self):
        r = valid_report()
        r["dataset_version"] = ""
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_dataset_version_max_length(self):
        r = valid_report()
        r["dataset_version"] = "x" * 65
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_integer_counts_minimum_zero(self):
        for field in ["dataset_case_count", "case_count", "attempt_count",
                      "schema_failure_count", "invariant_failure_count",
                      "safety_failure_count", "model_failure_count"]:
            r = valid_report()
            r[field] = -1
            with pytest.raises(ValidationError):
                rv.validate(r)

    def test_percent_fields_range(self):
        r = valid_report()
        r["semantic_score_percent"] = 101
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_threshold_percent_minimum_80(self):
        r = valid_report()
        r["threshold_percent"] = 79.9
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_failed_case_ids_uniqueness(self):
        r = valid_report()
        r["failed_case_ids"] = ["a", "a"]
        with pytest.raises(ValidationError):
            rv.validate(r)

    def test_failed_case_ids_string_bounds(self):
        r = valid_report()
        r["failed_case_ids"] = [""]
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportEvaluationFail:
    """Phase 2 Group 1: Evaluation status=FAIL conditional - requires failures array minItems: 1."""
    
    def test_evaluation_fail_with_failures(self):
        r = valid_report()
        r["evaluation_status"] = "FAIL"
        r["system_acceptance_status"] = "BLOCKED"
        r["failures"] = [{"case_id": "case-1", "gate_name": "schema", "reason_code": "SCHEMA_FAIL"}]
        rv.validate(r)
    
    def test_evaluation_fail_without_failures_rejected(self):
        r = valid_report()
        r["evaluation_status"] = "FAIL"
        r["system_acceptance_status"] = "BLOCKED"
        r["failures"] = []
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportSystemAcceptanceStates:
    """Phase 2 Group 2: System acceptance state conditionals and constraints."""
    
    def test_pending_human_review_requires_pass_evaluation(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        rv.validate(r)
    
    def test_pending_human_review_rejects_fail_evaluation(self):
        r = valid_report()
        r["evaluation_status"] = "FAIL"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["failures"] = [{"case_id": "case-1", "gate_name": "schema", "reason_code": "FAIL"}]
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pending_human_review_requires_pass_resource(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        rv.validate(r)
    
    def test_pending_human_review_rejects_fail_resource(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["resource_status"] = "FAIL"
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pending_human_review_requires_compatible_constitution(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        rv.validate(r)
    
    def test_pending_human_review_rejects_pending_owner_review(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "PENDING_OWNER_REVIEW"
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pending_resource_verification_requires_not_measured_resource(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_RESOURCE_VERIFICATION"
        r["resource_status"] = "NOT_MEASURED"
        rv.validate(r)
    
    def test_pending_governance_allows_non_compatible_constitution(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_GOVERNANCE_DECISION"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "PENDING_OWNER_REVIEW"
        rv.validate(r)

class TestReportResourceConstitutionBindings:
    """Phase 2 Group 3: Resource status and constitution compatibility state bindings."""
    
    def test_resource_not_measured_allows_pass_evaluation(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_RESOURCE_VERIFICATION"
        r["resource_status"] = "NOT_MEASURED"
        rv.validate(r)
    
    def test_resource_fail_independent_of_evaluation(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "BLOCKED"
        r["resource_status"] = "FAIL"
        rv.validate(r)
    
    def test_constitution_pending_owner_review_allowed(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_GOVERNANCE_DECISION"
        r["constitution_compatibility"] = "PENDING_OWNER_REVIEW"
        rv.validate(r)
    
    def test_constitution_requires_redesign_allowed(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_GOVERNANCE_DECISION"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        rv.validate(r)
    
    def test_constitution_compatible_with_pending_human_review(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["constitution_compatibility"] = "COMPATIBLE"
        rv.validate(r)
    
    def test_resource_remediation_allowed_with_blocked_status(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "BLOCKED"
        r["resource_status"] = "REMEDIATION_REQUIRED"
        rv.validate(r)

class TestReportRepairAndRejection:
    """Phase 2 Group 4: PENDING_REPAIR status and human-review requirements."""
    
    def test_pending_repair_requires_repair_reference(self):
        r = valid_report()
        r["evaluation_status"] = "PENDING_REPAIR"
        r["system_acceptance_status"] = "BLOCKED"
        r["repair_reference"] = "repairs/repair-001.json"
        rv.validate(r)
    
    def test_pending_repair_rejects_missing_repair_reference(self):
        r = valid_report()
        r["evaluation_status"] = "PENDING_REPAIR"
        r["system_acceptance_status"] = "BLOCKED"
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pending_human_review_forbids_human_review_object(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportEvaluationPass:
    """Phase 2 Group 5: PASS evaluation status constraints."""
    
    def test_pass_valid_minimum_counts(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["dataset_case_count"] = 15
        r["case_count"] = 15
        r["attempt_count"] = 45
        rv.validate(r)
    
    def test_pass_rejects_dataset_case_count_below_15(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["dataset_case_count"] = 14
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_rejects_case_count_below_15(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["case_count"] = 14
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_rejects_attempt_count_below_45(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["attempt_count"] = 44
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_requires_zero_schema_failures(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["schema_failure_count"] = 1
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_requires_zero_invariant_failures(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["invariant_failure_count"] = 1
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_requires_zero_safety_failures(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["safety_failure_count"] = 1
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_requires_zero_model_failures(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["model_failure_count"] = 1
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportSemanticAndAttemptResults:
    """Phase 2 Group 6: Semantic score and attempt results constraints for PASS status."""
    
    def test_pass_requires_semantic_score_min_80(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["semantic_score_percent"] = 80.0
        rv.validate(r)
    
    def test_pass_rejects_semantic_score_below_80(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["semantic_score_percent"] = 79.9
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_pass_requires_45_attempt_results(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["attempt_results"] = [attempt_result() for _ in range(45)]
        rv.validate(r)
    
    def test_pass_rejects_attempt_results_below_45(self):
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["attempt_results"] = [attempt_result() for _ in range(44)]
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportHumanReviewDecisions:
    """Gap-closure Group 1: Human-review decision states and their system-acceptance consequences."""
    
    def test_human_review_rejected_forces_rejected_status(self):
        """allOf[8]: human_review.decision=REJECTED → system_acceptance_status=REJECTED."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "REJECTED"
        r["human_review"] = {
            "decision": "REJECTED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_REJECT_QUALITY"
        }
        rv.validate(r)
    
    def test_human_review_rejected_rejects_non_rejected_status(self):
        """allOf[8]: human_review.decision=REJECTED must have system_acceptance_status=REJECTED."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["human_review"] = {
            "decision": "REJECTED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_REJECT_QUALITY"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_rejected_status_requires_human_review(self):
        """allOf[9]: system_acceptance_status=REJECTED requires human_review."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "REJECTED"
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_rejected_status_requires_human_review_decision_rejected(self):
        """allOf[9]: system_acceptance_status=REJECTED requires human_review.decision=REJECTED."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "REJECTED"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_human_review_request_repair_forces_pending_repair_and_blocked(self):
        """allOf[10]: human_review.decision=REQUEST_REPAIR → evaluation=PENDING_REPAIR and system=BLOCKED."""
        r = valid_report()
        r["evaluation_status"] = "PENDING_REPAIR"
        r["system_acceptance_status"] = "BLOCKED"
        r["repair_reference"] = "repairs/repair-001.json"
        r["human_review"] = {
            "decision": "REQUEST_REPAIR",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_REQUEST_REPAIR"
        }
        rv.validate(r)
    
    def test_human_review_request_repair_rejects_non_pending_repair(self):
        """allOf[10]: human_review.decision=REQUEST_REPAIR must have evaluation_status=PENDING_REPAIR."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["human_review"] = {
            "decision": "REQUEST_REPAIR",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_REQUEST_REPAIR"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportAcceptedState:
    """Gap-closure Group 2a: system_acceptance_status=ACCEPTED comprehensive constraints."""
    
    def test_accepted_state_valid_all_conditions(self):
        """allOf[3]: ACCEPTED requires PASS evaluation, PASS resource, COMPATIBLE constitution, human_review APPROVED/REVIEW_COMPLETE_ACCEPT, and both evidence references."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        rv.validate(r)
    
    def test_accepted_rejects_non_pass_evaluation(self):
        """allOf[3]: ACCEPTED requires evaluation_status=PASS."""
        r = valid_report()
        r["evaluation_status"] = "FAIL"
        r["system_acceptance_status"] = "ACCEPTED"
        r["failures"] = [{"case_id": "case-1", "gate_name": "schema", "reason_code": "FAIL"}]
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_rejects_non_pass_resource_status(self):
        """allOf[3]: ACCEPTED requires resource_status=PASS."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "NOT_MEASURED"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_rejects_non_compatible_constitution(self):
        """allOf[3]: ACCEPTED requires constitution_compatibility=COMPATIBLE."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "PENDING_OWNER_REVIEW"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_rejects_non_approved_human_decision(self):
        """allOf[3]: ACCEPTED requires human_review.decision=APPROVED."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "REJECTED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_REJECT_QUALITY"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_rejects_wrong_human_decision_reason_code(self):
        """allOf[3]: ACCEPTED requires human_review.decision_reason_code=REVIEW_COMPLETE_ACCEPT."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_OTHER"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_requires_resource_evidence_reference(self):
        """allOf[3]: ACCEPTED requires resource_evidence_reference field."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_requires_constitution_evidence_reference(self):
        """allOf[3]: ACCEPTED requires constitution_compatibility_evidence_reference field."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_accepted_requires_human_review(self):
        """allOf[3]: ACCEPTED requires human_review object."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "COMPATIBLE"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        with pytest.raises(ValidationError):
            rv.validate(r)

class TestReportRequiresRedesignConstraints:
    """Gap-closure Group 2b: constitution_compatibility=REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT system-acceptance constraints."""
    
    def test_requires_redesign_allows_blocked_status(self):
        """allOf[13]: REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT allows system_acceptance_status=BLOCKED."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "BLOCKED"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        rv.validate(r)
    
    def test_requires_redesign_allows_pending_governance_decision_status(self):
        """allOf[13]: REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT allows system_acceptance_status=PENDING_GOVERNANCE_DECISION."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_GOVERNANCE_DECISION"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        rv.validate(r)
    
    def test_requires_redesign_rejects_pending_human_review_status(self):
        """allOf[13]: REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT forbids system_acceptance_status=PENDING_HUMAN_REVIEW."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_HUMAN_REVIEW"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_requires_redesign_rejects_accepted_status(self):
        """allOf[13]: REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT forbids system_acceptance_status=ACCEPTED."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "ACCEPTED"
        r["resource_status"] = "PASS"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        r["resource_evidence_reference"] = "evidence/resource-pass.md"
        r["constitution_compatibility_evidence_reference"] = "evidence/constitution-compatible.md"
        r["human_review"] = {
            "decision": "APPROVED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_COMPLETE_ACCEPT"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_requires_redesign_rejects_pending_resource_verification_status(self):
        """allOf[13]: REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT forbids system_acceptance_status=PENDING_RESOURCE_VERIFICATION."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "PENDING_RESOURCE_VERIFICATION"
        r["resource_status"] = "NOT_MEASURED"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        with pytest.raises(ValidationError):
            rv.validate(r)
    
    def test_requires_redesign_rejects_rejected_status(self):
        """allOf[13]: REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT forbids system_acceptance_status=REJECTED (enum constraint)."""
        r = valid_report()
        r["evaluation_status"] = "PASS"
        r["system_acceptance_status"] = "REJECTED"
        r["constitution_compatibility"] = "REQUIRES_REDESIGN_OR_FORMAL_AMENDMENT"
        r["human_review"] = {
            "decision": "REJECTED",
            "reviewer_role": "human_reviewer",
            "decision_reason_code": "REVIEW_REJECT_QUALITY"
        }
        with pytest.raises(ValidationError):
            rv.validate(r)
