from __future__ import annotations

from enum import Enum, StrEnum


class RegisterMethod(StrEnum):
    PHONE = "phone"
    EMAIL = "email"
    WECHAT = "wechat"
    WEIBO = "weibo"


class RiskLevel(StrEnum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"


class Visibility(StrEnum):
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"


class MarketInterest(StrEnum):
    A_SHARE = "a_share"
    HK_STOCK = "hk_stock"
    US_STOCK = "us_stock"
    FUND = "fund"
    BOND = "bond"
    FUTURE = "future"


class VerificationStatus(StrEnum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProfessionalDocType(StrEnum):
    PRACTITIONER_CERT = "practitioner_cert"
    DEGREE_CERT = "degree_cert"
    OTHER = "other"


class AchievementBadge(StrEnum):
    SHARP_ANALYST = "sharp_analyst"
    VALUE_HUNTER = "value_hunter"
    HOT_AUTHOR = "hot_author"
    COMMUNITY_MENTOR = "community_mentor"


class ProfileField(str, Enum):
    NICKNAME = "nickname"
    AVATAR_URL = "avatar_url"
    BIO = "bio"
    EXPERIENCE_TAGS = "experience_tags"
    INVESTMENT_PREFERENCES = "investment_preferences"
    ACHIEVEMENTS = "achievements"
