from app.services.validation_service import validate_source


def test_local_validation_for_supported_input():
    result = validate_source("sample.log", "failed to resolve dependency\n")
    assert result["summary_status"] == "FAIL"
    assert any(f["rule_id"] == "ci_cd_dependency_failure" for f in result["findings"])
