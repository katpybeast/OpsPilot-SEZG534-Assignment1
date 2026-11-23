from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class ValidationRun:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_file_name: str = ""
    source_type: str = ""
    status: str = "PASS"
    file_size_bytes: int = 0
    user_context: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "source_file_name": self.source_file_name,
            "source_type": self.source_type,
            "status": self.status,
            "file_size_bytes": self.file_size_bytes,
            "user_context": self.user_context,
        }
