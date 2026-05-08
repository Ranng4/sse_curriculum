from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.core.enums import (
    AchievementBadge,
    MarketInterest,
    ProfessionalDocType,
    RegisterMethod,
    RiskLevel,
    VerificationStatus,
    Visibility,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class InvestmentPreferences:
    focus_markets: list[MarketInterest] = field(default_factory=list)
    risk_preference: RiskLevel = RiskLevel.C3


@dataclass
class AchievementStats:
    posts_count: int = 0
    featured_posts_count: int = 0
    influence_score: int = 0
    badges: list[AchievementBadge] = field(default_factory=list)


@dataclass
class PrivacySettings:
    nickname_visibility: Visibility = Visibility.PUBLIC
    avatar_visibility: Visibility = Visibility.PUBLIC
    bio_visibility: Visibility = Visibility.PUBLIC
    investment_preferences_visibility: Visibility = Visibility.FOLLOWERS
    achievements_visibility: Visibility = Visibility.PUBLIC


@dataclass
class UserProfile:
    nickname: str
    avatar_url: str | None = None
    bio: str | None = None
    experience_tags: list[str] = field(default_factory=list)
    investment_preferences: InvestmentPreferences = field(
        default_factory=InvestmentPreferences
    )
    achievements: AchievementStats = field(default_factory=AchievementStats)
    privacy_settings: PrivacySettings = field(default_factory=PrivacySettings)


@dataclass
class RealNameVerification:
    status: VerificationStatus = VerificationStatus.NOT_SUBMITTED
    legal_name: str | None = None
    id_number: str | None = None
    face_verified: bool = False
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None


@dataclass
class ProfessionalDocument:
    doc_type: ProfessionalDocType
    file_name: str
    file_url: str
    uploaded_at: datetime = field(default_factory=utc_now)


@dataclass
class ProfessionalVerification:
    status: VerificationStatus = VerificationStatus.NOT_SUBMITTED
    documents: list[ProfessionalDocument] = field(default_factory=list)
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None
    verified_by: str | None = None

    @property
    def has_v_badge(self) -> bool:
        return self.status == VerificationStatus.APPROVED


@dataclass
class SuitabilityAssessment:
    completed: bool = False
    risk_level: RiskLevel | None = None
    score: int = 0
    answers: dict[str, int] = field(default_factory=dict)
    submitted_at: datetime | None = None


@dataclass
class UserAuth:
    password_hash: str | None = None
    phone: str | None = None
    phone_verified: bool = False
    email: str | None = None
    email_verified: bool = False
    wechat_open_id: str | None = None
    weibo_open_id: str | None = None

    def basic_verified(self) -> bool:
        return self.phone_verified or self.email_verified


@dataclass
class User:
    id: str = field(default_factory=lambda: str(uuid4()))
    register_method: RegisterMethod = RegisterMethod.PHONE
    auth: UserAuth = field(default_factory=UserAuth)
    profile: UserProfile = field(default_factory=lambda: UserProfile(nickname="新用户"))
    real_name_verification: RealNameVerification = field(default_factory=RealNameVerification)
    professional_verification: ProfessionalVerification = field(
        default_factory=ProfessionalVerification
    )
    suitability_assessment: SuitabilityAssessment = field(
        default_factory=SuitabilityAssessment
    )
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()
