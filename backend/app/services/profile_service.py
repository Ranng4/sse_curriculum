from __future__ import annotations

from app.core.enums import Visibility
from app.models.user import User
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.profile import (
    PublicProfileView,
    UpdateBasicProfileRequest,
    UpdateInvestmentPreferencesRequest,
    UpdatePrivacySettingsRequest,
    UserProfileView,
)


class ProfileService:
    def __init__(self, user_repository: InMemoryUserRepository) -> None:
        self.user_repository = user_repository

    def get_profile(self, user_id: str) -> UserProfileView:
        user = self.user_repository.get(user_id)
        return self._to_profile_view(user)

    def update_basic_profile(
        self,
        user_id: str,
        request: UpdateBasicProfileRequest,
    ) -> UserProfileView:
        user = self.user_repository.get(user_id)
        profile = user.profile

        if request.nickname is not None:
            profile.nickname = request.nickname
        if request.avatar_url is not None:
            profile.avatar_url = request.avatar_url
        if request.bio is not None:
            profile.bio = request.bio
        if request.experience_tags is not None:
            profile.experience_tags = request.experience_tags

        user.touch()
        saved = self.user_repository.save(user)
        return self._to_profile_view(saved)

    def update_investment_preferences(
        self,
        user_id: str,
        request: UpdateInvestmentPreferencesRequest,
    ) -> UserProfileView:
        user = self.user_repository.get(user_id)
        prefs = user.profile.investment_preferences

        if request.focus_markets is not None:
            prefs.focus_markets = request.focus_markets
        if request.risk_preference is not None:
            prefs.risk_preference = request.risk_preference

        user.touch()
        saved = self.user_repository.save(user)
        return self._to_profile_view(saved)

    def update_privacy_settings(
        self,
        user_id: str,
        request: UpdatePrivacySettingsRequest,
    ) -> UserProfileView:
        user = self.user_repository.get(user_id)
        privacy = user.profile.privacy_settings

        if request.nickname_visibility is not None:
            privacy.nickname_visibility = request.nickname_visibility
        if request.avatar_visibility is not None:
            privacy.avatar_visibility = request.avatar_visibility
        if request.bio_visibility is not None:
            privacy.bio_visibility = request.bio_visibility
        if request.investment_preferences_visibility is not None:
            privacy.investment_preferences_visibility = (
                request.investment_preferences_visibility
            )
        if request.achievements_visibility is not None:
            privacy.achievements_visibility = request.achievements_visibility

        user.touch()
        saved = self.user_repository.save(user)
        return self._to_profile_view(saved)

    def get_public_profile(self, target_user_id: str, viewer_user_id: str | None) -> PublicProfileView:
        user = self.user_repository.get(target_user_id)
        privacy = user.profile.privacy_settings
        profile = user.profile

        # Future extension point: follower relationship check.
        is_self_view = viewer_user_id == target_user_id
        viewer_is_follower = False

        def can_view(visibility: Visibility) -> bool:
            if is_self_view:
                return True
            if visibility == Visibility.PUBLIC:
                return True
            if visibility == Visibility.FOLLOWERS:
                return viewer_is_follower
            return False

        return PublicProfileView(
            user_id=user.id,
            nickname=profile.nickname if can_view(privacy.nickname_visibility) else None,
            avatar_url=profile.avatar_url if can_view(privacy.avatar_visibility) else None,
            bio=profile.bio if can_view(privacy.bio_visibility) else None,
            experience_tags=profile.experience_tags if can_view(privacy.bio_visibility) else None,
            investment_preferences=(
                profile.investment_preferences
                if can_view(privacy.investment_preferences_visibility)
                else None
            ),
            achievements=(
                profile.achievements if can_view(privacy.achievements_visibility) else None
            ),
        )

    @staticmethod
    def _to_profile_view(user: User) -> UserProfileView:
        profile = user.profile
        return UserProfileView(
            user_id=user.id,
            nickname=profile.nickname,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            experience_tags=profile.experience_tags,
            investment_preferences=profile.investment_preferences,
            achievements=profile.achievements,
            privacy_settings=profile.privacy_settings,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
