from __future__ import annotations

from app.storage.sqlite_repo import SqliteRepo


class HistoryService:
    def __init__(self, repo: SqliteRepo | None = None):
        self.repo = repo or SqliteRepo()

    def list_history(self) -> list[dict]:
        return self.repo.get_history()

    def get_latest(self) -> dict | None:
        history = self.list_history()
        return history[0] if history else None
