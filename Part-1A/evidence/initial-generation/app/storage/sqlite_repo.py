from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.models.report import Report


class SqliteRepo:
    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            base = Path(__file__).resolve().parents[2]
            db_path = base / "opspilot.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_runs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    source_file_name TEXT,
                    source_type TEXT,
                    status TEXT,
                    file_size_bytes INTEGER,
                    user_context TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    validation_run_id TEXT,
                    rule_id TEXT,
                    rule_family TEXT,
                    severity TEXT,
                    status TEXT,
                    description TEXT,
                    evidence TEXT,
                    location TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS report_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT,
                    summary_status TEXT,
                    source_file_name TEXT,
                    validation_run_id TEXT,
                    findings_count INTEGER,
                    serialized_report TEXT
                )
                """
            )
            conn.commit()

    def save_report(self, report: Report) -> dict[str, Any]:
        run = report.validation_run
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO validation_runs "
                "(id, created_at, source_file_name, source_type, status, "
                "file_size_bytes, user_context) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    run.id,
                    run.created_at,
                    run.source_file_name,
                    run.source_type,
                    run.status,
                    run.file_size_bytes,
                    run.user_context,
                ),
            )
            for finding in report.findings:
                conn.execute(
                    "INSERT OR REPLACE INTO findings "
                    "(id, validation_run_id, rule_id, rule_family, severity, "
                    "status, description, evidence, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        finding.id,
                        run.id,
                        finding.rule_id,
                        finding.rule_family,
                        finding.severity,
                        finding.status,
                        finding.description,
                        finding.evidence,
                        finding.location,
                    ),
                )
            serialized = json.dumps(report.to_dict())
            conn.execute(
                "INSERT INTO report_records "
                "(created_at, summary_status, source_file_name, validation_run_id, "
                "findings_count, serialized_report) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    run.created_at,
                    report.summary_status,
                    run.source_file_name,
                    run.id,
                    len(report.findings),
                    serialized,
                ),
            )
            conn.commit()
        return {"id": run.id, "summary_status": report.summary_status}

    def get_history(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT created_at, summary_status, source_file_name, "
                "validation_run_id, findings_count, serialized_report "
                "FROM report_records ORDER BY id DESC"
            ).fetchall()
        return [
            {
                "created_at": row[0],
                "summary_status": row[1],
                "source_file_name": row[2],
                "validation_run_id": row[3],
                "findings_count": row[4],
                "serialized_report": json.loads(row[5]),
            }
            for row in rows
        ]
