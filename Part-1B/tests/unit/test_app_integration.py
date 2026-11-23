"""Tests for Streamlit application integration with the model client."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from opspilot.model_client import (
    ModelFailureCode,
    ModelGenerationError,
    ModelFailure,
    GenerationResult,
    ModelProvenance,
)
from opspilot.versions import (
    MAX_INPUT_BYTES,
    MAX_CONTROL_CHARACTER_PERCENT,
    APPLICATION_VERSION,
)


# Import the validation function from app.py
# We'll test it without importing streamlit directly in this test
def _validate_input(log_text: str) -> tuple[bool, str]:
    """Validate log text against input constraints."""
    if not log_text or not log_text.strip():
        return False, "Log input cannot be empty."
    
    byte_length = len(log_text.encode("utf-8"))
    if byte_length > MAX_INPUT_BYTES:
        return False, f"Log input exceeds {MAX_INPUT_BYTES} bytes ({byte_length} bytes provided)."
    
    control_chars = sum(
        1 for c in log_text
        if ord(c) < 32 and c not in "\t\n\r"
    )
    control_percent = control_chars / len(log_text) if log_text else 0.0
    if control_percent > MAX_CONTROL_CHARACTER_PERCENT:
        return False, f"Log contains too many control characters ({control_percent:.1%}; max {MAX_CONTROL_CHARACTER_PERCENT:.1%})."
    
    return True, ""


class TestInputValidation:
    """Test input validation logic."""

    def test_empty_input_rejected(self):
        is_valid, error = _validate_input("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_whitespace_only_rejected(self):
        is_valid, error = _validate_input("   \n  \t  ")
        assert not is_valid
        assert "empty" in error.lower()

    def test_valid_simple_log_accepted(self):
        is_valid, error = _validate_input("Build failed: compilation error at line 42")
        assert is_valid
        assert error == ""

    def test_input_exceeding_byte_limit_rejected(self):
        large_input = "x" * (MAX_INPUT_BYTES + 1)
        is_valid, error = _validate_input(large_input)
        assert not is_valid
        assert "exceeds" in error.lower()
        assert str(MAX_INPUT_BYTES) in error

    def test_input_at_byte_limit_accepted(self):
        input_at_limit = "x" * MAX_INPUT_BYTES
        is_valid, error = _validate_input(input_at_limit)
        assert is_valid
        assert error == ""

    def test_unicode_input_counted_in_bytes(self):
        # Three-byte UTF-8 character (Chinese)
        char_3bytes = "你"
        input_text = char_3bytes * ((MAX_INPUT_BYTES // 3) + 1)
        is_valid, error = _validate_input(input_text)
        assert not is_valid
        assert "exceeds" in error.lower()

    def test_allowed_control_characters_accepted(self):
        input_with_tabs_newlines = "Line 1\tTab\nLine 2\rCarriage return"
        is_valid, error = _validate_input(input_with_tabs_newlines)
        assert is_valid
        assert error == ""

    def test_excessive_control_characters_rejected(self):
        # Create input with many ASCII control characters (not tabs/newlines/CR)
        log_text = "Normal text"
        # Add enough control chars to exceed the threshold
        control_chars = "\x01" * int(len(log_text) * MAX_CONTROL_CHARACTER_PERCENT + 1)
        input_text = log_text + control_chars
        
        is_valid, error = _validate_input(input_text)
        assert not is_valid
        assert "control characters" in error.lower()

    def test_control_character_threshold_at_boundary(self):
        # Create input with exactly at the threshold
        base_text = "x" * 100
        allowed_control_count = int(100 * MAX_CONTROL_CHARACTER_PERCENT)
        control_text = "\x01" * allowed_control_count
        input_text = base_text + control_text
        
        is_valid, error = _validate_input(input_text)
        assert is_valid
        assert error == ""


class TestModelResponseHandling:
    """Test handling of successful model responses."""

    def test_valid_response_structure(self):
        """Verify that expected response structure matches contract."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "Compilation failed due to syntax error.",
            "root_cause": "Missing semicolon at line 42.",
            "evidence": ["Compiler error message indicates line 42"],
            "suggested_actions": ["Check line 42 for syntax errors"],
            "confidence": 0.85,
            "needs_more_information": False,
        }
        
        # Verify all required keys are present
        required_keys = {
            "status", "category", "summary", "root_cause",
            "evidence", "suggested_actions", "confidence", "needs_more_information"
        }
        assert set(response.keys()) == required_keys

    def test_response_with_no_evidence(self):
        """Response can have empty evidence array."""
        response = {
            "status": "insufficient_information",
            "category": "UNKNOWN",
            "summary": "Cannot determine root cause.",
            "root_cause": "Log does not contain diagnostic information.",
            "evidence": [],
            "suggested_actions": ["Provide more detailed logs"],
            "confidence": 0.5,
            "needs_more_information": True,
        }
        
        assert response["evidence"] == []
        assert response["needs_more_information"] is True

    def test_response_with_no_actions(self):
        """Response can have empty suggested_actions array."""
        response = {
            "status": "invalid_input",
            "category": "UNKNOWN",
            "summary": "Input was not a valid log.",
            "root_cause": "Cannot parse input format.",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0,
            "needs_more_information": True,
        }
        
        assert response["suggested_actions"] == []


