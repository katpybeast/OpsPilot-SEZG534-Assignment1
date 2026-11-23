from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import uuid


@dataclass
class Finding:
    rule_id: str
    rule_family: str
    severity: str
    status: str
    description: str
    evidence: str = ""
    location: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    validation_run_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["id"] = self.id
        return payload
