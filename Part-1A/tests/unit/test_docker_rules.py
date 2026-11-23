from app.validators.dockerfile_validator import validate_dockerfile_contents


def test_dockerfile_missing_from_detected():
    sample = "RUN apt-get update\nCMD [\"bash\"]\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_missing_from" for item in findings)


def test_dockerfile_unpinned_base_image_detected():
    sample = "FROM ubuntu\nCMD [\"bash\"]\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_unpinned_base_image" for item in findings)


def test_dockerfile_latest_tag_detected():
    sample = "FROM python:latest\nCMD [\"python\"]\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_unpinned_base_image" for item in findings)


def test_dockerfile_pinned_base_image_is_safe():
    sample = "FROM python:3.11-slim\nUSER app\nCMD [\"python\"]\n"
    findings = validate_dockerfile_contents(sample)
    assert not any(item.rule_id == "docker_unpinned_base_image" for item in findings)
    assert not any(item.rule_id == "docker_missing_from" for item in findings)


def test_dockerfile_root_user_detected():
    sample = "FROM ubuntu:22.04\nUSER root\nCMD [\"bash\"]\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_root_user" for item in findings)


def test_dockerfile_ssh_port_warning_detected():
    sample = "FROM ubuntu:22.04\nEXPOSE 22\n"
    findings = validate_dockerfile_contents(sample)
    assert any(item.rule_id == "docker_exposed_port_22" for item in findings)
