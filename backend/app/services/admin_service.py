"""Admin service — content review, user management, forum analytics.

AI-generated: business logic for moderation operations.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.errors import NotFoundError, ValidationError
from app.repositories.content_repository import InMemoryContentRepository
from app.repositories.forum_repository import InMemoryForumBoardRepository
from app.repositories.social_repository import InMemorySocialRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.repositories.sqlite_backend import get_connection
from app.schemas.admin import (
    AdminStatsView,
    PostReviewRequest,
    PostReviewView,
    UserManageRequest,
    UserManageView,
)


def _ensure_review_table() -> None:
    """Ensure post_reviews table exists."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS post_reviews (
                post_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'pending',
                reason TEXT,
                reviewed_by TEXT,
                reviewed_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_status (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'active',
                reason TEXT,
                updated_by TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()


class AdminService:
    """Admin operations for content moderation and user management."""

    def __init__(
        self,
        user_repository: InMemoryUserRepository,
        content_repository: InMemoryContentRepository,
        forum_repository: InMemoryForumBoardRepository,
        social_repository: InMemorySocialRepository,
    ) -> None:
        self.user_repo = user_repository
        self.content_repo = content_repository
        self.forum_repo = forum_repository
        self.social_repo = social_repository
        _ensure_review_table()

    # ── Stats ──

    def get_stats(self) -> AdminStatsView:
        posts = self.content_repo.list_posts()
        users = list(self._all_user_rows())

        # Count today's activity
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        posts_today = sum(1 for p in posts if p.created_at.strftime("%Y-%m-%d") == today)

        # Active users today: distinct authors of today's posts/comments
        active_set = set()
        for p in posts:
            if p.created_at.strftime("%Y-%m-%d") == today:
                active_set.add(p.author_id)

        with get_connection() as conn:
            pending = conn.execute(
                "SELECT COUNT(1) FROM post_reviews WHERE status='pending'"
            ).fetchone()
            flagged = conn.execute(
                "SELECT COUNT(1) FROM post_reviews WHERE status='flagged'"
            ).fetchone()

        # Top boards by post count
        board_counts: dict[str, int] = {}
        board_names: dict[str, str] = {}
        for p in posts:
            board_counts[p.board_id] = board_counts.get(p.board_id, 0) + 1
            if p.board_id not in board_names:
                try:
                    board = self.forum_repo.get(p.board_id)
                    board_names[p.board_id] = board.name
                except NotFoundError:
                    board_names[p.board_id] = p.board_id

        top_boards = sorted(
            [{"board_name": board_names[bid], "post_count": cnt} for bid, cnt in board_counts.items()],
            key=lambda x: x["post_count"],
            reverse=True,
        )[:10]

        return AdminStatsView(
            total_users=len(users),
            total_posts=len(posts),
            total_comments=sum(self.content_repo.comment_count(p.id) for p in posts),
            total_likes=sum(self.content_repo.like_count(p.id) for p in posts),
            active_users_today=len(active_set),
            posts_today=posts_today,
            pending_reviews=pending["COUNT(1)"] if pending else 0,
            flagged_content=flagged["COUNT(1)"] if flagged else 0,
            top_boards=top_boards,
        )

    # ── Content Review ──

    def list_posts_for_review(
        self, status: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[PostReviewView]:
        posts = self.content_repo.list_posts()

        with get_connection() as conn:
            rows = conn.execute("SELECT post_id, status, reason, reviewed_by, reviewed_at FROM post_reviews").fetchall()
        review_map = {r["post_id"]: r for r in rows}

        results = []
        for p in posts:
            review = review_map.get(p.id)
            review_status = review["status"] if review else "approved"  # default: no review = approved

            if status and status != "all" and review_status != status:
                continue

            try:
                user = self.user_repo.get(p.author_id)
                nickname = user.profile.nickname
            except NotFoundError:
                nickname = "unknown"

            try:
                board = self.forum_repo.get(p.board_id)
                board_name = board.name
            except NotFoundError:
                board_name = p.board_id

            results.append(PostReviewView(
                id=p.id,
                title=p.title,
                author_id=p.author_id,
                author_nickname=nickname,
                board_name=board_name,
                created_at=p.created_at,
                review_status=review_status,
                review_reason=review["reason"] if review else None,
                reviewed_by=review["reviewed_by"] if review else None,
                reviewed_at=datetime.fromisoformat(review["reviewed_at"]) if review and review["reviewed_at"] else None,
            ))

        results.sort(key=lambda x: x.created_at, reverse=True)
        return results[offset:offset + limit]

    def review_post(self, post_id: str, reviewer_id: str, req: PostReviewRequest) -> PostReviewView:
        post = self.content_repo.get_post(post_id)

        if req.action not in ("approve", "reject", "flag"):
            raise ValidationError("action must be: approve, reject, flag")

        now = datetime.now(UTC).isoformat()
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO post_reviews (post_id, status, reason, reviewed_by, reviewed_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(post_id) DO UPDATE SET
                    status=excluded.status, reason=excluded.reason,
                    reviewed_by=excluded.reviewed_by, reviewed_at=excluded.reviewed_at
                """,
                (post_id, req.action, req.reason, reviewer_id, now),
            )
            conn.commit()

        try:
            user = self.user_repo.get(post.author_id)
            nickname = user.profile.nickname
        except NotFoundError:
            nickname = "unknown"
        try:
            board = self.forum_repo.get(post.board_id)
            board_name = board.name
        except NotFoundError:
            board_name = post.board_id

        return PostReviewView(
            id=post.id,
            title=post.title,
            author_id=post.author_id,
            author_nickname=nickname,
            board_name=board_name,
            created_at=post.created_at,
            review_status=req.action,
            review_reason=req.reason,
            reviewed_by=reviewer_id,
            reviewed_at=datetime.fromisoformat(now),
        )

    # ── User Management ──

    def list_users(
        self, status: str | None = None, keyword: str | None = None,
        limit: int = 20, offset: int = 0,
    ) -> list[UserManageView]:
        with get_connection() as conn:
            rows = conn.execute("SELECT user_id, status, reason, updated_by, updated_at FROM user_status").fetchall()
        status_map = {r["user_id"]: r for r in rows}

        results = []
        all_users = self._all_user_rows()
        for row in all_users:
            user = self.user_repo.get(row["id"])
            status_row = status_map.get(user.id)
            user_status = status_row["status"] if status_row else "active"

            if status and status != "all" and user_status != status:
                continue
            if keyword:
                kw = keyword.strip().lower()
                profile = user.profile
                if kw not in profile.nickname.lower():
                    continue

            results.append(UserManageView(
                user_id=user.id,
                nickname=user.profile.nickname,
                phone=user.auth.phone,
                email=user.auth.email,
                register_method=user.register_method.value,
                posts_count=user.profile.achievements.posts_count,
                user_status=user_status,
                status_reason=status_row["reason"] if status_row else None,
                created_at=user.created_at,
            ))

        results.sort(key=lambda x: x.created_at or datetime.min.replace(tzinfo=UTC), reverse=True)
        return results[offset:offset + limit]

    def manage_user(self, user_id: str, admin_id: str, req: UserManageRequest) -> UserManageView:
        user = self.user_repo.get(user_id)

        if req.action not in ("warn", "mute", "ban", "unban"):
            raise ValidationError("action must be: warn, mute, ban, unban")

        new_status = "active" if req.action == "unban" else req.action + "ed" if req.action == "ban" else req.action
        # Normalize: warned / muted / banned / active
        if req.action == "ban":
            new_status = "banned"
        elif req.action == "unban":
            new_status = "active"

        now = datetime.now(UTC).isoformat()
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_status (user_id, status, reason, updated_by, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    status=excluded.status, reason=excluded.reason,
                    updated_by=excluded.updated_by, updated_at=excluded.updated_at
                """,
                (user_id, new_status, req.reason, admin_id, now),
            )
            conn.commit()

        return UserManageView(
            user_id=user.id,
            nickname=user.profile.nickname,
            phone=user.auth.phone,
            email=user.auth.email,
            register_method=user.register_method.value,
            posts_count=user.profile.achievements.posts_count,
            user_status=new_status,
            status_reason=req.reason,
            created_at=user.created_at,
        )

    # ── Helpers ──

    def _all_user_rows(self):
        with get_connection() as conn:
            return conn.execute("SELECT id, phone, email FROM users").fetchall()
