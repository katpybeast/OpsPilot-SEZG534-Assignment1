"""Integration tests for the evaluation runner with mocked model calls."""

import json
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from opspilot.evaluation.runner import EvaluationRunner, AttemptResult
from opspilot.model_client import GenerationResult, ModelFailure, ModelFailureCode, ModelProvenance


@pytest.fixture
def mock_ollama_client():
    """Create a mock Ollama client."""
    client = Mock()
    
    # Mock successful generation with a valid response
    valid_response = {
        "status": "ok",
        "category": "BUILD",
        "summary": "Build failed due to missing dependency",
        "root_cause": "Build system could not find required linker library",
        "evidence": ["Build error", "linker not found"],
        "suggested_actions": ["Install development headers", "Check build configuration"],
        "confidence": 0.85,
        "needs_more_information": False,
    }
    
    provenance = ModelProvenance(
        provider="ollama_local",
        requested_model="qwen2.5:1.5b",
        actual_model="qwen2.5:1.5b",
        model_digest="abc123",
        runtime_version="0.1.0",
        endpoint="http://127.0.0.1:11434",
        temperature=0.7,
        seed_policy="omitted",
        context_tokens=4096,
        max_output_tokens=768,
    )
    
    client.generate.return_value = GenerationResult(
        response=valid_response,
        response_sha256="abc123def456" * 5 + "ab",
        provenance=provenance,
    )
    
    return client


class TestEvaluationRunnerBasics:
    """Test basic runner initialization and dataset loading."""

    def test_runner_initialization(self):
        runner = EvaluationRunner(threshold_percent=80.0)
        assert runner.threshold_percent == 80.0

    def test_dataset_loading_valid(self):
        runner = EvaluationRunner()
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            assert "cases" in dataset
            assert isinstance(dataset["cases"], list)
            assert len(dataset["cases"]) >= 15

    def test_dataset_case_coverage(self):
        runner = EvaluationRunner()
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            cases = dataset.get("cases", [])
            
            # Check case count
            assert len(cases) >= 15
            
            # Check all case_ids are unique
            case_ids = [c["case_id"] for c in cases]
            assert len(case_ids) == len(set(case_ids))
            
            # Check categories are represented
            categories = set(c["primary_category"] for c in cases)
            assert len(categories) > 0

    def test_dataset_coverage_tags(self):
        runner = EvaluationRunner()
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            cases = dataset.get("cases", [])
            all_tags = set()
            for case in cases:
                all_tags.update(case.get("coverage_tags", []))
            
            # Verify all required tags are present
            required_tags = {
                "normal",
                "boundary",
                "ambiguous",
                "underspecified",
                "malformed",
                "missing_information",
                "adversarial",
            }
            assert required_tags.issubset(all_tags)

    def test_dataset_minimum_cases_per_category(self):
        runner = EvaluationRunner()
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            cases = dataset.get("cases", [])
            category_counts = {}
            for case in cases:
                primary = case.get("primary_category")
                category_counts[primary] = category_counts.get(primary, 0) + 1
            
            # Each category should have at least 2 cases
            for count in category_counts.values():
                assert count >= 2


class TestRunSingleAttempt:
    """Test single attempt execution and scoring."""

    def test_attempt_result_structure(self, mock_ollama_client):
        runner = EvaluationRunner()
        _, dataset = runner.load_and_validate_dataset()
        
        if dataset.get("cases"):
            case = dataset["cases"][0]
            
            with patch.object(runner, '_response_schema_validator') as mock_validator:
                mock_validator.validate.return_value = None  # No validation error
                
                result = runner._run_single_attempt(
                    mock_ollama_client,
                    case_id=case["case_id"],
                    attempt_num=1,
                    case_input=case["input"],
                    case_dict=case,
                )
                
                # Verify result structure
                assert isinstance(result, AttemptResult)
                assert result.case_id == case["case_id"]
                assert result.attempt_number == 1
                assert result.generation_status in ["generated", "model_unavailable", "timeout", "invalid_output"]
                assert isinstance(result.schema_valid, bool)
                assert isinstance(result.invariant_failures, list)
                assert isinstance(result.safety_status, str)
                assert isinstance(result.rubric_points_dict, dict)
                assert isinstance(result.earned_points, int)
                assert 0 <= result.earned_points <= 10

    def test_attempt_result_on_model_failure(self, mock_ollama_client):
        from opspilot.model_client import ModelGenerationError, ModelFailure, ModelFailureCode
        
        runner = EvaluationRunner()
        _, dataset = runner.load_and_validate_dataset()
        
        if dataset.get("cases"):
            case = dataset["cases"][0]
            
            # Mock a model failure with the correct exception type
            failure = ModelFailure(
                code=ModelFailureCode.MODEL_UNAVAILABLE,
                message="Model not available",
                retryable=True,
                response_sha256="0" * 64,
            )
            mock_ollama_client.generate.side_effect = ModelGenerationError(failure)
            
            with patch.object(runner, '_response_schema_validator') as mock_validator:
                mock_validator.validate.return_value = None
                
                # This should handle the exception gracefully
                result = runner._run_single_attempt(
                    mock_ollama_client,
                    case_id=case["case_id"],
                    attempt_num=1,
                    case_input=case["input"],
                    case_dict=case,
                )
                
                # Result should indicate failure
                assert result.generation_status in ["model_unavailable", "timeout", "invalid_output"]
                assert "GENERATION_FAILED" in result.failure_reasons


