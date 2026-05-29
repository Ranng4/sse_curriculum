from __future__ import annotations

from datetime import UTC, datetime

from app.repositories.sqlite_backend import get_connection


def utc_now() -> datetime:
    return datetime.now(UTC)


class InMemorySocialRepository:
    """
    Backward-compatible class name; now backed by SQLite persistence.
    """

    def follow(self, follower_id: str, followee_id: str) -> datetime:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT followed_at FROM follows
                WHERE follower_id = ? AND followee_id = ?
                """,
                (follower_id, followee_id),
            ).fetchone()
            if row:
                followed_at = datetime.fromisoformat(row["followed_at"])
                return followed_at

            followed_at = utc_now()
            conn.execute(
                """
                INSERT INTO follows (follower_id, followee_id, followed_at)
                VALUES (?, ?, ?)
                """,
                (follower_id, followee_id, followed_at.isoformat()),
            )
            conn.commit()
        return followed_at

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                DELETE FROM follows
                WHERE follower_id = ? AND followee_id = ?
                """,
                (follower_id, followee_id),
            )
            conn.commit()

    def is_following(self, follower_id: str, followee_id: str) -> bool:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM follows
                WHERE follower_id = ? AND followee_id = ?
                """,
                (follower_id, followee_id),
            ).fetchone()
        return row is not None

    def list_following(self, follower_id: str) -> list[tuple[str, datetime]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT followee_id, followed_at
                FROM follows
                WHERE follower_id = ?
                ORDER BY followed_at DESC
                """,
                (follower_id,),
            ).fetchall()
        return [
            (row["followee_id"], datetime.fromisoformat(row["followed_at"]))
            for row in rows
        ]

    def list_followers(self, followee_id: str) -> list[tuple[str, datetime]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT follower_id, followed_at
                FROM follows
                WHERE followee_id = ?
                ORDER BY followed_at DESC
                """,
                (followee_id,),
            ).fetchall()
        return [
            (row["follower_id"], datetime.fromisoformat(row["followed_at"]))
            for row in rows
        ]

    def following_count(self, follower_id: str) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(1) AS c FROM follows WHERE follower_id = ?",
                (follower_id,),
            ).fetchone()
        return int(row["c"]) if row else 0

    def follower_count(self, followee_id: str) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(1) AS c FROM follows WHERE followee_id = ?",
                (followee_id,),
            ).fetchone()
        return int(row["c"]) if row else 0
