from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import RiskLevel


class RiskQuestionOption(BaseModel):
    option_key: str
    title: str
    score: int


    model_config = ConfigDict(from_attributes=True)


class RiskQuestion(BaseModel):
    question_id: str
    title: str
    options: list[RiskQuestionOption]


    model_config = ConfigDict(from_attributes=True)


class RiskQuestionnaireView(BaseModel):
    title: str
    questions: list[RiskQuestion]


    model_config = ConfigDict(from_attributes=True)


class SubmitSuitabilityRequest(BaseModel):
    answers: dict[str, int] = Field(min_length=3)

    @field_validator("answers")
    @classmethod
    def ensure_scores_non_negative(cls, answers: dict[str, int]) -> dict[str, int]:
        for key, value in answers.items():
            if value < 0:
                raise ValueError(f"score of {key} must be >= 0")
        return answers


class SuitabilityResultView(BaseModel):
    completed: bool
    risk_level: RiskLevel | None = None
    score: int = 0
    answers: dict[str, int]
    submitted_at: datetime | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
