"""Focused tests for the local Ollama inference client."""

import hashlib
import io
import json
import socket
from urllib.error import URLError
from unittest.mock import patch

import pytest

from opspilot.model_client import (
    ModelFailureCode,
    ModelGenerationError,
    OllamaClient,
)
from opspilot.versions import (
    GENERATION_CONTEXT_TOKENS,
    GENERATION_MAX_OUTPUT_TOKENS,
    GENERATION_TEMPERATURE,
    OLLAMA_ENDPOINT,
    OLLAMA_MODEL,
)

_MODEL_DIGEST = "a" * 64
_LOG = "Build failed: dependency example-lib was not found."
_VALID_RESPONSE = {
    "status": "ok",
    "category": "DEPENDENCY",
    "summary": "A dependency is missing.",
    "root_cause": "The build cannot find example-lib.",
    "evidence": ["dependency example-lib was not found"],
    "suggested_actions": ["Check the dependency declaration."],
    "confidence": 0.85,
    "needs_more_information": False,
}


def _ollama_json(payload: object) -> io.BytesIO:
    return io.BytesIO(json.dumps(payload).encode("utf-8"))


def _expected_calls(response: str = json.dumps(_VALID_RESPONSE)) -> list[io.BytesIO]:
    return [
        _ollama_json({"version": "0.5.0"}),
        _ollama_json(
            {
                "models": [
                    {"name": OLLAMA_MODEL, "digest": _MODEL_DIGEST}
                ]
            }
        ),
        _ollama_json(
            {
                "model": OLLAMA_MODEL,
                "response": response,
                "done": True,
            }
        ),
    ]


@patch("opspilot.model_client.urlopen")
def test_generate_uses_local_stochastic_model_and_preserves_provenance(
    mock_urlopen,
):
    mock_urlopen.side_effect = _expected_calls()

    result = OllamaClient(timeout_seconds=4.5).generate(_LOG)

    assert result.response == _VALID_RESPONSE
    assert result.response_sha256 == hashlib.sha256(
        json.dumps(_VALID_RESPONSE).encode("utf-8")
    ).hexdigest()
    assert result.provenance.provider == "ollama_local"
    assert result.provenance.requested_model == OLLAMA_MODEL
    assert result.provenance.actual_model == OLLAMA_MODEL
    assert result.provenance.model_digest == _MODEL_DIGEST
    assert result.provenance.runtime_version == "0.5.0"
    assert result.provenance.endpoint == OLLAMA_ENDPOINT
    assert result.provenance.temperature == GENERATION_TEMPERATURE == 0.7
    assert result.provenance.seed_policy == "omitted"
    assert result.provenance.context_tokens == GENERATION_CONTEXT_TOKENS
    assert result.provenance.max_output_tokens == GENERATION_MAX_OUTPUT_TOKENS

    requests = [call.args[0] for call in mock_urlopen.call_args_list]
    assert [request.get_method() for request in requests] == ["GET", "GET", "POST"]
    assert all(request.full_url.startswith("http://127.0.0.1:11434/") for request in requests)
    generation_payload = json.loads(requests[-1].data)
    assert generation_payload["model"] == OLLAMA_MODEL
    assert generation_payload["stream"] is False
    assert generation_payload["format"] == "json"
    assert _LOG in generation_payload["prompt"]
    assert generation_payload["options"]["temperature"] == 0.7
    assert generation_payload["options"]["num_ctx"] == GENERATION_CONTEXT_TOKENS
    assert generation_payload["options"]["num_predict"] == GENERATION_MAX_OUTPUT_TOKENS
    assert "seed" not in generation_payload["options"]
    assert all(call.kwargs["timeout"] == 4.5 for call in mock_urlopen.call_args_list)


