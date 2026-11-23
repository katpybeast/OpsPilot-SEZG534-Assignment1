from app.validators.log_validator import validate_log_contents


def test_ci_cd_log_dependency_failure_detected():
    sample = "npm ERR! code E404\nfailed to resolve dependency\nexit code 1"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_dependency_failure" for item in findings)


def test_ci_cd_log_test_failure_detected():
    sample = "pytest failed\nAssertionError: expected 2 got 3"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_test_failure" for item in findings)
