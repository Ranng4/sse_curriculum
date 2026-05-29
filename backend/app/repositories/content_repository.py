from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.core.errors import NotFoundError
from app.models.content import Comment, Post
from app.repositories.sqlite_backend import decode_payload, encode_payload, get_connection


class InMemoryContentRepository:
    """
    Backward-compatible class name; now backed by SQLite persistence.
    """

    def create_post(self, post: Post) -> Post:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO posts (id, board_id, author_id, created_at, payload)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    post.id,
                    post.board_id,
                    post.author_id,
                    post.created_at.isoformat(),
                    encode_payload(post),
                ),
            )
            conn.commit()
        return self.get_post(post.id)

    def save_post(self, post: Post) -> Post:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE posts
                SET board_id = ?, author_id = ?, created_at = ?, payload = ?
                WHERE id = ?
                """,
                (
                    post.board_id,
                    post.author_id,
                    post.created_at.isoformat(),
                    encode_payload(post),
                    post.id,
                ),
            )
            conn.commit()
        if cursor.rowcount == 0:
            raise NotFoundError("post not found")
        return self.get_post(post.id)

    def get_post(self, post_id: str) -> Post:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT payload FROM posts WHERE id = ?",
                (post_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError("post not found")
        return decode_payload(row["payload"])

    def list_posts(self) -> list[Post]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT payload FROM posts ORDER BY created_at DESC"
            ).fetchall()
        return [decode_payload(row["payload"]) for row in rows]

    def create_comment(self, comment: Comment) -> Comment:
        self.get_post(comment.post_id)
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO comments (id, post_id, author_id, parent_comment_id, created_at, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    comment.id,
                    comment.post_id,
                    comment.author_id,
                    comment.parent_comment_id,
                    comment.created_at.isoformat(),
                    encode_payload(comment),
                ),
            )
            conn.commit()
        return self.get_comment(comment.id)

    def get_comment(self, comment_id: str) -> Comment:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT payload FROM comments WHERE id = ?",
                (comment_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError("comment not found")
        return decode_payload(row["payload"])

    def list_comments(self, post_id: str) -> list[Comment]:
        self.get_post(post_id)
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT payload FROM comments WHERE post_id = ? ORDER BY created_at ASC",
                (post_id,),
            ).fetchall()
        return [decode_payload(row["payload"]) for row in rows]

    def set_like(self, post_id: str, user_id: str, enabled: bool) -> int:
        self.get_post(post_id)
        with get_connection() as conn:
            if enabled:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO post_likes (post_id, user_id, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (post_id, user_id, datetime.now(UTC).isoformat()),
                )
            else:
                conn.execute(
                    "DELETE FROM post_likes WHERE post_id = ? AND user_id = ?",
                    (post_id, user_id),
                )
            conn.commit()
        return self.like_count(post_id)

    def set_favorite(self, post_id: str, user_id: str, enabled: bool) -> int:
        self.get_post(post_id)
        with get_connection() as conn:
            if enabled:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO post_favorites (post_id, user_id, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (post_id, user_id, datetime.now(UTC).isoformat()),
                )
            else:
                conn.execute(
                    "DELETE FROM post_favorites WHERE post_id = ? AND user_id = ?",
                    (post_id, user_id),
                )
            conn.commit()
        return self.favorite_count(post_id)

    def is_liked(self, post_id: str, user_id: str) -> bool:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM post_likes WHERE post_id = ? AND user_id = ?",
                (post_id, user_id),
            ).fetchone()
        return row is not None

    def is_favorited(self, post_id: str, user_id: str) -> bool:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM post_favorites WHERE post_id = ? AND user_id = ?",
                (post_id, user_id),
            ).fetchone()
        return row is not None

    def like_count(self, post_id: str) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(1) AS c FROM post_likes WHERE post_id = ?",
                (post_id,),
            ).fetchone()
        return int(row["c"]) if row else 0

    def favorite_count(self, post_id: str) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(1) AS c FROM post_favorites WHERE post_id = ?",
                (post_id,),
            ).fetchone()
        return int(row["c"]) if row else 0

    def comment_count(self, post_id: str) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(1) AS c FROM comments WHERE post_id = ?",
                (post_id,),
            ).fetchone()
        return int(row["c"]) if row else 0

    def engagement_score(self, post_id: str) -> int:
        return (
            self.like_count(post_id) * 2
            + self.favorite_count(post_id) * 3
            + self.comment_count(post_id)
        )

    def list_hot_posts(self, limit: int = 20, days: int = 7) -> list[Post]:
        threshold = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT payload FROM posts
                WHERE created_at >= ?
                """,
                (threshold,),
            ).fetchall()
        candidates = [decode_payload(row["payload"]) for row in rows]
        candidates.sort(
            key=lambda post: (
                self.engagement_score(post.id),
                post.created_at,
            ),
            reverse=True,
        )
        return candidates[:limit]
