from __future__ import annotations

from app.models.finding import Finding


def evaluate_security_rules(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lowered = text.lower()

    if "privileged: true" in lowered or "privileged=true" in lowered or "--privileged" in lowered:
        findings.append(
            Finding(
                rule_id="security_privileged_container",
                rule_family="security",
                severity="FAIL",
                status="FAIL",
                description="A privileged container configuration was detected.",
                evidence="privileged=true or --privileged was present in the input.",
                location="security",
            )
        )

    if "cpu" not in lowered and "memory" not in lowered:
        findings.append(
            Finding(
                rule_id="security_missing_resource_limits",
                rule_family="security",
                severity="WARNING",
                status="WARNING",
                description="The configuration is missing explicit resource limits.",
                evidence="No CPU or memory limits were declared in the input.",
                location="security",
            )
        )

    return findings
