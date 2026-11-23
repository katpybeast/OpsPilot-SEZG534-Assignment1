from app.schema.report_contract import validate_report


def test_report_contract_accepts_valid_payload():
    payload = {
        "validation_run": {
            "id": "run-123",
            "source_file_name": "demo.log",
            "source_type": "ci_log",
            "status": "FAIL",
        },
        "findings": [
            {
                "rule_id": "ci_cd_dependency_failure",
                "rule_family": "ci_cd",
                "severity": "FAIL",
                "status": "FAIL",
                "description": "Dependency resolution failed.",
                "evidence": "Error: failed to resolve dependency",
            }
        ],
        "summary_status": "FAIL",
    }
    validated = validate_report(payload)
    assert validated["summary_status"] == "FAIL"
