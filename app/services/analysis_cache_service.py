"""Bounded in-memory cache for short-lived editor analysis requests."""

from __future__ import annotations

from hashlib import sha256
from threading import Lock
from time import monotonic
from typing import Any


class AnalysisCacheService:
    def __init__(self, ttl_seconds: int = 120, max_entries: int = 500) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: dict[str, tuple[float, dict[str, Any]]] = {}
        self._lock = Lock()

    @staticmethod
    def key(scope: str, files: list[dict[str, Any]]) -> str:
        digest = sha256()
        digest.update(scope.encode())
        for file in sorted(files, key=lambda item: item["path"]):
            digest.update(file["path"].encode())
            digest.update(file.get("content", "").encode())
            digest.update(file.get("change_type", "modified").encode())
        return digest.hexdigest()

    def get(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            entry = self._entries.get(key)
            if not entry or monotonic() - entry[0] > self.ttl_seconds:
                self._entries.pop(key, None)
                return None
            return entry[1]

    def set(self, key: str, value: dict[str, Any]) -> None:
        with self._lock:
            if len(self._entries) >= self.max_entries:
                oldest = min(self._entries, key=lambda item: self._entries[item][0])
                self._entries.pop(oldest, None)
            self._entries[key] = (monotonic(), value)


analysis_cache_service = AnalysisCacheService()
