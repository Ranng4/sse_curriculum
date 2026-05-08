from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import (
    get_current_user_id_from_request,
    get_optional_current_user_id_from_request,
    get_profile_service,
)
from app.core.errors import ValidationError
from app.schemas.profile import (
    UpdateBasicProfileRequest,
    UpdateInvestmentPreferencesRequest,
    UpdatePrivacySettingsRequest,
)

profile_bp = Blueprint("profile", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


@profile_bp.get("/me")
def get_my_profile():
    profile_service = get_profile_service()
    user_id = get_current_user_id_from_request(request)
    view = profile_service.get_profile(user_id)
    return _success(view.model_dump(mode="json"))


@profile_bp.patch("/basic")
def update_basic_profile():
    profile_service = get_profile_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = UpdateBasicProfileRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = profile_service.update_basic_profile(user_id, req)
    return _success(view.model_dump(mode="json"))


@profile_bp.patch("/investment-preferences")
def update_investment_preferences():
    profile_service = get_profile_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = UpdateInvestmentPreferencesRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = profile_service.update_investment_preferences(user_id, req)
    return _success(view.model_dump(mode="json"))


@profile_bp.patch("/privacy-settings")
def update_privacy_settings():
    profile_service = get_profile_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = UpdatePrivacySettingsRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = profile_service.update_privacy_settings(user_id, req)
    return _success(view.model_dump(mode="json"))


@profile_bp.get("/<target_user_id>")
def get_public_profile(target_user_id: str):
    profile_service = get_profile_service()
    viewer_user_id = get_optional_current_user_id_from_request(request)
    view = profile_service.get_public_profile(target_user_id, viewer_user_id)
    return _success(view.model_dump(mode="json"))
