from flask import Blueprint, jsonify, request

from src.controllers import produto_controller


bp = Blueprint("produtos", __name__)


def _respond(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@bp.get("/produtos")
def listar_produtos():
    return _respond(produto_controller.listar_produtos())


@bp.get("/produtos/busca")
def buscar_produtos():
    return _respond(
        produto_controller.buscar_produtos(
            request.args.get("q", ""),
            request.args.get("categoria"),
            request.args.get("preco_min"),
            request.args.get("preco_max"),
        )
    )


@bp.get("/produtos/<int:produto_id>")
def buscar_produto(produto_id):
    return _respond(produto_controller.buscar_produto(produto_id))


@bp.post("/produtos")
def criar_produto():
    return _respond(produto_controller.criar_produto(request.get_json(silent=True)))


@bp.put("/produtos/<int:produto_id>")
def atualizar_produto(produto_id):
    return _respond(
        produto_controller.atualizar_produto(produto_id, request.get_json(silent=True))
    )


@bp.delete("/produtos/<int:produto_id>")
def deletar_produto(produto_id):
    return _respond(produto_controller.deletar_produto(produto_id))
