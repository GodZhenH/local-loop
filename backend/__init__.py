"""Local Loop backend - Flask application factory (Puvanan)."""


"""Local Loop backend - Flask application factory (Puvanan)."""

import os

from flask import Flask, jsonify
from flask_cors import CORS

from backend import database


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    app.config["DATABASE"] = os.environ.get(
        "DATABASE_PATH", str(database.DEFAULT_DB_PATH)
    )

    if test_config:
        app.config.update(test_config)

    # Registers the per-request DB cleanup and creates tables on first run.
    database.init_app(app)

    # Imported here to avoid circular imports.
    from backend.routes.exchanges import exchanges_bp
    from backend.routes.listings import listings_bp
    from backend.routes.users import users_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(exchanges_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "Internal server error"}), 500

    return app