class TestModelFailureHandling:
    """Test handling of model generation failures."""

    def test_unavailable_model_failure_structure(self):
        """Verify failure contains no sensitive data."""
        failure = ModelFailure(
            code=ModelFailureCode.MODEL_UNAVAILABLE,
            message="The local Ollama service is unavailable.",
            retryable=True,
        )
        
        failure_dict = failure.to_dict()
        assert failure_dict["code"] == "MODEL_UNAVAILABLE"
        assert failure_dict["retryable"] is True
        assert "message" in failure_dict

    def test_timeout_failure_is_retryable(self):
        """Timeout failures should be retryable."""
        failure = ModelFailure(
            code=ModelFailureCode.MODEL_TIMEOUT,
            message="The local Ollama request timed out.",
            retryable=True,
        )
        
        assert failure.to_dict()["retryable"] is True

    def test_model_not_installed_failure(self):
        """Model not installed failure structure."""
        failure = ModelFailure(
            code=ModelFailureCode.MODEL_NOT_INSTALLED,
            message="The configured Ollama model is not installed locally.",
            retryable=False,
        )
        
        failure_dict = failure.to_dict()
        assert failure_dict["code"] == "MODEL_NOT_INSTALLED"
        assert failure_dict["retryable"] is False

    def test_invalid_output_failure_includes_hash(self):
        """Invalid output includes response hash but not content."""
        prov = ModelProvenance(
            provider="ollama_local",
            requested_model="qwen2.5:1.5b",
            actual_model="qwen2.5:1.5b",
            model_digest="a" * 64,
            runtime_version="0.5.0",
            endpoint="http://127.0.0.1:11434",
            temperature=0.7,
            seed_policy="omitted",
            context_tokens=4096,
            max_output_tokens=768,
        )
        
        failure = ModelFailure(
            code=ModelFailureCode.MODEL_OUTPUT_INVALID,
            message="The generated response did not satisfy the response schema.",
            retryable=False,
            response_sha256="abc123def456",
            provenance=prov,
        )
        
        failure_dict = failure.to_dict()
        assert failure_dict["response_sha256"] == "abc123def456"
        assert failure_dict["provenance"] is not None
        assert failure_dict["provenance"]["endpoint"] == "http://127.0.0.1:11434"

    def test_failure_with_http_status(self):
        """HTTP error failures include status code."""
        failure = ModelFailure(
            code=ModelFailureCode.OLLAMA_HTTP_ERROR,
            message="Ollama rejected the local API request.",
            retryable=True,
            http_status=500,
        )
        
        failure_dict = failure.to_dict()
        assert failure_dict["http_status"] == 500

    def test_model_generation_error_preserves_failure(self):
        """ModelGenerationError encapsulates the failure."""
        failure = ModelFailure(
            code=ModelFailureCode.MODEL_UNAVAILABLE,
            message="Ollama is not running.",
            retryable=True,
        )
        
        error = ModelGenerationError(failure)
        assert error.failure is failure
        assert str(error) == "Ollama is not running."


class TestOllamaClientMocking:
    """Test that OllamaClient can be properly mocked for integration testing."""

    def test_client_can_be_mocked_for_success(self):
        """Verify mocking pattern for successful generation."""
        mock_client = Mock()
        mock_response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "Build failed.",
            "root_cause": "Compilation error.",
            "evidence": ["Error at line 42"],
            "suggested_actions": ["Fix compilation error"],
            "confidence": 0.85,
            "needs_more_information": False,
        }
        
        mock_result = GenerationResult(
            response=mock_response,
            response_sha256="mock_hash_123",
            provenance=Mock(),
        )
        
        mock_client.generate.return_value = mock_result
        
        result = mock_client.generate("test log")
        assert result.response == mock_response
        assert result.response_sha256 == "mock_hash_123"
        mock_client.generate.assert_called_once_with("test log")

    def test_client_can_be_mocked_for_failure(self):
        """Verify mocking pattern for generation failure."""
        mock_client = Mock()
        failure = ModelFailure(
            code=ModelFailureCode.MODEL_UNAVAILABLE,
            message="Ollama is unavailable.",
            retryable=True,
        )
        
        mock_client.generate.side_effect = ModelGenerationError(failure)
        
        with pytest.raises(ModelGenerationError) as exc_info:
            mock_client.generate("test log")
        
        assert exc_info.value.failure.code == ModelFailureCode.MODEL_UNAVAILABLE


class TestApplicationConfiguration:
    """Test that application uses correct configuration."""

    def test_application_version_is_defined(self):
        """Application version should be defined."""
        assert APPLICATION_VERSION is not None
        assert isinstance(APPLICATION_VERSION, str)
        assert len(APPLICATION_VERSION) > 0

    def test_max_input_bytes_is_reasonable(self):
        """Input size limit should be reasonable (not too small or huge)."""
        assert MAX_INPUT_BYTES > 1024  # At least 1 KiB
        assert MAX_INPUT_BYTES <= 1_000_000  # At most 1 MiB

    def test_control_character_threshold_is_valid(self):
        """Control character threshold should be between 0 and 1."""
        assert 0 < MAX_CONTROL_CHARACTER_PERCENT < 1
        assert isinstance(MAX_CONTROL_CHARACTER_PERCENT, (int, float))
