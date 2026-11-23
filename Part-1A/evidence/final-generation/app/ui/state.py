from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DashboardState:
    history: list[dict[str, Any]] = field(default_factory=list)
    current_report: dict[str, Any] | None = None

    def set_history(self, items: list[dict[str, Any]]) -> None:
        self.history = items

    def set_current_report(self, report: dict[str, Any] | None) -> None:
        self.current_report = report
