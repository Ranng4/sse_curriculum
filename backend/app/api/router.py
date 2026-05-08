from __future__ import annotations

from flask import Flask

from app.api.routers.auth import auth_bp
from app.api.routers.profile import profile_bp
from app.api.routers.suitability import suitability_bp


def register_routers(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/v1/profile")
    app.register_blueprint(suitability_bp, url_prefix="/api/v1/suitability")
