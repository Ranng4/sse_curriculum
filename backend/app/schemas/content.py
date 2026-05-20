from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.content import PostType


class AuthorView(BaseModel):
    user_id: str
    nickname: str


class PostMetricsView(BaseModel):
    like_count: int = 0
    favorite_count: int = 0
    comment_count: int = 0
    engagement_score: int = 0


class PostView(BaseModel):
    id: str
    board_id: str
    board_name: str
    title: str
    content: str
    post_type: PostType
    stock_codes: list[str]
    image_urls: list[str]
    author: AuthorView
    created_at: datetime
    updated_at: datetime
    metrics: PostMetricsView
    liked_by_me: bool = False
    favorited_by_me: bool = False

    model_config = ConfigDict(use_enum_values=True)


class CommentView(BaseModel):
    id: str
    post_id: str
    author: AuthorView
    content: str
    parent_comment_id: str | None = None
    created_at: datetime
    updated_at: datetime


class PostCreateRequest(BaseModel):
    board_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)
    post_type: PostType = PostType.NORMAL
    stock_codes: list[str] = Field(default_factory=list, max_length=10)
    image_urls: list[str] = Field(default_factory=list, max_length=12)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        return value.strip()

    @field_validator("stock_codes")
    @classmethod
    def normalize_codes(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            code = item.strip().upper()
            if not code or code in seen:
                continue
            seen.add(code)
            normalized.append(code)
        return normalized


class PostUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    post_type: PostType | None = None
    stock_codes: list[str] | None = Field(default=None, max_length=10)
    image_urls: list[str] | None = Field(default=None, max_length=12)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("stock_codes")
    @classmethod
    def normalize_codes(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            code = item.strip().upper()
            if not code or code in seen:
                continue
            seen.add(code)
            normalized.append(code)
        return normalized


class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    parent_comment_id: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        return value.strip()


class SearchSuggestView(BaseModel):
    query: str
    suggestions: list[str]


class PostSortOption(BaseModel):
    sort: Literal["latest", "hot"] = "latest"
