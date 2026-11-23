import pytest

from app.storage.sqlite_repo import SqliteRepo
from app.limits import MAX_FILE_SIZE_BYTES
from app.validators.input_validator import validate_uploaded_file
from app.validators.log_validator import validate_log_contents
from app.services.validation_service import validate_source


def test_ci_cd_log_dependency_failure_detected():
    sample = "npm ERR! code E404\nfailed to resolve dependency\nexit code 1"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_dependency_failure" for item in findings)


def test_ci_cd_log_dependency_version_requirement_failure_detected():
    sample = "ERROR: Could not find a version that satisfies the requirement requests==2.31.0"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_dependency_failure" for item in findings)


def test_ci_cd_log_dependency_no_matching_distribution_detected():
    sample = "ERROR: No matching distribution found for pyyaml==999"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_dependency_failure" for item in findings)


def test_ci_cd_log_common_dependency_install_failure_detected():
    sample = "pip install failed: dependency installation failed for requirements.txt"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_dependency_failure" for item in findings)


def test_ci_cd_log_test_failure_detected():
    sample = "pytest failed\nAssertionError: expected 2 got 3"
    findings = validate_log_contents(sample)
    assert any(item.rule_id == "ci_cd_test_failure" for item in findings)


def test_txt_files_are_rejected():
    try:
        validate_uploaded_file("notes.txt", "plain text")
        raise AssertionError("Expected ValueError for .txt uploads")
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)


def test_log_files_are_accepted():
    source_type, payload = validate_uploaded_file("build.log", "pytest failed\n")
    assert source_type == "ci_log"
    assert payload == b"pytest failed\n"


def test_file_at_maximum_size_is_accepted():
    payload = b"x" * MAX_FILE_SIZE_BYTES

    source_type, accepted_payload = validate_uploaded_file("boundary.log", payload)

    assert source_type == "ci_log"
    assert len(accepted_payload) == 1_048_576


def test_file_over_maximum_size_is_rejected():
    payload = b"x" * (MAX_FILE_SIZE_BYTES + 1)

    with pytest.raises(ValueError, match="1 MiB limit"):
        validate_uploaded_file("oversized.log", payload)


def test_validate_source_saves_report_to_history(tmp_path):
    repo = SqliteRepo(tmp_path / "history.db")
    validate_source("first.log", "pytest failed\n", repo=repo)
    validate_source("second.log", "pip install failed\n", repo=repo)

    history = repo.get_history()
    assert len(history) == 2
    assert [item["source_file_name"] for item in history] == ["second.log", "first.log"]
    assert history[0]["summary_status"] in {"FAIL", "WARNING"}
