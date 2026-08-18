from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from config.settings import load_settings
from database import db
from middlewares.error_handler import register_error_handlers
from views.report_views import report_bp
from views.task_views import task_bp
from views.user_views import user_bp
from utils.helpers import utcnow


def create_app(overrides=None):
    load_dotenv()
    app = Flask(__name__)
    settings = load_settings()
    if overrides:
        settings.update(overrides)
    app.config.update(settings)
    CORS(app)
    db.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": str(utcnow())})

    @app.get("/")
    def index():
        return jsonify({"message": "Task Manager API", "version": "1.0"})

    with app.app_context():
        db.create_all()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
    )
