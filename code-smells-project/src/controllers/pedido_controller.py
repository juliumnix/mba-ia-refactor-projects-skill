from flask import current_app

from src.database import get_db
from src.errors import AppError
from src.models import pedido_model
from src.services import notification_service


def criar_pedido(dados):
    if not dados:
        raise AppError("Dados inválidos")
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise AppError("Usuario ID é obrigatório")
    if not itens:
        raise AppError("Pedido deve ter pelo menos 1 item")

    resultado = pedido_model.create(get_db(), usuario_id, itens)
    if "erro" in resultado:
        raise AppError(resultado["erro"])

    notification_service.notify_pedido_criado(resultado["pedido_id"], usuario_id)
    return {
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }, 201


def listar_pedidos_usuario(usuario_id):
    return {"dados": pedido_model.list_by_usuario(get_db(), usuario_id), "sucesso": True}


def listar_todos_pedidos():
    return {"dados": pedido_model.list_all(get_db()), "sucesso": True}


def atualizar_status_pedido(pedido_id, dados):
    if not dados:
        raise AppError("Dados inválidos")
    novo_status = dados.get("status", "")
    if novo_status not in current_app.config["STATUS_PEDIDO"]:
        raise AppError("Status inválido")
    pedido_model.update_status(get_db(), pedido_id, novo_status)
    notification_service.notify_status_atualizado(pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}


def relatorio_vendas():
    return {"dados": pedido_model.sales_report(get_db()), "sucesso": True}
