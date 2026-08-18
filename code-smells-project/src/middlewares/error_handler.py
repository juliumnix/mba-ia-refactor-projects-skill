from flask import jsonify

from src.errors import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        payload = {"erro": str(err), "sucesso": False}
        return jsonify(payload), err.status_code

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"erro": "Rota não encontrada", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("unhandled_error: %s", err)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
