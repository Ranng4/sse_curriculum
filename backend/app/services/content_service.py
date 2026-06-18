from __future__ import annotations

from app.core.errors import UnauthorizedError, ValidationError
from app.models.content import Comment, Post
from app.services.content_filter import content_filter
from app.repositories.content_repository import InMemoryContentRepository
from app.repositories.forum_repository import InMemoryForumBoardRepository
from app.repositories.social_repository import InMemorySocialRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.content import (
    AuthorView,
    CommentCreateRequest,
    CommentView,
    PostCreateRequest,
    PostMetricsView,
    PostUpdateRequest,
    PostView,
    SearchSuggestView,
)


class ContentService:
    def __init__(
        self,
        content_repository: InMemoryContentRepository,
        user_repository: InMemoryUserRepository,
        forum_repository: InMemoryForumBoardRepository,
        social_repository: InMemorySocialRepository,
    ) -> None:
        self.content_repository = content_repository
        self.user_repository = user_repository
        self.forum_repository = forum_repository
        self.social_repository = social_repository
        self._default_suggestions = [
            "600519",
            "000001",
            "510300",
            "A股",
            "港股",
            "美股",
            "基金",
            "量化",
            "价值投资",
        ]

    def create_post(self, user_id: str, request: PostCreateRequest) -> PostView:
        # Content moderation: check sensitive words
        full_text = f"{request.title} {request.content}"
        check = content_filter.check(full_text)
        if not check.passed:
            raise ValidationError(content_filter.get_violation_message(check))

        self.user_repository.get(user_id)
        board = self.forum_repository.get(request.board_id)
        if not board.is_active:
            raise ValidationError("board is inactive")

        post = Post(
            author_id=user_id,
            board_id=request.board_id,
            title=request.title,
            content=request.content,
            post_type=request.post_type,
            stock_codes=request.stock_codes,
            image_urls=request.image_urls,
        )
        saved = self.content_repository.create_post(post)
        return self._to_post_view(saved, viewer_user_id=user_id)

    def update_post(self, user_id: str, post_id: str, request: PostUpdateRequest) -> PostView:
        post = self.content_repository.get_post(post_id)
        if post.author_id != user_id:
            raise UnauthorizedError("cannot edit post of other user")

        if request.title is not None:
            post.title = request.title
        if request.content is not None:
            post.content = request.content
        if request.post_type is not None:
            post.post_type = request.post_type
        if request.stock_codes is not None:
            post.stock_codes = request.stock_codes
        if request.image_urls is not None:
            post.image_urls = request.image_urls

        post.touch()
        saved = self.content_repository.save_post(post)
        return self._to_post_view(saved, viewer_user_id=user_id)

    def get_post(self, post_id: str, viewer_user_id: str | None = None) -> PostView:
        post = self.content_repository.get_post(post_id)
        return self._to_post_view(post, viewer_user_id=viewer_user_id)

    def list_posts(
        self,
        viewer_user_id: str | None = None,
        board_id: str | None = None,
        keyword: str | None = None,
        stock_code: str | None = None,
        sort: str = "latest",
        limit: int = 20,
    ) -> list[PostView]:
        posts = self.content_repository.list_posts()

        if board_id:
            posts = [post for post in posts if post.board_id == board_id]

        if keyword:
            normalized = keyword.strip().lower()
            posts = [
                post
                for post in posts
                if normalized in post.title.lower() or normalized in post.content.lower()
            ]

        if stock_code:
            normalized_code = stock_code.strip().upper()
            posts = [
                post for post in posts if normalized_code in {item.upper() for item in post.stock_codes}
            ]

        if sort == "hot":
            posts.sort(
                key=lambda item: (
                    self.content_repository.engagement_score(item.id),
                    item.created_at,
                ),
                reverse=True,
            )
        else:
            posts.sort(key=lambda item: item.created_at, reverse=True)

        limited = posts[:limit]
        return [self._to_post_view(post, viewer_user_id=viewer_user_id) for post in limited]

    def list_feed(
        self,
        viewer_user_id: str | None = None,
        following_only: bool = False,
        limit: int = 20,
    ) -> list[PostView]:
        posts = self.content_repository.list_posts()

        if following_only:
            if viewer_user_id is None:
                raise UnauthorizedError("login required for following feed")
            following = {item[0] for item in self.social_repository.list_following(viewer_user_id)}
            following.add(viewer_user_id)
            posts = [post for post in posts if post.author_id in following]

        posts.sort(key=lambda item: item.created_at, reverse=True)
        return [self._to_post_view(post, viewer_user_id=viewer_user_id) for post in posts[:limit]]

    def list_hot_rank(self, viewer_user_id: str | None = None, limit: int = 20) -> list[PostView]:
        posts = self.content_repository.list_hot_posts(limit=limit)
        return [self._to_post_view(post, viewer_user_id=viewer_user_id) for post in posts]

    def create_comment(
        self,
        user_id: str,
        post_id: str,
        request: CommentCreateRequest,
    ) -> CommentView:
        # Content moderation: check sensitive words
        check = content_filter.check(request.content)
        if not check.passed:
            raise ValidationError(content_filter.get_violation_message(check))

        self.user_repository.get(user_id)
        self.content_repository.get_post(post_id)
        if request.parent_comment_id:
            parent = self.content_repository.get_comment(request.parent_comment_id)
            if parent.post_id != post_id:
                raise ValidationError("parent comment does not belong to the post")

        comment = Comment(
            post_id=post_id,
            author_id=user_id,
            content=request.content,
            parent_comment_id=request.parent_comment_id,
        )
        saved = self.content_repository.create_comment(comment)
        return self._to_comment_view(saved)

    def list_comments(self, post_id: str) -> list[CommentView]:
        comments = self.content_repository.list_comments(post_id)
        comments.sort(key=lambda item: item.created_at)
        return [self._to_comment_view(item) for item in comments]

    def set_like(self, user_id: str, post_id: str, enabled: bool) -> PostMetricsView:
        self.user_repository.get(user_id)
        self.content_repository.get_post(post_id)
        self.content_repository.set_like(post_id, user_id, enabled)
        return self._metrics(post_id)

    def set_favorite(self, user_id: str, post_id: str, enabled: bool) -> PostMetricsView:
        self.user_repository.get(user_id)
        self.content_repository.get_post(post_id)
        self.content_repository.set_favorite(post_id, user_id, enabled)
        return self._metrics(post_id)

    def search_suggestions(self, query: str, limit: int = 10) -> SearchSuggestView:
        normalized = query.strip().lower()
        if not normalized:
            return SearchSuggestView(query=query, suggestions=[])

        dynamic_terms: set[str] = set(self._default_suggestions)
        for post in self.content_repository.list_posts():
            dynamic_terms.update(post.stock_codes)
            dynamic_terms.add(post.title)
        for board in self.forum_repository.list():
            dynamic_terms.add(board.name)

        matched = [term for term in dynamic_terms if normalized in term.lower()]
        matched.sort()
        return SearchSuggestView(query=query, suggestions=matched[:limit])

    def _to_post_view(self, post: Post, viewer_user_id: str | None = None) -> PostView:
        author = self._author_view(post.author_id)
        board = self.forum_repository.get(post.board_id)
        metrics = self._metrics(post.id)
        liked = False
        favorited = False
        if viewer_user_id:
            liked = self.content_repository.is_liked(post.id, viewer_user_id)
            favorited = self.content_repository.is_favorited(post.id, viewer_user_id)

        return PostView(
            id=post.id,
            board_id=post.board_id,
            board_name=board.name,
            title=post.title,
            content=post.content,
            post_type=post.post_type,
            stock_codes=post.stock_codes,
            image_urls=post.image_urls,
            author=author,
            created_at=post.created_at,
            updated_at=post.updated_at,
            metrics=metrics,
            liked_by_me=liked,
            favorited_by_me=favorited,
        )

    def _to_comment_view(self, comment: Comment) -> CommentView:
        return CommentView(
            id=comment.id,
            post_id=comment.post_id,
            author=self._author_view(comment.author_id),
            content=comment.content,
            parent_comment_id=comment.parent_comment_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    def _metrics(self, post_id: str) -> PostMetricsView:
        like_count = self.content_repository.like_count(post_id)
        favorite_count = self.content_repository.favorite_count(post_id)
        comment_count = self.content_repository.comment_count(post_id)
        return PostMetricsView(
            like_count=like_count,
            favorite_count=favorite_count,
            comment_count=comment_count,
            engagement_score=like_count * 2 + favorite_count * 3 + comment_count,
        )

    def _author_view(self, user_id: str) -> AuthorView:
        user = self.user_repository.get(user_id)
        return AuthorView(user_id=user.id, nickname=user.profile.nickname)
