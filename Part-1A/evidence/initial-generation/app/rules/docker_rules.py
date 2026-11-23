from __future__ import annotations

from app.models.finding import Finding


def evaluate_dockerfile_rules(docker_text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = docker_text.splitlines()
    upper = docker_text.upper()

    for index, line in enumerate(lines, start=1):
        if "USER ROOT" in line.upper():
            findings.append(
                Finding(
                    rule_id="docker_root_user",
                    rule_family="docker",
                    severity="FAIL",
                    status="FAIL",
                    description="The Dockerfile runs as root, which increases container risk.",
                    evidence=line.strip(),
                    location=f"line {index}",
                )
            )
            break

    for index, line in enumerate(lines, start=1):
        if "EXPOSE 22" in line.upper():
            findings.append(
                Finding(
                    rule_id="docker_exposed_port_22",
                    rule_family="docker",
                    severity="WARNING",
                    status="WARNING",
                    description="A privileged SSH port is exposed in the container image.",
                    evidence=line.strip(),
                    location=f"line {index}",
                )
            )
            break

    if "USER " not in docker_text and "USER root" not in upper:
        findings.append(
            Finding(
                rule_id="docker_missing_security_user",
                rule_family="docker",
                severity="WARNING",
                status="WARNING",
                description="The Dockerfile does not define a non-root user.",
                evidence="Dockerfile has no USER instruction.",
                location="dockerfile",
            )
        )

    return findings
