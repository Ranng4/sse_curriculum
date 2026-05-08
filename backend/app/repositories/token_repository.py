from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.errors import NotFoundError


@dataclass
class AccessTokenRecord:
    token: str
    user_id: str
    expires_at: datetime

    def expired(self) -> bool:
        return self.expires_at <= datetime.now(UTC)


class InMemoryTokenRepository:
    def __init__(self) -> None:
        self._records: dict[str, AccessTokenRecord] = {}

    def save(self, record: AccessTokenRecord) -> None:
        self._records[record.token] = record

    def get(self, token: str) -> AccessTokenRecord:
        record = self._records.get(token)
        if record is None:
            raise NotFoundError("access token not found")
        return record

    def revoke(self, token: str) -> None:
        self._records.pop(token, None)

