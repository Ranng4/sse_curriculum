from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import (
    get_content_service,
    get_current_user_id_from_request,
    get_optional_current_user_id_from_request,
)
from app.core.errors import ValidationError
from app.schemas.content import CommentCreateRequest, PostCreateRequest, PostUpdateRequest

content_bp = Blueprint("content", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


def _parse_limit(raw: str | None, default: int = 20, max_limit: int = 100) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValidationError("limit must be an integer") from exc
    if value <= 0:
        raise ValidationError("limit must be > 0")
    return min(value, max_limit)


def _parse_sort(raw: str | None) -> str:
    if raw is None or raw == "":
        return "latest"
    if raw not in {"latest", "hot"}:
        raise ValidationError("sort must be one of: latest, hot")
    return raw


def _parse_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@content_bp.post("/posts")
def create_post():
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = PostCreateRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = content_service.create_post(user_id, req)
    return _success(view.model_dump(mode="json"), 201)


@content_bp.patch("/posts/<post_id>")
def update_post(post_id: str):
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = PostUpdateRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = content_service.update_post(user_id, post_id, req)
    return _success(view.model_dump(mode="json"))


@content_bp.get("/posts")
def list_posts():
    content_service = get_content_service()
    viewer_user_id = get_optional_current_user_id_from_request(request)
    limit = _parse_limit(request.args.get("limit"), default=20)
    sort = _parse_sort(request.args.get("sort"))
    board_id = request.args.get("board_id")
    keyword = request.args.get("keyword")
    stock_code = request.args.get("stock_code")
    view = content_service.list_posts(
        viewer_user_id=viewer_user_id,
        board_id=board_id,
        keyword=keyword,
        stock_code=stock_code,
        sort=sort,
        limit=limit,
    )
    return _success([item.model_dump(mode="json") for item in view])


@content_bp.get("/posts/<post_id>")
def get_post(post_id: str):
    content_service = get_content_service()
    viewer_user_id = get_optional_current_user_id_from_request(request)
    view = content_service.get_post(post_id, viewer_user_id=viewer_user_id)
    return _success(view.model_dump(mode="json"))


@content_bp.post("/posts/<post_id>/comments")
def create_comment(post_id: str):
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = CommentCreateRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = content_service.create_comment(user_id, post_id, req)
    return _success(view.model_dump(mode="json"), 201)


@content_bp.get("/posts/<post_id>/comments")
def list_comments(post_id: str):
    content_service = get_content_service()
    view = content_service.list_comments(post_id)
    return _success([item.model_dump(mode="json") for item in view])


@content_bp.post("/posts/<post_id>/like")
def like_post(post_id: str):
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    view = content_service.set_like(user_id, post_id, enabled=True)
    return _success(view.model_dump(mode="json"))


@content_bp.delete("/posts/<post_id>/like")
def unlike_post(post_id: str):
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    view = content_service.set_like(user_id, post_id, enabled=False)
    return _success(view.model_dump(mode="json"))


@content_bp.post("/posts/<post_id>/favorite")
def favorite_post(post_id: str):
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    view = content_service.set_favorite(user_id, post_id, enabled=True)
    return _success(view.model_dump(mode="json"))


@content_bp.delete("/posts/<post_id>/favorite")
def unfavorite_post(post_id: str):
    content_service = get_content_service()
    user_id = get_current_user_id_from_request(request)
    view = content_service.set_favorite(user_id, post_id, enabled=False)
    return _success(view.model_dump(mode="json"))


@content_bp.get("/feed")
def list_feed():
    content_service = get_content_service()
    viewer_user_id = get_optional_current_user_id_from_request(request)
    following_only = _parse_bool(request.args.get("following_only"), default=False)
    limit = _parse_limit(request.args.get("limit"), default=20)
    view = content_service.list_feed(
        viewer_user_id=viewer_user_id,
        following_only=following_only,
        limit=limit,
    )
    return _success([item.model_dump(mode="json") for item in view])


@content_bp.get("/hot-rank")
def list_hot_rank():
    content_service = get_content_service()
    viewer_user_id = get_optional_current_user_id_from_request(request)
    limit = _parse_limit(request.args.get("limit"), default=20)
    view = content_service.list_hot_rank(viewer_user_id=viewer_user_id, limit=limit)
    return _success([item.model_dump(mode="json") for item in view])


@content_bp.get("/search/suggest")
def search_suggest():
    content_service = get_content_service()
    query = request.args.get("q", "")
    limit = _parse_limit(request.args.get("limit"), default=10, max_limit=30)
    view = content_service.search_suggestions(query=query, limit=limit)
    return _success(view.model_dump(mode="json"))
