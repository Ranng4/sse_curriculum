from __future__ import annotations

from flask import Flask

from app.api.routers.auth import auth_bp
from app.api.routers.content import content_bp
from app.api.routers.forum import forum_bp
from app.api.routers.profile import profile_bp
from app.api.routers.social import social_bp
from app.api.routers.suitability import suitability_bp
from app.api.routers.admin import admin_bp
from app.api.routers.messages import messages_bp


def register_routers(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(forum_bp, url_prefix="/api/v1/forum")
    app.register_blueprint(profile_bp, url_prefix="/api/v1/profile")
    app.register_blueprint(suitability_bp, url_prefix="/api/v1/suitability")
    app.register_blueprint(content_bp, url_prefix="/api/v1/content")
    app.register_blueprint(social_bp, url_prefix="/api/v1/social")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(messages_bp, url_prefix="/api/v1")
