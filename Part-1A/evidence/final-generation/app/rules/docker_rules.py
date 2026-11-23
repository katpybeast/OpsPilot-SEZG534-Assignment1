from __future__ import annotations

from app.models.finding import Finding


def evaluate_dockerfile_rules(docker_text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = docker_text.splitlines()
    upper = docker_text.upper()

    from_line = _extract_from_instruction(lines)
    if from_line is None:
        findings.append(
            Finding(
                rule_id="docker_missing_from",
                rule_family="docker",
                severity="FAIL",
                status="FAIL",
                description="The Dockerfile is missing a mandatory FROM instruction.",
                evidence="No FROM instruction was found in the Dockerfile.",
                location="dockerfile",
            )
        )
    else:
        image_name = _normalize_from_image(from_line)
        if image_name is None or _is_unpinned_base_image(image_name):
            findings.append(
                Finding(
                    rule_id="docker_unpinned_base_image",
                    rule_family="docker",
                    severity="WARNING",
                    status="WARNING",
                    description=(
                        "The FROM base image is unpinned and should specify an "
                        "explicit version or digest."
                    ),
                    evidence=from_line.strip(),
                    location="dockerfile",
                )
            )

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


def _extract_from_instruction(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.upper().startswith("FROM "):
            return stripped
    return None


def _normalize_from_image(from_line: str) -> str | None:
    tokens = from_line.split()
    if len(tokens) < 2:
        return None
    for token in tokens[1:]:
        if token.upper() == "AS":
            break
        if token.startswith("--"):
            continue
        return token
    return None


def _is_unpinned_base_image(image_name: str) -> bool:
    last_segment = image_name.rsplit("/", 1)[-1]
    if ":" not in last_segment:
        return True
    tag = last_segment.rsplit(":", 1)[1]
    return tag.lower() == "latest"
