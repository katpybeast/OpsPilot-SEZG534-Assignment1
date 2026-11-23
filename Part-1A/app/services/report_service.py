from __future__ import annotations

from app.models.finding import Finding
from app.models.report import Report
from app.models.validation_run import ValidationRun


def summarize_findings(findings: list[Finding]) -> str:
    if any(finding.status == "FAIL" for finding in findings):
        return "FAIL"
    if any(finding.status == "WARNING" for finding in findings):
        return "WARNING"
    return "PASS"


def build_report(validation_run: ValidationRun, findings: list[Finding]) -> Report:
    report = Report(
        validation_run=validation_run,
        findings=findings,
        summary_status=summarize_findings(findings),
    )
    validation_run.status = report.summary_status
    return report


def serialize_report(report: Report) -> dict:
    payload = report.to_dict()
    payload["summary_status"] = report.summary_status
    return payload
