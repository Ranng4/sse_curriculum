from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class ForumBoardCategory(StrEnum):
    MARKET = "market"
    TOPIC = "topic"
    COMPANY_RESEARCH = "company_research"
    QA = "qa"


@dataclass
class ForumBoard:
    id: str = field(default_factory=lambda: str(uuid4()))
    slug: str = ""
    name: str = ""
    description: str = ""
    category: ForumBoardCategory = ForumBoardCategory.TOPIC
    market: str | None = None
    parent_id: str | None = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()
