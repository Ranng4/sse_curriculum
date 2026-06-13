"""Message schemas — private messaging request/response models.

AI-generated: Pydantic models for messaging API.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SendMessageRequest(BaseModel):
    to_user_id: str = Field(min_length=1, max_length=64)
    content: str = Field(min_length=1, max_length=2000)
    image_url: str | None = Field(default=None, max_length=512)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        return value.strip()


class MessageView(BaseModel):
    id: str
    from_id: str
    from_nickname: str
    to_id: str
    content: str
    image_url: str | None = None
    created_at: datetime
    is_read: bool = False


class ConversationPreview(BaseModel):
    partner_id: str
    partner_nickname: str
    unread_count: int = 0
    last_message: str
    last_time: datetime
    last_from_me: bool = False


class UnreadCountView(BaseModel):
    unread_count: int = 0
