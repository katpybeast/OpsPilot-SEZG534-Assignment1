from __future__ import annotations

from datetime import datetime

from app.models.finding import Finding
from app.models.validation_run import ValidationRun
from app.rules.security_rules import evaluate_security_rules
from app.schema.report_contract import validate_report
from app.services.report_service import build_report
from app.validators.dockerfile_validator import validate_dockerfile_contents
from app.validators.input_validator import validate_uploaded_file
from app.validators.kubernetes_validator import validate_kubernetes_contents
from app.validators.log_validator import validate_log_contents


def validate_source(file_name: str, content: bytes | str, *, user_context: str = "") -> dict:
    source_type, payload = validate_uploaded_file(file_name, content)
    decoded = payload.decode("utf-8", errors="replace")

    if source_type == "ci_log":
        findings = validate_log_contents(decoded)
    elif source_type == "dockerfile":
        findings = validate_dockerfile_contents(decoded)
    elif source_type == "kubernetes_yaml":
        findings = validate_kubernetes_contents(decoded)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    findings.extend(evaluate_security_rules(decoded))
    deduped: list[Finding] = []
    seen: set[str] = set()
    for finding in findings:
        if finding.rule_id in seen:
            continue
        seen.add(finding.rule_id)
        deduped.append(finding)

    validation_run = ValidationRun(
        created_at=datetime.utcnow().isoformat(),
        source_file_name=file_name,
        source_type=source_type,
        file_size_bytes=len(payload),
        user_context=user_context,
    )
    report = build_report(validation_run, deduped)
    payload_report = report.to_dict()
    validate_report(payload_report)
    return payload_report
