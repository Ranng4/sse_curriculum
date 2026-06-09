"""Admin management API — content review, user management, analytics.

AI-generated: admin blueprint with moderation and statistics endpoints.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import get_admin_service, get_current_user_id_from_request
from app.core.errors import ValidationError
from app.schemas.admin import (
    AdminStatsView,
    PostReviewRequest,
    UserManageRequest,
)

admin_bp = Blueprint("admin", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


def _parse_int(value, default=20, max_val=100):
    if value is None:
        return default
    try:
        v = int(value)
    except ValueError:
        raise ValidationError("param must be integer")
    return min(max(v, 1), max_val)


# ── Dashboard / Stats ──


@admin_bp.get("/stats")
def get_stats():
    """Get forum-wide analytics: total users, posts, comments, activity."""
    service = get_admin_service()
    stats = service.get_stats()
    return _success(stats.model_dump(mode="json"))


# ── Content Review ──


@admin_bp.get("/posts")
def list_posts_for_review():
    """List all posts with optional status filter for moderation queue."""
    service = get_admin_service()
    status = request.args.get("status")          # all / pending / flagged
    limit = _parse_int(request.args.get("limit"), default=20)
    offset = _parse_int(request.args.get("offset"), default=0, max_val=10000)
    posts = service.list_posts_for_review(status=status, limit=limit, offset=offset)
    return _success([p.model_dump(mode="json") for p in posts])


@admin_bp.patch("/posts/<post_id>")
def review_post(post_id: str):
    """Approve, reject, or flag a post for moderation."""
    service = get_admin_service()
    reviewer_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = PostReviewRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = service.review_post(post_id, reviewer_id, req)
    return _success(view.model_dump(mode="json"))


# ── User Management ──


@admin_bp.get("/users")
def list_users():
    """List all users with optional status/role filters."""
    service = get_admin_service()
    status = request.args.get("status")           # active / warned / muted / banned
    keyword = request.args.get("keyword")
    limit = _parse_int(request.args.get("limit"), default=20)
    offset = _parse_int(request.args.get("offset"), default=0, max_val=10000)
    users = service.list_users(status=status, keyword=keyword, limit=limit, offset=offset)
    return _success([u.model_dump(mode="json") for u in users])


@admin_bp.patch("/users/<user_id>")
def manage_user(user_id: str):
    """Warn, mute, or ban a user."""
    service = get_admin_service()
    admin_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = UserManageRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = service.manage_user(user_id, admin_id, req)
    return _success(view.model_dump(mode="json"))
