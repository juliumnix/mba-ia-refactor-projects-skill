from flask import Blueprint, jsonify, request

from src.controllers import usuario_controller


bp = Blueprint("usuarios", __name__)


def _respond(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@bp.get("/usuarios")
def listar_usuarios():
    return _respond(usuario_controller.listar_usuarios())


@bp.get("/usuarios/<int:usuario_id>")
def buscar_usuario(usuario_id):
    return _respond(usuario_controller.buscar_usuario(usuario_id))


@bp.post("/usuarios")
def criar_usuario():
    return _respond(usuario_controller.criar_usuario(request.get_json(silent=True)))


@bp.post("/login")
def login():
    return _respond(usuario_controller.login(request.get_json(silent=True)))
