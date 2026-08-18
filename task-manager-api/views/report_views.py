from flask import Blueprint, jsonify, request

from controllers import report_controller


report_bp = Blueprint("reports", __name__)


def _respond(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@report_bp.get("/reports/summary")
def summary_report():
    return _respond(report_controller.summary_report())


@report_bp.get("/reports/user/<int:user_id>")
def user_report(user_id):
    return _respond(report_controller.user_report(user_id))


@report_bp.get("/categories")
def get_categories():
    return _respond(report_controller.list_categories())


@report_bp.post("/categories")
def create_category():
    return _respond(report_controller.create_category(request.get_json(silent=True)))


@report_bp.put("/categories/<int:cat_id>")
def update_category(cat_id):
    return _respond(report_controller.update_category(cat_id, request.get_json(silent=True)))


@report_bp.delete("/categories/<int:cat_id>")
def delete_category(cat_id):
    return _respond(report_controller.delete_category(cat_id))
