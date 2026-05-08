from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import get_auth_service, get_current_user_id_from_request
from app.core.errors import ValidationError
from app.schemas.auth import (
    LoginRequest,
    RegisterByEmailRequest,
    RegisterByPhoneRequest,
    RegisterByThirdPartyRequest,
    SubmitProfessionalVerificationRequest,
    SubmitRealNameVerificationRequest,
    VerifyBasicRequest,
)

auth_bp = Blueprint("auth", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"code": 0, "message": "ok", "data": data}), status_code


def _parse_register_request(payload: dict):
    method = payload.get("method")
    if method == "phone":
        return RegisterByPhoneRequest(**payload)
    if method == "email":
        return RegisterByEmailRequest(**payload)
    if method in {"wechat", "weibo"}:
        return RegisterByThirdPartyRequest(**payload)
    raise ValidationError("method must be one of: phone, email, wechat, weibo")


@auth_bp.post("/register")
def register():
    auth_service = get_auth_service()
    payload = request.get_json(silent=True) or {}
    try:
        req = _parse_register_request(payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    user, token = auth_service.register(req)
    return _success(
        {
            "user_id": user.id,
            "token": token.model_dump(mode="json"),
        },
        201,
    )


@auth_bp.post("/login")
def login():
    auth_service = get_auth_service()
    payload = request.get_json(silent=True) or {}
    try:
        req = LoginRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    token = auth_service.login(req)
    return _success(token.model_dump(mode="json"))


@auth_bp.get("/basic-verification")
def get_basic_verification():
    auth_service = get_auth_service()
    user_id = get_current_user_id_from_request(request)
    view = auth_service.get_auth_view(user_id)
    return _success(view.model_dump(mode="json"))


@auth_bp.post("/basic-verification")
def verify_basic():
    auth_service = get_auth_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = VerifyBasicRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = auth_service.verify_basic(user_id, req)
    return _success(view.model_dump(mode="json"))


@auth_bp.get("/real-name-verification")
def get_real_name_verification():
    auth_service = get_auth_service()
    user_id = get_current_user_id_from_request(request)
    view = auth_service.get_real_name_view(user_id)
    return _success(view.model_dump(mode="json"))


@auth_bp.post("/real-name-verification")
def submit_real_name_verification():
    auth_service = get_auth_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = SubmitRealNameVerificationRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = auth_service.submit_real_name_verification(user_id, req)
    return _success(view.model_dump(mode="json"))


@auth_bp.get("/professional-verification")
def get_professional_verification():
    auth_service = get_auth_service()
    user_id = get_current_user_id_from_request(request)
    view = auth_service.get_professional_view(user_id)
    return _success(view.model_dump(mode="json"))


@auth_bp.post("/professional-verification")
def submit_professional_verification():
    auth_service = get_auth_service()
    user_id = get_current_user_id_from_request(request)
    payload = request.get_json(silent=True) or {}
    try:
        req = SubmitProfessionalVerificationRequest(**payload)
    except PydanticValidationError as exc:
        raise ValidationError(exc.errors(include_url=False)) from exc

    view = auth_service.submit_professional_verification(user_id, req)
    return _success(view.model_dump(mode="json"))
