from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AchievementBadge, MarketInterest, ProfileField, RiskLevel, Visibility


class InvestmentPreferencesView(BaseModel):
    focus_markets: list[MarketInterest] = Field(default_factory=list)
    risk_preference: RiskLevel = RiskLevel.C3

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class AchievementStatsView(BaseModel):
    posts_count: int = 0
    featured_posts_count: int = 0
    influence_score: int = 0
    badges: list[AchievementBadge] = Field(default_factory=list)

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class PrivacySettingsView(BaseModel):
    nickname_visibility: Visibility = Visibility.PUBLIC
    avatar_visibility: Visibility = Visibility.PUBLIC
    bio_visibility: Visibility = Visibility.PUBLIC
    investment_preferences_visibility: Visibility = Visibility.FOLLOWERS
    achievements_visibility: Visibility = Visibility.PUBLIC

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class UserProfileView(BaseModel):
    user_id: str
    nickname: str
    avatar_url: str | None = None
    bio: str | None = None
    experience_tags: list[str] = Field(default_factory=list)
    investment_preferences: InvestmentPreferencesView
    achievements: AchievementStatsView
    privacy_settings: PrivacySettingsView
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class UpdateBasicProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=32)
    avatar_url: str | None = Field(default=None, max_length=512)
    bio: str | None = Field(default=None, max_length=500)
    experience_tags: list[str] | None = Field(default=None, max_length=20)


class UpdateInvestmentPreferencesRequest(BaseModel):
    focus_markets: list[MarketInterest] | None = Field(default=None, max_length=10)
    risk_preference: RiskLevel | None = None

    model_config = ConfigDict(use_enum_values=True)


class UpdatePrivacySettingsRequest(BaseModel):
    nickname_visibility: Visibility | None = None
    avatar_visibility: Visibility | None = None
    bio_visibility: Visibility | None = None
    investment_preferences_visibility: Visibility | None = None
    achievements_visibility: Visibility | None = None

    model_config = ConfigDict(use_enum_values=True)


class PublicProfileView(BaseModel):
    user_id: str
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    experience_tags: list[str] | None = None
    investment_preferences: InvestmentPreferencesView | None = None
    achievements: AchievementStatsView | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class ProfileVisibilityRule(BaseModel):
    field: ProfileField
    visibility: Visibility

    model_config = ConfigDict(use_enum_values=True)
