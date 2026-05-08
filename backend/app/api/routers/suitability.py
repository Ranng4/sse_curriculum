from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import (
    get_current_user_id_from_request,
    get_suitability_service,
    get_user_service,
)
from app.core.errors import ValidationError
from app.schemas.suitability import SubmitSuitabilityRequest

suitability_bp = Blueprint("suitability", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


@suitability_bp.get("/questionnaire")
def get_questionnaire():
    suitability_service = get_suitability_service()
    view = suitability_service.get_questionnaire()
    return _success(view.model_dump(mode="json"))


@suitability_bp.get("/result")
def get_result():
    user_service = get_user_service()
    user_id = get_current_user_id_from_request(request)
    view = user_service.get_suitability_result(user_id)
    return _success(view.model_dump(mode="json"))


@suitability_bp.post("/submit")
def submit_questionnaire():
    user_service = get_user_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = SubmitSuitabilityRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = user_service.submit_suitability_assessment(user_id, req.answers)
    return _success(view.model_dump(mode="json"))