@pytest.mark.parametrize(
    ("raw_response", "expected_code"),
    [
        ("not JSON", ModelFailureCode.MODEL_OUTPUT_INVALID),
        (
            '{"status":"ok","status":"analysis_error"}',
            ModelFailureCode.MODEL_OUTPUT_INVALID,
        ),
        (
            json.dumps({**_VALID_RESPONSE, "extra": "not allowed"}),
            ModelFailureCode.MODEL_OUTPUT_INVALID,
        ),
    ],
)
@patch("opspilot.model_client.urlopen")
def test_invalid_generated_response_is_a_structured_failure(
    mock_urlopen, raw_response, expected_code
):
    mock_urlopen.side_effect = _expected_calls(raw_response)

    with pytest.raises(ModelGenerationError) as raised:
        OllamaClient().generate(_LOG)

    failure = raised.value.failure
    assert failure.code is expected_code
    assert failure.response_sha256 == hashlib.sha256(
        raw_response.encode("utf-8")
    ).hexdigest()
    assert failure.provenance is not None
    assert _LOG not in str(failure.to_dict())


@patch("opspilot.model_client.urlopen")
def test_unavailable_ollama_raises_without_fallback(mock_urlopen):
    mock_urlopen.side_effect = URLError(ConnectionRefusedError())

    with pytest.raises(ModelGenerationError) as raised:
        OllamaClient().generate(_LOG)

    assert raised.value.failure.code is ModelFailureCode.MODEL_UNAVAILABLE
    assert raised.value.failure.to_dict()["retryable"] is True
    assert mock_urlopen.call_count == 1
    assert _LOG not in str(raised.value.failure.to_dict())


@patch("opspilot.model_client.urlopen")
def test_ollama_timeout_is_reported_as_retryable(mock_urlopen):
    mock_urlopen.side_effect = socket.timeout()

    with pytest.raises(ModelGenerationError) as raised:
        OllamaClient(timeout_seconds=0.25).generate(_LOG)

    assert raised.value.failure.code is ModelFailureCode.MODEL_TIMEOUT
    assert raised.value.failure.to_dict()["retryable"] is True
    assert mock_urlopen.call_args.kwargs["timeout"] == 0.25


@patch("opspilot.model_client.urlopen")
def test_missing_model_is_reported_without_attempting_a_pull(mock_urlopen):
    mock_urlopen.side_effect = [
        _ollama_json({"version": "0.5.0"}),
        _ollama_json({"models": []}),
    ]

    with pytest.raises(ModelGenerationError) as raised:
        OllamaClient().generate(_LOG)

    assert raised.value.failure.code is ModelFailureCode.MODEL_NOT_INSTALLED
    assert mock_urlopen.call_count == 2
    assert all(
        call.args[0].get_method() == "GET"
        for call in mock_urlopen.call_args_list
    )


@patch("opspilot.model_client.urlopen")
def test_request_payload_includes_schema_parameter(mock_urlopen):
    """Verify that the request payload includes the JSON schema for structured output."""
    mock_urlopen.side_effect = _expected_calls()

    OllamaClient().generate(_LOG)

    requests = [call.args[0] for call in mock_urlopen.call_args_list]
    generation_payload = json.loads(requests[-1].data)

    # Schema parameter must be present
    assert "schema" in generation_payload, "schema parameter not found in request"
    
    # Schema must be a dict with expected structure
    schema = generation_payload["schema"]
    assert isinstance(schema, dict), f"schema must be dict, got {type(schema)}"
    
    # Verify schema has required top-level fields
    assert "properties" in schema, "schema missing 'properties'"
    assert "required" in schema, "schema missing 'required'"
    
    # Verify all 8 required fields are listed
    required_fields = {"status", "category", "summary", "root_cause", 
                       "evidence", "suggested_actions", "confidence", "needs_more_information"}
    schema_required = set(schema["required"])
    assert schema_required == required_fields, f"schema required fields mismatch: {schema_required} != {required_fields}"
    
    # Verify field enums are present
    assert "enum" in schema["properties"]["status"], "status field missing enum"
    assert set(schema["properties"]["status"]["enum"]) == {"ok", "insufficient_information", "invalid_input", "analysis_error"}
    
    assert "enum" in schema["properties"]["category"], "category field missing enum"
    assert set(schema["properties"]["category"]["enum"]) == {"BUILD", "DEPENDENCY", "TEST", "CONFIGURATION", "SECURITY", "UNKNOWN"}
    
    assert "enum" in schema["properties"]["confidence"], "confidence field missing enum"
    assert set(schema["properties"]["confidence"]["enum"]) == {0, 0.3, 0.5, 0.65, 0.7, 0.85, 0.95}


