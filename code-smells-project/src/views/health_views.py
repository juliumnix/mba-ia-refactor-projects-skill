from flask import Blueprint, jsonify

from src.controllers import health_controller


bp = Blueprint("health", __name__)


@bp.get("/")
def index():
    return jsonify(health_controller.index())


@bp.get("/health")
def health_check():
    return jsonify(health_controller.health_check())


@bp.post("/admin/reset-db")
def reset_database():
    return jsonify(health_controller.reset_database()), 200
