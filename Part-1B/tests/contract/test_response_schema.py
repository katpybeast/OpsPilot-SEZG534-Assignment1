"""Contract tests for explanation-response.schema.json"""
import json
import pytest
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_PATH = Path(__file__).parent.parent.parent / "specs" / "001-explain-ci-logs" / "contracts" / "explanation-response.schema.json"


@pytest.fixture
def schema():
    """Load the explanation response schema."""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture
def validator(schema):
    """Create a Draft 2020-12 validator."""
    return Draft202012Validator(schema)


class TestRequiredKeys:
    """Test that all eight required keys are enforced."""

    def test_all_eight_keys_required(self, validator):
        """Missing any required key should fail validation."""
        required_keys = ["status", "category", "summary", "root_cause", 
                        "evidence", "suggested_actions", "confidence", 
                        "needs_more_information"]
        for missing_key in required_keys:
            response = {k: v for k, v in {
                "status": "ok",
                "category": "BUILD",
                "summary": "test",
                "root_cause": "test",
                "evidence": ["test"],
                "suggested_actions": ["test"],
                "confidence": 0.7,
                "needs_more_information": False
            }.items() if k != missing_key}
            assert not validator.is_valid(response), f"Should fail without {missing_key}"

    def test_valid_minimal_ok_response(self, validator):
        """Valid ok status response with minimal content."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "Build failed",
            "root_cause": "Missing dependency",
            "evidence": ["error message"],
            "suggested_actions": ["install dependency"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)


class TestStatusEnum:
    """Test status field enum constraint."""

    @pytest.mark.parametrize("status", ["ok", "insufficient_information", "invalid_input", "analysis_error"])
    def test_valid_statuses(self, validator, status):
        if status == "ok":
            confidence = 0.7
            evidence = ["test evidence"]
            suggested_actions = ["test action"]
            needs_more_info = False
        elif status == "insufficient_information":
            confidence = 0.5
            evidence = []
            suggested_actions = ["test action"]
            needs_more_info = True
        else:  # invalid_input or analysis_error
            confidence = 0
            evidence = []
            suggested_actions = []
            needs_more_info = True
        
        response = {
            "status": status,
            "category": "UNKNOWN" if status in ["invalid_input", "analysis_error"] else "BUILD",
            "summary": "valid summary" if status not in ["invalid_input", "analysis_error"] else "s",
            "root_cause": "valid root cause" if status not in ["invalid_input", "analysis_error"] else "r",
            "evidence": evidence,
            "suggested_actions": suggested_actions,
            "confidence": confidence,
            "needs_more_information": needs_more_info
        }
        assert validator.is_valid(response), f"Status '{status}' should be valid"

    def test_invalid_status(self, validator):
        response = {
            "status": "unknown_status",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)


class TestCategoryEnum:
    """Test category field enum constraint."""

    @pytest.mark.parametrize("category", ["BUILD", "DEPENDENCY", "TEST", "CONFIGURATION", "SECURITY", "UNKNOWN"])
    def test_valid_categories(self, validator, category):
        response = {
            "status": "ok",
            "category": category,
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response), f"Category '{category}' should be valid"

    def test_invalid_category(self, validator):
        response = {
            "status": "ok",
            "category": "INVALID",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)


class TestStringLengthConstraints:
    """Test string length constraints."""

    def test_summary_minlength_1(self, validator):
        """Summary must have minLength 1."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_summary_maxlength_240(self, validator):
        """Summary must have maxLength 240."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "x" * 241,
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_summary_at_maxlength_240(self, validator):
        """Summary at exactly maxLength 240 should be valid."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "x" * 240,
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)

    def test_root_cause_minlength_1(self, validator):
        """Root cause must have minLength 1."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_root_cause_maxlength_1000(self, validator):
        """Root cause must have maxLength 1000."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "x" * 1001,
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_root_cause_at_maxlength_1000(self, validator):
        """Root cause at exactly maxLength 1000 should be valid."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "x" * 1000,
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)


class TestArrayBounds:
    """Test array bounds and minItems/maxItems constraints."""

    def test_evidence_minItems_0(self, validator):
        """Evidence can have minItems 0 for certain statuses."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response), "ok status requires minItems 1 for evidence"

    def test_evidence_minItems_1_for_ok(self, validator):
        """Evidence requires minItems 1 when status is ok."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)

    def test_evidence_maxItems_10(self, validator):
        """Evidence must have maxItems 10."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [f"item{i}" for i in range(11)],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_evidence_at_maxItems_10(self, validator):
        """Evidence at exactly maxItems 10 should be valid."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [f"item{i}" for i in range(10)],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)

    def test_suggested_actions_minItems_1_for_ok(self, validator):
        """Suggested actions requires minItems 1 when status is ok."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": [],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_suggested_actions_maxItems_5(self, validator):
        """Suggested actions must have maxItems 5."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": [f"action{i}" for i in range(6)],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)


class TestConfidenceEnum:
    """Test confidence field enum constraint."""

    @pytest.mark.parametrize("confidence", [0, 0.3, 0.5, 0.65, 0.7, 0.85, 0.95])
    def test_valid_confidence_values(self, validator, confidence):
        if confidence == 0:
            status = "invalid_input"
            evidence = []
            suggested_actions = []
            needs_more_info = True
            category = "UNKNOWN"
            summary = "s"
            root_cause = "r"
        elif confidence in [0.3, 0.5, 0.65]:
            status = "insufficient_information"
            evidence = []
            suggested_actions = ["test"]
            needs_more_info = True
            category = "BUILD"
            summary = "test"
            root_cause = "test"
        else:  # 0.7, 0.85, 0.95
            status = "ok"
            evidence = ["test"]
            suggested_actions = ["test"]
            needs_more_info = False
            category = "BUILD"
            summary = "test"
            root_cause = "test"
        
        response = {
            "status": status,
            "category": category,
            "summary": summary,
            "root_cause": root_cause,
            "evidence": evidence,
            "suggested_actions": suggested_actions,
            "confidence": confidence,
            "needs_more_information": needs_more_info
        }
        assert validator.is_valid(response), f"Confidence {confidence} should be valid"

    def test_invalid_confidence(self, validator):
        """Invalid confidence value should fail."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.5,
            "needs_more_information": False
        }
        assert not validator.is_valid(response), "0.5 confidence not valid for ok status"


