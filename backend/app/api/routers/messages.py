"""Message API routes — private messaging.

AI-generated: Blueprint with send, list conversations, get conversation, unread count.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import get_current_user_id_from_request, get_message_service
from app.core.errors import ValidationError
from app.schemas.message import SendMessageRequest

messages_bp = Blueprint("messages", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


def _parse_limit(raw: str | None, default: int = 50, max_limit: int = 100) -> int:
    if raw is None:
        return default
    try:
        v = int(raw)
    except ValueError:
        raise ValidationError("limit must be integer")
    return min(max(v, 1), max_limit)


# ── Send message ──


@messages_bp.post("/messages")
def send_message():
    """Send a private message to another user."""
    service = get_message_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = SendMessageRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = service.send(user_id, req)
    return _success(view.model_dump(mode="json"), 201)


# ── List conversations ──


@messages_bp.get("/messages/conversations")
def list_conversations():
    """List all conversation partners with last message preview."""
    service = get_message_service()
    user_id = get_current_user_id_from_request(request)
    view = service.list_conversations(user_id)
    return _success([v.model_dump(mode="json") for v in view])


# ── Get conversation with specific user ──


@messages_bp.get("/messages/conversations/<partner_id>")
def get_conversation(partner_id: str):
    """Get message history with a specific user (marks as read)."""
    service = get_message_service()
    user_id = get_current_user_id_from_request(request)
    limit = _parse_limit(request.args.get("limit"), default=50)
    view = service.get_conversation(user_id, partner_id, limit=limit)
    return _success([v.model_dump(mode="json") for v in view])


# ── Unread count ──


@messages_bp.get("/messages/unread-count")
def get_unread_count():
    """Get total unread message count."""
    service = get_message_service()
    user_id = get_current_user_id_from_request(request)
    view = service.get_unread_count(user_id)
    return _success(view.model_dump(mode="json"))
