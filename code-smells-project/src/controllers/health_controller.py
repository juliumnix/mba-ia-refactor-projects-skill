from flask import current_app

from src.database import get_db, reset_db


def health_check():
    db = get_db()
    db.execute("SELECT 1")
    produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produtos,
            "usuarios": usuarios,
            "pedidos": pedidos,
        },
        "versao": current_app.config["APP_VERSION"],
        "ambiente": current_app.config["AMBIENTE"],
    }


def index():
    return {
        "mensagem": "Bem-vindo à API da Loja",
        "versao": current_app.config["APP_VERSION"],
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    }


def reset_database():
    reset_db()
    return {"mensagem": "Banco de dados resetado", "sucesso": True}
