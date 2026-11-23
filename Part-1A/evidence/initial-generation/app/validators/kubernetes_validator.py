from __future__ import annotations

from app.models.finding import Finding
from app.rules.kubernetes_rules import evaluate_kubernetes_rules


def validate_kubernetes_contents(text: str) -> list[Finding]:
    if not text or not text.strip():
        raise ValueError("The Kubernetes manifest is empty or unreadable.")
    return evaluate_kubernetes_rules(text)
