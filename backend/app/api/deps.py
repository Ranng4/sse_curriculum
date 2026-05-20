from __future__ import annotations

from dataclasses import dataclass

from flask import Request

from app.core.errors import UnauthorizedError, UserSystemError
from app.repositories.content_repository import InMemoryContentRepository
from app.repositories.token_repository import InMemoryTokenRepository
from app.repositories.forum_repository import InMemoryForumBoardRepository
from app.repositories.social_repository import InMemorySocialRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.services.content_service import ContentService
from app.services.forum_service import ForumService
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.services.social_service import SocialService
from app.services.suitability_service import SuitabilityService
from app.services.user_service import UserService


@dataclass
class ServiceContainer:
    user_repository: InMemoryUserRepository
    token_repository: InMemoryTokenRepository
    forum_repository: InMemoryForumBoardRepository
    content_repository: InMemoryContentRepository
    social_repository: InMemorySocialRepository
    suitability_service: SuitabilityService
    forum_service: ForumService
    auth_service: AuthService
    profile_service: ProfileService
    user_service: UserService
    content_service: ContentService
    social_service: SocialService


def create_service_container() -> ServiceContainer:
    user_repository = InMemoryUserRepository()
    token_repository = InMemoryTokenRepository()
    forum_repository = InMemoryForumBoardRepository()
    content_repository = InMemoryContentRepository()
    social_repository = InMemorySocialRepository()
    suitability_service = SuitabilityService()
    forum_service = ForumService(board_repository=forum_repository)
    auth_service = AuthService(user_repository=user_repository, token_repository=token_repository)
    profile_service = ProfileService(user_repository=user_repository)
    user_service = UserService(
        user_repository=user_repository,
        suitability_service=suitability_service,
    )
    content_service = ContentService(
        content_repository=content_repository,
        user_repository=user_repository,
        forum_repository=forum_repository,
        social_repository=social_repository,
    )
    social_service = SocialService(
        social_repository=social_repository,
        user_repository=user_repository,
    )
    return ServiceContainer(
        user_repository=user_repository,
        token_repository=token_repository,
        forum_repository=forum_repository,
        content_repository=content_repository,
        social_repository=social_repository,
        suitability_service=suitability_service,
        forum_service=forum_service,
        auth_service=auth_service,
        profile_service=profile_service,
        user_service=user_service,
        content_service=content_service,
        social_service=social_service,
    )


CONTAINER = create_service_container()


def get_auth_service() -> AuthService:
    return CONTAINER.auth_service


def get_profile_service() -> ProfileService:
    return CONTAINER.profile_service


def get_user_service() -> UserService:
    return CONTAINER.user_service


def get_suitability_service() -> SuitabilityService:
    return CONTAINER.suitability_service


def get_forum_service() -> ForumService:
    return CONTAINER.forum_service


def get_content_service() -> ContentService:
    return CONTAINER.content_service


def get_social_service() -> SocialService:
    return CONTAINER.social_service


def _extract_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return None
    prefix = "Bearer "
    if not auth_header.startswith(prefix):
        return None
    token = auth_header[len(prefix) :].strip()
    return token or None


def get_current_user_id_from_request(request: Request) -> str:
    token = _extract_bearer_token(request)
    if token is None:
        raise UnauthorizedError("missing or invalid Authorization header")

    try:
        user = CONTAINER.auth_service.get_user_by_token(token)
    except UserSystemError as exc:
        raise UnauthorizedError(str(exc)) from exc
    return user.id


def get_optional_current_user_id_from_request(request: Request) -> str | None:
    token = _extract_bearer_token(request)
    if token is None:
        return None
    try:
        user = CONTAINER.auth_service.get_user_by_token(token)
    except UserSystemError:
        return None
    return user.id
