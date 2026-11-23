from __future__ import annotations

from datetime import datetime

from app.models.finding import Finding
from app.models.validation_run import ValidationRun
from app.rules.security_rules import evaluate_security_rules
from app.schema.report_contract import validate_report
from app.services.report_service import build_report
from app.storage.sqlite_repo import SqliteRepo
from app.validators.dockerfile_validator import validate_dockerfile_contents
from app.validators.input_validator import validate_uploaded_file
from app.validators.kubernetes_validator import validate_kubernetes_contents
from app.validators.log_validator import validate_log_contents


def validate_source(
    file_name: str,
    content: bytes | str,
    *,
    user_context: str = "",
    repo: SqliteRepo | None = None,
) -> dict:
    source_type, payload = validate_uploaded_file(file_name, content)
    decoded = payload.decode("utf-8", errors="replace")

    if source_type == "ci_log":
        findings = validate_log_contents(decoded)
    elif source_type == "dockerfile":
        findings = validate_dockerfile_contents(decoded)
    elif source_type == "kubernetes_yaml":
        findings = validate_kubernetes_contents(decoded)
        findings.extend(evaluate_security_rules(decoded))
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    deduped = _deduplicate_findings(findings)

    validation_run = ValidationRun(
        created_at=datetime.utcnow().isoformat(),
        source_file_name=file_name,
        source_type=source_type,
        file_size_bytes=len(payload),
        user_context=user_context,
    )
    report = build_report(validation_run, deduped)
    repo = repo or SqliteRepo()
    repo.save_report(report)
    payload_report = report.to_dict()
    validate_report(payload_report)
    return payload_report


def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    deduped: list[Finding] = []
    seen: dict[str, Finding] = {}

    for finding in findings:
        key = _canonical_finding_key(finding.rule_id)
        if key not in seen:
            seen[key] = finding
            deduped.append(finding)
            continue

        current = seen[key]
        if current.rule_family != "security" and finding.rule_family == "security":
            deduped[deduped.index(current)] = finding
            seen[key] = finding

    return deduped


def _canonical_finding_key(rule_id: str) -> str:
    if rule_id in {"k8s_privileged_container", "security_privileged_container"}:
        return "privileged_container"
    if rule_id in {"k8s_missing_resource_limits", "security_missing_resource_limits"}:
        return "missing_resource_limits"
    return rule_id
