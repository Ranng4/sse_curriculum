from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T

    model_config = ConfigDict(use_enum_values=True)


class TimeStampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(use_enum_values=True)