class TestEvaluationReport:
    """Test evaluation report structure and scoring."""

    def test_report_structure(self, mock_ollama_client):
        runner = EvaluationRunner(threshold_percent=80.0)
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            with patch('opspilot.evaluation.runner.OllamaClient') as mock_client_class:
                mock_client_class.return_value = mock_ollama_client
                
                with patch.object(runner, '_response_schema_validator') as mock_validator:
                    mock_validator.validate.return_value = None
                    
                    report = runner.run_evaluation(dataset)
                    
                    # Verify top-level report structure
                    assert "evaluation_status" in report
                    assert report["evaluation_status"] in ["PASS", "FAIL"]
                    assert "attempt_results" in report
                    assert isinstance(report["attempt_results"], list)
                    assert "failures" in report
                    assert isinstance(report["failures"], list)
                    assert "semantic_score_percent" in report
                    assert isinstance(report["semantic_score_percent"], (int, float))
                    assert "dataset_case_count" in report
                    assert report["dataset_case_count"] == len(dataset.get("cases", []))

    def test_attempt_results_per_case(self, mock_ollama_client):
        runner = EvaluationRunner(threshold_percent=80.0)
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            with patch('opspilot.evaluation.runner.OllamaClient') as mock_client_class:
                mock_client_class.return_value = mock_ollama_client
                
                with patch.object(runner, '_response_schema_validator') as mock_validator:
                    mock_validator.validate.return_value = None
                    
                    report = runner.run_evaluation(dataset)
                    
                    # 3 attempts per case
                    case_count = len(dataset.get("cases", []))
                    expected_attempt_count = 3 * case_count
                    
                    assert len(report["attempt_results"]) == expected_attempt_count

    def test_semantic_score_calculation(self, mock_ollama_client):
        runner = EvaluationRunner(threshold_percent=80.0)
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            with patch('opspilot.evaluation.runner.OllamaClient') as mock_client_class:
                mock_client_class.return_value = mock_ollama_client
                
                with patch.object(runner, '_response_schema_validator') as mock_validator:
                    mock_validator.validate.return_value = None
                    
                    report = runner.run_evaluation(dataset)
                    
                    # Score should be between 0 and 100
                    assert 0 <= report["semantic_score_percent"] <= 100

    def test_threshold_check(self, mock_ollama_client):
        runner = EvaluationRunner(threshold_percent=80.0)
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            with patch('opspilot.evaluation.runner.OllamaClient') as mock_client_class:
                mock_client_class.return_value = mock_ollama_client
                
                with patch.object(runner, '_response_schema_validator') as mock_validator:
                    mock_validator.validate.return_value = None
                    
                    report = runner.run_evaluation(dataset)
                    
                    # If semantic score is below threshold, evaluation should fail
                    if report["semantic_score_percent"] < 80.0:
                        assert report["evaluation_status"] == "FAIL"


class TestRunnerProvenance:
    """Test model provenance tracking."""

    def test_report_includes_provenance(self, mock_ollama_client):
        runner = EvaluationRunner()
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            with patch('opspilot.evaluation.runner.OllamaClient') as mock_client_class:
                mock_client_class.return_value = mock_ollama_client
                
                with patch.object(runner, '_response_schema_validator') as mock_validator:
                    mock_validator.validate.return_value = None
                    
                    report = runner.run_evaluation(dataset)
                    
                    # Verify provenance fields
                    assert "model_provenance" in report
                    provenance = report["model_provenance"]
                    assert provenance["provider"] == "ollama_local"
                    assert provenance["requested_model"] == "qwen2.5:1.5b"
                    assert provenance["endpoint"] == "http://127.0.0.1:11434"

    def test_report_includes_versions(self, mock_ollama_client):
        runner = EvaluationRunner()
        success, dataset = runner.load_and_validate_dataset()
        
        if success:
            with patch('opspilot.evaluation.runner.OllamaClient') as mock_client_class:
                mock_client_class.return_value = mock_ollama_client
                
                with patch.object(runner, '_response_schema_validator') as mock_validator:
                    mock_validator.validate.return_value = None
                    
                    report = runner.run_evaluation(dataset)
                    
                    # Verify version fields
                    assert "dataset_version" in report
                    assert "rubric_version" in report
                    assert "application_version" in report
                    assert "safety_catalog_version" in report
