from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.errors import NotFoundError
from app.repositories.sqlite_backend import get_connection


@dataclass
class AccessTokenRecord:
    token: str
    user_id: str
    expires_at: datetime

    def expired(self) -> bool:
        return self.expires_at <= datetime.now(UTC)


class InMemoryTokenRepository:
    """
    Backward-compatible class name; now backed by SQLite persistence.
    """

    def save(self, record: AccessTokenRecord) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO access_tokens (token, user_id, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(token) DO UPDATE SET
                  user_id = excluded.user_id,
                  expires_at = excluded.expires_at
                """,
                (record.token, record.user_id, record.expires_at.isoformat()),
            )
            conn.commit()

    def get(self, token: str) -> AccessTokenRecord:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT token, user_id, expires_at FROM access_tokens WHERE token = ?",
                (token,),
            ).fetchone()
        if row is None:
            raise NotFoundError("access token not found")
        return AccessTokenRecord(
            token=row["token"],
            user_id=row["user_id"],
            expires_at=datetime.fromisoformat(row["expires_at"]),
        )

    def revoke(self, token: str) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM access_tokens WHERE token = ?", (token,))
            conn.commit()
