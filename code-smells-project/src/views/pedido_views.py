from flask import Blueprint, jsonify, request

from src.controllers import pedido_controller


bp = Blueprint("pedidos", __name__)


def _respond(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@bp.post("/pedidos")
def criar_pedido():
    return _respond(pedido_controller.criar_pedido(request.get_json(silent=True)))


@bp.get("/pedidos")
def listar_todos_pedidos():
    return _respond(pedido_controller.listar_todos_pedidos())


@bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    return _respond(pedido_controller.listar_pedidos_usuario(usuario_id))


@bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    return _respond(
        pedido_controller.atualizar_status_pedido(
            pedido_id, request.get_json(silent=True)
        )
    )


@bp.get("/relatorios/vendas")
def relatorio_vendas():
    return _respond(pedido_controller.relatorio_vendas())
