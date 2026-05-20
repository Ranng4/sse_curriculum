from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api.deps import get_current_user_id_from_request, get_social_service

social_bp = Blueprint("social", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


@social_bp.post("/follows/<target_user_id>")
def follow_user(target_user_id: str):
    social_service = get_social_service()
    user_id = get_current_user_id_from_request(request)
    view = social_service.follow(user_id, target_user_id)
    return _success(view.model_dump(mode="json"))


@social_bp.delete("/follows/<target_user_id>")
def unfollow_user(target_user_id: str):
    social_service = get_social_service()
    user_id = get_current_user_id_from_request(request)
    view = social_service.unfollow(user_id, target_user_id)
    return _success(view.model_dump(mode="json"))


@social_bp.get("/follows/me")
def list_following():
    social_service = get_social_service()
    user_id = get_current_user_id_from_request(request)
    view = social_service.list_following(user_id)
    return _success([item.model_dump(mode="json") for item in view])


@social_bp.get("/fans/me")
def list_followers():
    social_service = get_social_service()
    user_id = get_current_user_id_from_request(request)
    view = social_service.list_followers(user_id)
    return _success([item.model_dump(mode="json") for item in view])


@social_bp.get("/stats/me")
def get_my_stats():
    social_service = get_social_service()
    user_id = get_current_user_id_from_request(request)
    view = social_service.get_stats(user_id)
    return _success(view.model_dump(mode="json"))
