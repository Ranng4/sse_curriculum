from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FollowUserView(BaseModel):
    user_id: str
    nickname: str
    followed_at: datetime


class FollowActionResultView(BaseModel):
    target_user_id: str
    is_following: bool
    following_count: int
    follower_count_of_target: int


class FollowStatsView(BaseModel):
    user_id: str
    following_count: int
    follower_count: int
