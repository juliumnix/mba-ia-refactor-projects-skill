import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import load_settings
from src.database import init_db
from src.middlewares.error_handler import register_error_handlers
from src.views import health_views, pedido_views, produto_views, usuario_views


def create_app(overrides=None):
    settings = load_settings()
    if overrides:
        settings.update(overrides)

    app = Flask(__name__)
    app.config.update(settings)
    CORS(app)
    register_error_handlers(app)
    init_db(app)

    app.register_blueprint(health_views.bp)
    app.register_blueprint(produto_views.bp)
    app.register_blueprint(usuario_views.bp)
    app.register_blueprint(pedido_views.bp)

    logging.basicConfig(level=logging.INFO)
    return app
