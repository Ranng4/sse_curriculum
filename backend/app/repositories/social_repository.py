from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


class InMemorySocialRepository:
    def __init__(self) -> None:
        self._following: dict[str, set[str]] = {}
        self._followers: dict[str, set[str]] = {}
        self._followed_at: dict[tuple[str, str], datetime] = {}

    def follow(self, follower_id: str, followee_id: str) -> datetime:
        self._following.setdefault(follower_id, set()).add(followee_id)
        self._followers.setdefault(followee_id, set()).add(follower_id)
        followed_at = self._followed_at.get((follower_id, followee_id), utc_now())
        self._followed_at[(follower_id, followee_id)] = followed_at
        return followed_at

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        self._following.setdefault(follower_id, set()).discard(followee_id)
        self._followers.setdefault(followee_id, set()).discard(follower_id)
        self._followed_at.pop((follower_id, followee_id), None)

    def is_following(self, follower_id: str, followee_id: str) -> bool:
        return followee_id in self._following.get(follower_id, set())

    def list_following(self, follower_id: str) -> list[tuple[str, datetime]]:
        followees = self._following.get(follower_id, set())
        pairs = [
            (followee_id, self._followed_at.get((follower_id, followee_id), utc_now()))
            for followee_id in followees
        ]
        pairs.sort(key=lambda item: item[1], reverse=True)
        return pairs

    def list_followers(self, followee_id: str) -> list[tuple[str, datetime]]:
        followers = self._followers.get(followee_id, set())
        pairs = [
            (follower_id, self._followed_at.get((follower_id, followee_id), utc_now()))
            for follower_id in followers
        ]
        pairs.sort(key=lambda item: item[1], reverse=True)
        return pairs

    def following_count(self, follower_id: str) -> int:
        return len(self._following.get(follower_id, set()))

    def follower_count(self, followee_id: str) -> int:
        return len(self._followers.get(followee_id, set()))
