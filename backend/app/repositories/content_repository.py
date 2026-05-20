from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime

from app.core.errors import NotFoundError
from app.models.content import Comment, Post


class InMemoryContentRepository:
    def __init__(self) -> None:
        self._posts: dict[str, Post] = {}
        self._comments: dict[str, Comment] = {}
        self._post_comment_ids: dict[str, list[str]] = {}
        self._post_likes: dict[str, set[str]] = {}
        self._post_favorites: dict[str, set[str]] = {}

    def create_post(self, post: Post) -> Post:
        self._posts[post.id] = deepcopy(post)
        self._post_comment_ids[post.id] = []
        self._post_likes[post.id] = set()
        self._post_favorites[post.id] = set()
        return deepcopy(post)

    def save_post(self, post: Post) -> Post:
        if post.id not in self._posts:
            raise NotFoundError("post not found")
        self._posts[post.id] = deepcopy(post)
        return deepcopy(post)

    def get_post(self, post_id: str) -> Post:
        post = self._posts.get(post_id)
        if post is None:
            raise NotFoundError("post not found")
        return deepcopy(post)

    def list_posts(self) -> list[Post]:
        return [deepcopy(post) for post in self._posts.values()]

    def create_comment(self, comment: Comment) -> Comment:
        if comment.post_id not in self._posts:
            raise NotFoundError("post not found")
        self._comments[comment.id] = deepcopy(comment)
        self._post_comment_ids.setdefault(comment.post_id, []).append(comment.id)
        return deepcopy(comment)

    def get_comment(self, comment_id: str) -> Comment:
        comment = self._comments.get(comment_id)
        if comment is None:
            raise NotFoundError("comment not found")
        return deepcopy(comment)

    def list_comments(self, post_id: str) -> list[Comment]:
        if post_id not in self._posts:
            raise NotFoundError("post not found")
        ids = self._post_comment_ids.get(post_id, [])
        return [deepcopy(self._comments[item]) for item in ids if item in self._comments]

    def set_like(self, post_id: str, user_id: str, enabled: bool) -> int:
        self.get_post(post_id)
        likes = self._post_likes.setdefault(post_id, set())
        if enabled:
            likes.add(user_id)
        else:
            likes.discard(user_id)
        return len(likes)

    def set_favorite(self, post_id: str, user_id: str, enabled: bool) -> int:
        self.get_post(post_id)
        favorites = self._post_favorites.setdefault(post_id, set())
        if enabled:
            favorites.add(user_id)
        else:
            favorites.discard(user_id)
        return len(favorites)

    def is_liked(self, post_id: str, user_id: str) -> bool:
        return user_id in self._post_likes.get(post_id, set())

    def is_favorited(self, post_id: str, user_id: str) -> bool:
        return user_id in self._post_favorites.get(post_id, set())

    def like_count(self, post_id: str) -> int:
        return len(self._post_likes.get(post_id, set()))

    def favorite_count(self, post_id: str) -> int:
        return len(self._post_favorites.get(post_id, set()))

    def comment_count(self, post_id: str) -> int:
        return len(self._post_comment_ids.get(post_id, []))

    def engagement_score(self, post_id: str) -> int:
        return (
            self.like_count(post_id) * 2
            + self.favorite_count(post_id) * 3
            + self.comment_count(post_id)
        )

    def list_hot_posts(self, limit: int = 20, days: int = 7) -> list[Post]:
        now = datetime.now(UTC)
        candidates = [
            post
            for post in self._posts.values()
            if (now - post.created_at).days <= days
        ]
        candidates.sort(
            key=lambda post: (
                self.engagement_score(post.id),
                post.created_at,
            ),
            reverse=True,
        )
        return [deepcopy(post) for post in candidates[:limit]]
