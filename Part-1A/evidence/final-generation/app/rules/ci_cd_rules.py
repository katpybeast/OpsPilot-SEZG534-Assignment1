from __future__ import annotations

from app.models.finding import Finding


def evaluate_ci_cd_rules(log_text: str) -> list[Finding]:
    findings: list[Finding] = []
    lowered = log_text.lower()

    dependency_match = (
        "failed to resolve" in lowered
        or "could not resolve" in lowered
        or "module not found" in lowered
        or "could not find a version that satisfies the requirement" in lowered
        or "no matching distribution found" in lowered
        or "pip install failed" in lowered
        or "dependency installation failed" in lowered
        or "requirements could not be resolved" in lowered
    )
    if dependency_match:
        findings.append(
            Finding(
                rule_id="ci_cd_dependency_failure",
                rule_family="ci_cd",
                severity="FAIL",
                status="FAIL",
                description="Dependency resolution failed.",
                evidence=_extract_evidence(
                    log_text,
                    [
                        "could not find a version that satisfies the requirement",
                        "no matching distribution found",
                        "failed to resolve",
                        "could not resolve",
                        "module not found",
                        "pip install failed",
                        "dependency installation failed",
                        "requirements could not be resolved",
                    ],
                ),
                location="log",
            )
        )

    test_match = (
        "pytest failed" in lowered
        or "test failed" in lowered
        or "assertionerror" in lowered
    )
    if test_match:
        findings.append(
            Finding(
                rule_id="ci_cd_test_failure",
                rule_family="ci_cd",
                severity="FAIL",
                status="FAIL",
                description="One or more tests failed in the validation pipeline.",
                evidence=_extract_evidence(
                    log_text,
                    ["pytest failed", "test failed", "assertionerror"],
                ),
                location="log",
            )
        )

    build_match = (
        "build failed" in lowered
        or "error: failed to build" in lowered
        or "compilation failed" in lowered
    )
    if build_match:
        findings.append(
            Finding(
                rule_id="ci_cd_build_failure",
                rule_family="ci_cd",
                severity="FAIL",
                status="FAIL",
                description="The build pipeline failed during compilation or packaging.",
                evidence=_extract_evidence(
                    log_text,
                    ["build failed", "error: failed to build", "compilation failed"],
                ),
                location="log",
            )
        )

    if not findings and "warning" in lowered and "deprecated" in lowered:
        findings.append(
            Finding(
                rule_id="ci_cd_build_failure",
                rule_family="ci_cd",
                severity="WARNING",
                status="WARNING",
                description="A deprecation warning was detected in the pipeline log.",
                evidence=_extract_evidence(log_text, ["warning", "deprecated"]),
                location="log",
            )
        )

    return findings


def _extract_evidence(log_text: str, needles: list[str]) -> str:
    lower = log_text.lower()
    for needle in needles:
        idx = lower.find(needle)
        if idx != -1:
            start = max(0, idx - 80)
            end = min(len(log_text), idx + 200)
            return log_text[start:end].strip()
    return log_text[:200].strip()