@patch("opspilot.model_client.urlopen")
def test_prompt_includes_explicit_field_constraints(mock_urlopen):
    """Verify that the analysis prompt includes explicit field constraints and enum values."""
    mock_urlopen.side_effect = _expected_calls()

    OllamaClient().generate(_LOG)

    requests = [call.args[0] for call in mock_urlopen.call_args_list]
    generation_payload = json.loads(requests[-1].data)
    prompt = generation_payload["prompt"]

    # Verify prompt includes the log
    assert _LOG in prompt, "log text not found in prompt"
    
    # Verify prompt explicitly mentions required fields
    for field in ["status", "category", "summary", "root_cause", "evidence", 
                  "suggested_actions", "confidence", "needs_more_information"]:
        assert field in prompt, f"field '{field}' not explicitly mentioned in prompt"
    
    # Verify prompt includes exact enum values for status
    for status_value in ["ok", "insufficient_information", "invalid_input", "analysis_error"]:
        assert status_value in prompt, f"status enum value '{status_value}' not in prompt"
    
    # Verify prompt includes exact enum values for category
    for category_value in ["BUILD", "DEPENDENCY", "TEST", "CONFIGURATION", "SECURITY", "UNKNOWN"]:
        assert category_value in prompt, f"category enum value '{category_value}' not in prompt"
    
    # Verify prompt includes confidence values
    for confidence_value in [0, 0.3, 0.5, 0.65, 0.7, 0.85, 0.95]:
        assert str(confidence_value) in prompt, f"confidence value '{confidence_value}' not in prompt"
    
    # Verify prompt specifies needs_more_information is boolean
    assert "boolean" in prompt.lower(), "prompt should specify 'boolean' type for needs_more_information"


@patch("opspilot.model_client.urlopen")
def test_strict_validation_rejects_response_with_invalid_enum_values(mock_urlopen):
    """Verify that responses with invalid enum values are rejected after generation."""
    invalid_responses = [
        {"status": "Error", **{k: v for k, v in _VALID_RESPONSE.items() if k != "status"}},  # Invalid status
        {"category": "Compilation Error", **{k: v for k, v in _VALID_RESPONSE.items() if k != "category"}},  # Invalid category
    ]
    
    for invalid_response in invalid_responses:
        mock_urlopen.reset_mock()
        mock_urlopen.side_effect = _expected_calls(json.dumps(invalid_response))

        with pytest.raises(ModelGenerationError) as raised:
            OllamaClient().generate(_LOG)

        # Validation must catch the error (not silently repair)
        assert raised.value.failure.code is ModelFailureCode.MODEL_OUTPUT_INVALID
        assert raised.value.failure.response_sha256 is not None


@patch("opspilot.model_client.urlopen")
def test_strict_validation_rejects_wrong_confidence_type_and_range(mock_urlopen):
    """Verify that responses with invalid confidence (wrong type/range) are rejected."""
    invalid_confidence_responses = [
        {"confidence": 90, **{k: v for k, v in _VALID_RESPONSE.items() if k != "confidence"}},  # 0-100 range
        {"confidence": 0.9, **{k: v for k, v in _VALID_RESPONSE.items() if k != "confidence"}},  # Not in allowed enum
    ]
    
    for invalid_response in invalid_confidence_responses:
        mock_urlopen.reset_mock()
        mock_urlopen.side_effect = _expected_calls(json.dumps(invalid_response))

        with pytest.raises(ModelGenerationError) as raised:
            OllamaClient().generate(_LOG)

        # Must reject, not repair
        assert raised.value.failure.code is ModelFailureCode.MODEL_OUTPUT_INVALID


@patch("opspilot.model_client.urlopen")
def test_strict_validation_rejects_wrong_needs_more_information_type(mock_urlopen):
    """Verify that needs_more_information must be boolean, not array or string."""
    invalid_response = {
        "needs_more_information": ["Ensure config is set"],  # Array, not boolean
        **{k: v for k, v in _VALID_RESPONSE.items() if k != "needs_more_information"}
    }
    
    mock_urlopen.side_effect = _expected_calls(json.dumps(invalid_response))

    with pytest.raises(ModelGenerationError) as raised:
        OllamaClient().generate(_LOG)

    # Must reject, not repair
    assert raised.value.failure.code is ModelFailureCode.MODEL_OUTPUT_INVALID