class TestAdditionalProperties:
    """Test additionalProperties: false constraint."""

    def test_no_additional_properties(self, validator):
        """Additional properties should be rejected."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False,
            "extra_field": "should fail"
        }
        assert not validator.is_valid(response)


class TestStatusOkRules:
    """Test status=ok specific conditional rules."""

    def test_ok_requires_confidence_0_7_0_85_0_95(self, validator):
        """When status=ok, confidence must be 0.7, 0.85, or 0.95."""
        for conf in [0, 0.3, 0.5, 0.65]:
            response = {
                "status": "ok",
                "category": "BUILD",
                "summary": "test",
                "root_cause": "test",
                "evidence": ["test"],
                "suggested_actions": ["test"],
                "confidence": conf,
                "needs_more_information": False
            }
            assert not validator.is_valid(response), f"ok status should not allow confidence {conf}"

    def test_ok_requires_evidence_minItems_1(self, validator):
        """When status=ok, evidence must have minItems 1."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_ok_requires_suggested_actions_minItems_1(self, validator):
        """When status=ok, suggested_actions must have minItems 1."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": [],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_ok_requires_needs_more_information_false(self, validator):
        """When status=ok, needs_more_information must be false."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": True
        }
        assert not validator.is_valid(response)


class TestStatusInsufficientInformationRules:
    """Test status=insufficient_information specific conditional rules."""

    def test_insufficient_information_confidence_values(self, validator):
        """When status=insufficient_information, confidence must be 0.3, 0.5, or 0.65."""
        for conf in [0, 0.7, 0.85, 0.95]:
            response = {
                "status": "insufficient_information",
                "category": "BUILD",
                "summary": "test",
                "root_cause": "test",
                "evidence": [],
                "suggested_actions": ["test"],
                "confidence": conf,
                "needs_more_information": True
            }
            assert not validator.is_valid(response), f"insufficient_information should not allow confidence {conf}"

    def test_insufficient_information_requires_suggested_actions_minItems_1(self, validator):
        """When status=insufficient_information, suggested_actions must have minItems 1."""
        response = {
            "status": "insufficient_information",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0.5,
            "needs_more_information": True
        }
        assert not validator.is_valid(response)

    def test_insufficient_information_requires_needs_more_information_true(self, validator):
        """When status=insufficient_information, needs_more_information must be true."""
        response = {
            "status": "insufficient_information",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [],
            "suggested_actions": ["test"],
            "confidence": 0.5,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)


