from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.models.finding import Finding
from app.models.validation_run import ValidationRun


@dataclass
class Report:
    validation_run: ValidationRun
    findings: list[Finding] = field(default_factory=list)
    summary_status: str = "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_run": self.validation_run.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "summary_status": self.summary_status,
        }
