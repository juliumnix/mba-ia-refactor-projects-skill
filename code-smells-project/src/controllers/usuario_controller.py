from src.database import get_db
from src.errors import AppError, NotFoundError, UnauthorizedError
from src.models import usuario_model


def listar_usuarios():
    return {"dados": usuario_model.list_all(get_db()), "sucesso": True}


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_by_id(get_db(), usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return {"dados": usuario, "sucesso": True}


def criar_usuario(dados):
    if not dados:
        raise AppError("Dados inválidos")
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise AppError("Nome, email e senha são obrigatórios")
    usuario_id = usuario_model.create(get_db(), nome, email, senha)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


def login(dados):
    if not dados:
        raise AppError("Dados inválidos")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise AppError("Email e senha são obrigatórios")
    usuario = usuario_model.authenticate(get_db(), email, senha)
    if not usuario:
        raise UnauthorizedError("Email ou senha inválidos")
    return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}
