"""Message repository — SQLite-backed private messaging storage.

AI-generated: CRUD for messages table with conversation queries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.repositories.sqlite_backend import get_connection


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid4()))
    from_id: str = ""
    to_id: str = ""
    content: str = ""
    image_url: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    is_read: bool = False


class MessageRepository:
    """Backed by SQLite messages table."""

    def create(self, msg: Message) -> Message:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO messages (id, from_id, to_id, content, image_url, created_at, is_read)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (msg.id, msg.from_id, msg.to_id, msg.content, msg.image_url,
                 msg.created_at.isoformat(), 1 if msg.is_read else 0),
            )
            conn.commit()
        return self.get(msg.id)

    def get(self, msg_id: str) -> Message:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)).fetchone()
        if row is None:
            raise LookupError("message not found")
        return Message(
            id=row["id"], from_id=row["from_id"], to_id=row["to_id"],
            content=row["content"], image_url=row["image_url"],
            created_at=datetime.fromisoformat(row["created_at"]),
            is_read=bool(row["is_read"]),
        )

    def list_conversation(self, user_a: str, user_b: str, limit: int = 50) -> list[Message]:
        """List messages between two users (ordered by time)."""
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM messages
                   WHERE (from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?)
                   ORDER BY created_at DESC LIMIT ?""",
                (user_a, user_b, user_b, user_a, limit),
            ).fetchall()
        return [Message(
            id=r["id"], from_id=r["from_id"], to_id=r["to_id"],
            content=r["content"], image_url=r["image_url"],
            created_at=datetime.fromisoformat(r["created_at"]),
            is_read=bool(r["is_read"]),
        ) for r in rows][::-1]  # reverse for chronological order

    def list_conversations(self, user_id: str) -> list[dict]:
        """Get list of conversation partners with last message preview and unread count."""
        with get_connection() as conn:
            # Get all distinct conversation partners
            rows = conn.execute(
                """SELECT DISTINCT
                     CASE WHEN from_id = ? THEN to_id ELSE from_id END AS partner_id
                   FROM messages
                   WHERE from_id = ? OR to_id = ?""",
                (user_id, user_id, user_id),
            ).fetchall()

            conversations = []
            for r in rows:
                partner = r["partner_id"]
                # Get unread count
                unread = conn.execute(
                    "SELECT COUNT(1) FROM messages WHERE from_id = ? AND to_id = ? AND is_read = 0",
                    (partner, user_id),
                ).fetchone()
                # Get last message
                last = conn.execute(
                    """SELECT * FROM messages
                       WHERE (from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?)
                       ORDER BY created_at DESC LIMIT 1""",
                    (user_id, partner, partner, user_id),
                ).fetchone()
                if last:
                    conversations.append({
                        "partner_id": partner,
                        "unread_count": unread["COUNT(1)"],
                        "last_message": last["content"],
                        "last_time": datetime.fromisoformat(last["created_at"]),
                        "last_from_me": last["from_id"] == user_id,
                    })

            conversations.sort(key=lambda c: c["last_time"], reverse=True)
            return conversations

    def mark_read(self, user_id: str, from_id: str) -> int:
        """Mark all messages from from_id to user_id as read. Returns count."""
        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE messages SET is_read = 1 WHERE from_id = ? AND to_id = ? AND is_read = 0",
                (from_id, user_id),
            )
            conn.commit()
        return cursor.rowcount

    def unread_count(self, user_id: str) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(1) AS c FROM messages WHERE to_id = ? AND is_read = 0",
                (user_id,),
            ).fetchone()
        return int(row["c"]) if row else 0
