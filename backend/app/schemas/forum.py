from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.forum import ForumBoardCategory


class ForumBoardView(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    category: ForumBoardCategory
    market: str | None = None
    parent_id: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ForumSectionView(BaseModel):
    category: ForumBoardCategory
    title: str
    description: str
    boards: list[ForumBoardView]


class ForumBoardCreateRequest(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=300)
    category: ForumBoardCategory
    market: str | None = Field(default=None, max_length=32)
    parent_id: str | None = None
    sort_order: int = Field(default=0, ge=0, le=9999)
    is_active: bool = True

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "-")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()


class ForumBoardUpdateRequest(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=300)
    category: ForumBoardCategory | None = None
    market: str | None = Field(default=None, max_length=32)
    parent_id: str | None = None
    sort_order: int | None = Field(default=None, ge=0, le=9999)
    is_active: bool | None = None

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower().replace(" ", "-")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()
