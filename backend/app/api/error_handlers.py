from __future__ import annotations

from flask import Flask, jsonify

from app.core.errors import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    UserSystemError,
    ValidationError,
)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        return jsonify({"code": 400, "message": str(exc), "data": None}), 400

    @app.errorhandler(ConflictError)
    def handle_conflict_error(exc: ConflictError):
        return jsonify({"code": 409, "message": str(exc), "data": None}), 409

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(exc: NotFoundError):
        return jsonify({"code": 404, "message": str(exc), "data": None}), 404

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(exc: UnauthorizedError):
        return jsonify({"code": 401, "message": str(exc), "data": None}), 401

    @app.errorhandler(UserSystemError)
    def handle_user_system_error(exc: UserSystemError):
        return jsonify({"code": 400, "message": str(exc), "data": None}), 400
