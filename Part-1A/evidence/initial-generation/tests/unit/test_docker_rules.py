from app.validators.dockerfile_validator import validate_dockerfile_contents


def test_dockerfile_root_user_detected():
    sample = "FROM ubuntu\nUSER root\nCMD [\"bash\"]\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_root_user" for item in findings)


def test_dockerfile_ssh_port_warning_detected():
    sample = "FROM ubuntu\nEXPOSE 22\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_exposed_port_22" for item in findings)
