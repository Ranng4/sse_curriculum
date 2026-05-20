from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class PostType(StrEnum):
    NORMAL = "normal"
    LONGFORM = "longform"
    REALTIME = "realtime"


@dataclass
class Post:
    id: str = field(default_factory=lambda: str(uuid4()))
    author_id: str = ""
    board_id: str = ""
    title: str = ""
    content: str = ""
    post_type: PostType = PostType.NORMAL
    stock_codes: list[str] = field(default_factory=list)
    image_urls: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()


@dataclass
class Comment:
    id: str = field(default_factory=lambda: str(uuid4()))
    post_id: str = ""
    author_id: str = ""
    content: str = ""
    parent_comment_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()
