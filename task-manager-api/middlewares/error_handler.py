from flask import jsonify

from errors import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"error": str(err)}), err.status_code

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"error": "Rota não encontrada"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("unhandled_error: %s", err)
        return jsonify({"error": "Erro interno"}), 500
