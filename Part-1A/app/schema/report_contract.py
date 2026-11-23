from __future__ import annotations

from typing import Any


REQUIRED_FINDING_KEYS = {"rule_id", "rule_family", "severity", "status", "description", "evidence"}


def validate_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("Report must be a dictionary")
    findings = report.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")

    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValueError(f"Finding {index} is not a dictionary")
        missing = REQUIRED_FINDING_KEYS - set(finding)
        if missing:
            raise ValueError(f"Finding {index} missing required keys: {sorted(missing)}")
        rule_family = finding.get("rule_family")
        if rule_family not in {"ci_cd", "docker", "kubernetes", "security"}:
            raise ValueError(f"Finding {index} has invalid rule family: {rule_family!r}")
        severity = finding.get("severity")
        if severity not in {"INFO", "WARNING", "FAIL"}:
            raise ValueError(f"Finding {index} has invalid severity: {severity!r}")
        status = finding.get("status")
        if status not in {"PASS", "FAIL", "WARNING"}:
            raise ValueError(f"Finding {index} has invalid status: {status!r}")
    return report
