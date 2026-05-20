from __future__ import annotations

from app.core.errors import ValidationError
from app.repositories.social_repository import InMemorySocialRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.social import FollowActionResultView, FollowStatsView, FollowUserView


class SocialService:
    def __init__(
        self,
        social_repository: InMemorySocialRepository,
        user_repository: InMemoryUserRepository,
    ) -> None:
        self.social_repository = social_repository
        self.user_repository = user_repository

    def follow(self, follower_id: str, followee_id: str) -> FollowActionResultView:
        self._validate_follow(follower_id, followee_id)
        self.user_repository.get(follower_id)
        self.user_repository.get(followee_id)

        self.social_repository.follow(follower_id, followee_id)
        return self._action_result(follower_id, followee_id)

    def unfollow(self, follower_id: str, followee_id: str) -> FollowActionResultView:
        self._validate_follow(follower_id, followee_id)
        self.user_repository.get(follower_id)
        self.user_repository.get(followee_id)

        self.social_repository.unfollow(follower_id, followee_id)
        return self._action_result(follower_id, followee_id)

    def list_following(self, follower_id: str) -> list[FollowUserView]:
        self.user_repository.get(follower_id)
        pairs = self.social_repository.list_following(follower_id)
        result: list[FollowUserView] = []
        for followee_id, followed_at in pairs:
            user = self.user_repository.get(followee_id)
            result.append(
                FollowUserView(
                    user_id=followee_id,
                    nickname=user.profile.nickname,
                    followed_at=followed_at,
                )
            )
        return result

    def list_followers(self, followee_id: str) -> list[FollowUserView]:
        self.user_repository.get(followee_id)
        pairs = self.social_repository.list_followers(followee_id)
        result: list[FollowUserView] = []
        for follower_id, followed_at in pairs:
            user = self.user_repository.get(follower_id)
            result.append(
                FollowUserView(
                    user_id=follower_id,
                    nickname=user.profile.nickname,
                    followed_at=followed_at,
                )
            )
        return result

    def get_stats(self, user_id: str) -> FollowStatsView:
        self.user_repository.get(user_id)
        return FollowStatsView(
            user_id=user_id,
            following_count=self.social_repository.following_count(user_id),
            follower_count=self.social_repository.follower_count(user_id),
        )

    def _validate_follow(self, follower_id: str, followee_id: str) -> None:
        if follower_id == followee_id:
            raise ValidationError("cannot follow yourself")

    def _action_result(self, follower_id: str, followee_id: str) -> FollowActionResultView:
        return FollowActionResultView(
            target_user_id=followee_id,
            is_following=self.social_repository.is_following(follower_id, followee_id),
            following_count=self.social_repository.following_count(follower_id),
            follower_count_of_target=self.social_repository.follower_count(followee_id),
        )