class TestStatusErrorRules:
    """Test status=invalid_input and status=analysis_error specific conditional rules."""

    @pytest.mark.parametrize("status", ["invalid_input", "analysis_error"])
    def test_error_status_requires_category_unknown(self, validator, status):
        """When status=invalid_input or analysis_error, category must be UNKNOWN."""
        response = {
            "status": status,
            "category": "BUILD",
            "summary": "",
            "root_cause": "",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0,
            "needs_more_information": True
        }
        assert not validator.is_valid(response)

    @pytest.mark.parametrize("status", ["invalid_input", "analysis_error"])
    def test_error_status_evidence_maxItems_0(self, validator, status):
        """When status=invalid_input or analysis_error, evidence must have maxItems 0."""
        response = {
            "status": status,
            "category": "UNKNOWN",
            "summary": "",
            "root_cause": "",
            "evidence": ["test"],
            "suggested_actions": [],
            "confidence": 0,
            "needs_more_information": True
        }
        assert not validator.is_valid(response)

    @pytest.mark.parametrize("status", ["invalid_input", "analysis_error"])
    def test_error_status_suggested_actions_maxItems_0(self, validator, status):
        """When status=invalid_input or analysis_error, suggested_actions must have maxItems 0."""
        response = {
            "status": status,
            "category": "UNKNOWN",
            "summary": "",
            "root_cause": "",
            "evidence": [],
            "suggested_actions": ["test"],
            "confidence": 0,
            "needs_more_information": True
        }
        assert not validator.is_valid(response)

    @pytest.mark.parametrize("status", ["invalid_input", "analysis_error"])
    def test_error_status_confidence_0(self, validator, status):
        """When status=invalid_input or analysis_error, confidence must be 0."""
        response = {
            "status": status,
            "category": "UNKNOWN",
            "summary": "",
            "root_cause": "",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0.5,
            "needs_more_information": True
        }
        assert not validator.is_valid(response)

    @pytest.mark.parametrize("status", ["invalid_input", "analysis_error"])
    def test_error_status_needs_more_information_true(self, validator, status):
        """When status=invalid_input or analysis_error, needs_more_information must be true."""
        response = {
            "status": status,
            "category": "UNKNOWN",
            "summary": "",
            "root_cause": "",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    @pytest.mark.parametrize("status", ["invalid_input", "analysis_error"])
    def test_valid_error_response(self, validator, status):
        """Valid error response with all required fields."""
        response = {
            "status": status,
            "category": "UNKNOWN",
            "summary": "error",
            "root_cause": "error",
            "evidence": [],
            "suggested_actions": [],
            "confidence": 0,
            "needs_more_information": True
        }
        assert validator.is_valid(response)


class TestEvidenceItemConstraints:
    """Test individual evidence array item constraints."""

    def test_evidence_item_minlength_1(self, validator):
        """Evidence array items must have minLength 1."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": [""],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_evidence_item_maxlength_500(self, validator):
        """Evidence array items must have maxLength 500."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["x" * 501],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_evidence_item_at_maxlength_500(self, validator):
        """Evidence array item at exactly maxLength 500 should be valid."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["x" * 500],
            "suggested_actions": ["test"],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)


class TestSuggestedActionsItemConstraints:
    """Test individual suggested_actions array item constraints."""

    def test_suggested_actions_item_minlength_1(self, validator):
        """Suggested actions array items must have minLength 1."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": [""],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_suggested_actions_item_maxlength_240(self, validator):
        """Suggested actions array items must have maxLength 240."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["x" * 241],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert not validator.is_valid(response)

    def test_suggested_actions_item_at_maxlength_240(self, validator):
        """Suggested actions array item at exactly maxLength 240 should be valid."""
        response = {
            "status": "ok",
            "category": "BUILD",
            "summary": "test",
            "root_cause": "test",
            "evidence": ["test"],
            "suggested_actions": ["x" * 240],
            "confidence": 0.7,
            "needs_more_information": False
        }
        assert validator.is_valid(response)
