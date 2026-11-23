from app.services.validation_service import validate_source


def test_offline_validation_is_deterministic_for_same_input():
    sample = "failed to resolve dependency\nexit code 1\n"
    first = validate_source("sample.log", sample)
    second = validate_source("sample.log", sample)

    def normalize(report):
        findings = []
        for finding in report["findings"]:
            findings.append(
                {
                    "rule_id": finding["rule_id"],
                    "rule_family": finding["rule_family"],
                    "severity": finding["severity"],
                    "status": finding["status"],
                    "description": finding["description"],
                    "evidence": finding["evidence"],
                    "location": finding["location"],
                }
            )
        findings.sort(key=lambda item: item["rule_id"])
        return {
            "summary_status": report["summary_status"],
            "source_file_name": report["validation_run"]["source_file_name"],
            "source_type": report["validation_run"]["source_type"],
            "findings": findings,
        }

    assert normalize(first) == normalize(second)
    assert first["summary_status"] == "FAIL"
