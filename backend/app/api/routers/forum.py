from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import get_forum_service
from app.core.errors import ValidationError
from app.models.forum import ForumBoardCategory
from app.schemas.forum import ForumBoardCreateRequest, ForumBoardUpdateRequest

forum_bp = Blueprint("forum", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


def _parse_category(value: str | None) -> ForumBoardCategory | None:
    if value is None or value == "":
        return None
    try:
        return ForumBoardCategory(value)
    except ValueError as exc:
        raise ValidationError("invalid category") from exc


@forum_bp.get("/sections")
def list_sections():
    forum_service = get_forum_service()
    view = forum_service.list_sections()
    return _success([item.model_dump(mode="json") for item in view])


def _section_response(category: ForumBoardCategory):
    forum_service = get_forum_service()
    section = forum_service.get_section(category)
    return _success(section.model_dump(mode="json"))


@forum_bp.get("/markets")
def market_section():
    return _section_response(ForumBoardCategory.MARKET)


@forum_bp.get("/topics")
def topic_section():
    return _section_response(ForumBoardCategory.TOPIC)


@forum_bp.get("/company-research")
def company_research_section():
    return _section_response(ForumBoardCategory.COMPANY_RESEARCH)


@forum_bp.get("/qa")
def qa_section():
    return _section_response(ForumBoardCategory.QA)


@forum_bp.get("/sections/<category>")
def get_section(category: str):
    parsed_category = _parse_category(category)
    if parsed_category is None:
        raise ValidationError("invalid category")
    return _section_response(parsed_category)


@forum_bp.get("/boards")
def list_boards():
    forum_service = get_forum_service()
    category = _parse_category(request.args.get("category"))
    market = request.args.get("market")
    active_only = request.args.get("active_only")
    if active_only is None:
        active = None
    else:
        active = active_only.lower() in {"1", "true", "yes", "on"}
    view = forum_service.list_boards(category=category, market=market, active_only=active)
    return _success([item.model_dump(mode="json") for item in view])


@forum_bp.get("/boards/<board_id>")
def get_board(board_id: str):
    forum_service = get_forum_service()
    view = forum_service.get_board(board_id)
    return _success(view.model_dump(mode="json"))


@forum_bp.post("/boards")
def create_board():
    forum_service = get_forum_service()
    payload = request.get_json(silent=True) or {}
    try:
        req = ForumBoardCreateRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = forum_service.create_board(req)
    return _success(view.model_dump(mode="json"), 201)


@forum_bp.patch("/boards/<board_id>")
def update_board(board_id: str):
    forum_service = get_forum_service()
    payload = request.get_json(silent=True) or {}
    try:
        req = ForumBoardUpdateRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc
    view = forum_service.update_board(board_id, req)
    return _success(view.model_dump(mode="json"))


@forum_bp.delete("/boards/<board_id>")
def delete_board(board_id: str):
    forum_service = get_forum_service()
    forum_service.delete_board(board_id)
    return _success(None)
