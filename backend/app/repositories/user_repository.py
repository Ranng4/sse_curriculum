from __future__ import annotations

from app.core.errors import ConflictError, NotFoundError
from app.models.user import User
from app.repositories.sqlite_backend import decode_payload, encode_payload, get_connection


class InMemoryUserRepository:
    """
    Backward-compatible class name; now backed by SQLite persistence.
    """

    def create(self, user: User) -> User:
        self._check_index_conflict(user)
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (id, phone, email, wechat_open_id, weibo_open_id, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user.id,
                    user.auth.phone,
                    user.auth.email,
                    user.auth.wechat_open_id,
                    user.auth.weibo_open_id,
                    encode_payload(user),
                ),
            )
            conn.commit()
        return self.get(user.id)

    def save(self, user: User) -> User:
        self._check_index_conflict(user)
        with get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE users
                SET phone = ?, email = ?, wechat_open_id = ?, weibo_open_id = ?, payload = ?
                WHERE id = ?
                """,
                (
                    user.auth.phone,
                    user.auth.email,
                    user.auth.wechat_open_id,
                    user.auth.weibo_open_id,
                    encode_payload(user),
                    user.id,
                ),
            )
            conn.commit()
        if cursor.rowcount == 0:
            raise NotFoundError("user not found")
        return self.get(user.id)

    def get(self, user_id: str) -> User:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT payload FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError("user not found")
        return decode_payload(row["payload"])

    def find_by_phone(self, phone: str) -> User | None:
        return self._find_by_field("phone", phone)

    def find_by_email(self, email: str) -> User | None:
        return self._find_by_field("email", email)

    def find_by_wechat_open_id(self, open_id: str) -> User | None:
        return self._find_by_field("wechat_open_id", open_id)

    def find_by_weibo_open_id(self, open_id: str) -> User | None:
        return self._find_by_field("weibo_open_id", open_id)

    def _find_by_field(self, field: str, value: str) -> User | None:
        with get_connection() as conn:
            row = conn.execute(
                f"SELECT id FROM users WHERE {field} = ?",
                (value,),
            ).fetchone()
        if row is None:
            return None
        return self.get(row["id"])

    def _check_index_conflict(self, user: User) -> None:
        auth = user.auth
        if auth.phone:
            owner = self._find_owner_id("phone", auth.phone)
            if owner and owner != user.id:
                raise ConflictError("phone already exists")
        if auth.email:
            owner = self._find_owner_id("email", auth.email)
            if owner and owner != user.id:
                raise ConflictError("email already exists")
        if auth.wechat_open_id:
            owner = self._find_owner_id("wechat_open_id", auth.wechat_open_id)
            if owner and owner != user.id:
                raise ConflictError("wechat account already exists")
        if auth.weibo_open_id:
            owner = self._find_owner_id("weibo_open_id", auth.weibo_open_id)
            if owner and owner != user.id:
                raise ConflictError("weibo account already exists")

    def _find_owner_id(self, field: str, value: str) -> str | None:
        with get_connection() as conn:
            row = conn.execute(
                f"SELECT id FROM users WHERE {field} = ?",
                (value,),
            ).fetchone()
        if row is None:
            return None
        return row["id"]
