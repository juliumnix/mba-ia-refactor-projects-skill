from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from marshmallow import ValidationError
from sqlalchemy.orm import subqueryload

from database import db
from errors import AppError, ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from models.task import Task
from models.user import User
from schemas.task_schema import UserCreateSchema
from utils.helpers import validate_email


def _load_user(payload):
    if not payload:
        raise AppError("Dados inválidos")
    try:
        return UserCreateSchema().load(payload)
    except ValidationError as err:
        messages = err.messages
        first = next(iter(messages.values()))
        if isinstance(first, list):
            first = first[0]
        raise AppError(str(first)) from err


def list_users():
    users = User.query.options(subqueryload(User.tasks)).all()
    result = []
    for user in users:
        data = user.to_dict()
        data["task_count"] = len(user.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    data = user.to_dict()
    data["tasks"] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
    return data


def create_user(payload):
    data = _load_user(payload)
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")
    if not name:
        raise AppError("Nome é obrigatório")
    if not email:
        raise AppError("Email é obrigatório")
    if not password:
        raise AppError("Senha é obrigatória")
    if not validate_email(email):
        raise AppError("Email inválido")
    if len(password) < current_app.config["MIN_PASSWORD_LENGTH"]:
        raise AppError("Senha deve ter no mínimo 4 caracteres")
    if User.query.filter_by(email=email).first():
        raise ConflictError("Email já cadastrado")
    if role not in current_app.config["VALID_ROLES"]:
        raise AppError("Role inválido")
    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201


def update_user(user_id, payload):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    if not payload:
        raise AppError("Dados inválidos")
    if "name" in payload:
        user.name = payload["name"]
    if "email" in payload:
        if not validate_email(payload["email"]):
            raise AppError("Email inválido")
        existing = User.query.filter_by(email=payload["email"]).first()
        if existing and existing.id != user_id:
            raise ConflictError("Email já cadastrado")
        user.email = payload["email"]
    if "password" in payload:
        if len(payload["password"]) < current_app.config["MIN_PASSWORD_LENGTH"]:
            raise AppError("Senha muito curta")
        user.set_password(payload["password"])
    if "role" in payload:
        if payload["role"] not in current_app.config["VALID_ROLES"]:
            raise AppError("Role inválido")
        user.role = payload["role"]
    if "active" in payload:
        user.active = payload["active"]
    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return {"message": "Usuário deletado com sucesso"}


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    result = []
    for task in Task.query.filter_by(user_id=user_id).all():
        data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "created_at": str(task.created_at),
            "due_date": str(task.due_date) if task.due_date else None,
            "overdue": task.is_overdue(),
        }
        result.append(data)
    return result


def login(payload):
    if not payload:
        raise AppError("Dados inválidos")
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise AppError("Email e senha são obrigatórios")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise UnauthorizedError("Credenciais inválidas")
    if not user.active:
        raise ForbiddenError("Usuário inativo")
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps({"uid": user.id})
    return {
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": token,
    }
