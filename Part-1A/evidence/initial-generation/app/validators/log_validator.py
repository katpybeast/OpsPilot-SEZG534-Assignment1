from __future__ import annotations

from app.models.finding import Finding
from app.rules.ci_cd_rules import evaluate_ci_cd_rules


def validate_log_contents(text: str) -> list[Finding]:
    if not text or not text.strip():
        raise ValueError("The log is empty or unreadable.")
    return evaluate_ci_cd_rules(text)
