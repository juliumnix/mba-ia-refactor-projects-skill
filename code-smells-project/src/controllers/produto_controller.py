from flask import current_app

from src.database import get_db
from src.errors import AppError, NotFoundError
from src.models import produto_model


def listar_produtos():
    return {"dados": produto_model.list_all(get_db()), "sucesso": True}


def buscar_produto(produto_id):
    produto = produto_model.get_by_id(get_db(), produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return {"dados": produto, "sucesso": True}


def criar_produto(dados):
    nome, descricao, preco, estoque, categoria = _parse_produto_payload(dados)
    produto_id = produto_model.create(
        get_db(), nome, descricao, preco, estoque, categoria
    )
    return {
        "dados": {"id": produto_id},
        "sucesso": True,
        "mensagem": "Produto criado",
    }, 201


def atualizar_produto(produto_id, dados):
    if not produto_model.get_by_id(get_db(), produto_id):
        raise NotFoundError("Produto não encontrado")
    nome, descricao, preco, estoque, categoria = _parse_produto_payload(dados)
    produto_model.update(get_db(), produto_id, nome, descricao, preco, estoque, categoria)
    return {"sucesso": True, "mensagem": "Produto atualizado"}


def deletar_produto(produto_id):
    if not produto_model.get_by_id(get_db(), produto_id):
        raise NotFoundError("Produto não encontrado")
    produto_model.delete(get_db(), produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}


def buscar_produtos(termo, categoria, preco_min, preco_max):
    parsed_min = float(preco_min) if preco_min not in (None, "") else None
    parsed_max = float(preco_max) if preco_max not in (None, "") else None
    resultados = produto_model.search(
        get_db(), termo, categoria, parsed_min, parsed_max
    )
    return {"dados": resultados, "total": len(resultados), "sucesso": True}


def _parse_produto_payload(dados):
    if not dados:
        raise AppError("Dados inválidos")
    for field in ("nome", "preco", "estoque"):
        if field not in dados:
            label = {"nome": "Nome", "preco": "Preço", "estoque": "Estoque"}[field]
            raise AppError(f"{label} é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")
    settings = current_app.config

    if preco < 0:
        raise AppError("Preço não pode ser negativo")
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo")
    if len(nome) < settings["NOME_MIN"]:
        raise AppError("Nome muito curto")
    if len(nome) > settings["NOME_MAX"]:
        raise AppError("Nome muito longo")
    if categoria not in settings["CATEGORIAS_VALIDAS"]:
        raise AppError(
            "Categoria inválida. Válidas: " + str(list(settings["CATEGORIAS_VALIDAS"]))
        )
    return nome, descricao, preco, estoque, categoria
