"""Admin schemas — review, user management, analytics views.

AI-generated: Pydantic models for admin API request/response.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Post Review ──


class PostReviewRequest(BaseModel):
    action: str = Field(min_length=2, max_length=16, description="approve / reject / flag")
    reason: str | None = Field(default=None, max_length=500)


class PostReviewView(BaseModel):
    id: str
    title: str
    author_id: str
    author_nickname: str
    board_name: str
    created_at: datetime
    review_status: str = "pending"          # pending / approved / rejected / flagged
    review_reason: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ── User Management ──


class UserManageRequest(BaseModel):
    action: str = Field(min_length=2, max_length=16, description="warn / mute / ban / unban")
    reason: str | None = Field(default=None, max_length=500)


class UserManageView(BaseModel):
    user_id: str
    nickname: str
    phone: str | None = None
    email: str | None = None
    register_method: str
    posts_count: int = 0
    user_status: str = "active"              # active / warned / muted / banned
    status_reason: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Analytics ──


class AdminStatsView(BaseModel):
    total_users: int = 0
    total_posts: int = 0
    total_comments: int = 0
    total_likes: int = 0
    active_users_today: int = 0
    posts_today: int = 0
    pending_reviews: int = 0
    flagged_content: int = 0
    top_boards: list[dict] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
