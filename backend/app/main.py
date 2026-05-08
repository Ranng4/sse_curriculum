from __future__ import annotations

from flask import Flask, jsonify

from app.api.error_handlers import register_error_handlers
from app.api.router import register_routers


def create_app() -> Flask:
    app = Flask(__name__)
    register_routers(app)
    register_error_handlers(app)

    @app.get("/healthz")
    def health_check():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
