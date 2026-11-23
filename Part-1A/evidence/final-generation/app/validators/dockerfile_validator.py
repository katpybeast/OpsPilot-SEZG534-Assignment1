from __future__ import annotations

from app.models.finding import Finding
from app.rules.docker_rules import evaluate_dockerfile_rules


def validate_dockerfile_contents(text: str) -> list[Finding]:
    if not text or not text.strip():
        raise ValueError("The Dockerfile is empty or unreadable.")
    return evaluate_dockerfile_rules(text)
