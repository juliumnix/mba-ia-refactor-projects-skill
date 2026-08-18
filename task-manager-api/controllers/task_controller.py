from flask import current_app
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from database import db
from errors import AppError, NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from schemas.task_schema import TaskCreateSchema, TaskSchema
from utils.helpers import parse_date, utcnow


def _serialize_tags(tags):
    if tags is None:
        return None
    if isinstance(tags, list):
        return ",".join(tags)
    return tags


def _load(schema, payload, partial=False):
    if not payload:
        raise AppError("Dados inválidos")
    try:
        return schema.load(payload, partial=partial)
    except ValidationError as err:
        messages = err.messages
        first = next(iter(messages.values()))
        if isinstance(first, list):
            first = first[0]
        raise AppError(str(first)) from err


def _get_or_404(model, entity_id, message):
    entity = db.session.get(model, entity_id)
    if not entity:
        raise NotFoundError(message)
    return entity


def _validate_title(title, required=False):
    settings = current_app.config
    if title is None and not required:
        return None
    if not title:
        raise AppError("Título é obrigatório" if required else "Título não pode ser vazio")
    if len(title) < settings["MIN_TITLE_LENGTH"]:
        raise AppError("Título muito curto")
    if len(title) > settings["MAX_TITLE_LENGTH"]:
        raise AppError("Título muito longo")
    return title


def _ensure_user(user_id):
    if user_id and not db.session.get(User, user_id):
        raise NotFoundError("Usuário não encontrado")


def _ensure_category(category_id):
    if category_id and not db.session.get(Category, category_id):
        raise NotFoundError("Categoria não encontrada")


def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    result = []
    for task in tasks:
        data = task.to_dict()
        data["overdue"] = task.is_overdue()
        data["user_name"] = task.user.name if task.user else None
        data["category_name"] = task.category.name if task.category else None
        result.append(data)
    return result


def get_task(task_id):
    task = _get_or_404(Task, task_id, "Task não encontrada")
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return data


def create_task(payload):
    data = _load(TaskCreateSchema(), payload)
    title = _validate_title(data.get("title"), required=True)
    status = data.get("status", "pending")
    if status not in current_app.config["VALID_STATUSES"]:
        raise AppError("Status inválido")
    priority = data.get("priority", current_app.config["DEFAULT_PRIORITY"])
    if priority < current_app.config["MIN_PRIORITY"] or priority > current_app.config["MAX_PRIORITY"]:
        raise AppError("Prioridade deve ser entre 1 e 5")
    _ensure_user(data.get("user_id"))
    _ensure_category(data.get("category_id"))

    task = Task()
    task.title = title
    task.description = data.get("description", "")
    task.status = status
    task.priority = priority
    task.user_id = data.get("user_id")
    task.category_id = data.get("category_id")
    if data.get("due_date"):
        parsed = parse_date(data["due_date"])
        if not parsed:
            raise AppError("Formato de data inválido. Use YYYY-MM-DD")
        task.due_date = parsed
    if data.get("tags") is not None:
        task.tags = _serialize_tags(data["tags"])

    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201


def update_task(task_id, payload):
    task = _get_or_404(Task, task_id, "Task não encontrada")
    data = _load(TaskSchema(), payload, partial=True)
    if "title" in data:
        task.title = _validate_title(data["title"], required=True)
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        if data["status"] not in current_app.config["VALID_STATUSES"]:
            raise AppError("Status inválido")
        task.status = data["status"]
    if "priority" in data:
        if data["priority"] < current_app.config["MIN_PRIORITY"] or data["priority"] > current_app.config["MAX_PRIORITY"]:
            raise AppError("Prioridade deve ser entre 1 e 5")
        task.priority = data["priority"]
    if "user_id" in data:
        _ensure_user(data["user_id"])
        task.user_id = data["user_id"]
    if "category_id" in data:
        _ensure_category(data["category_id"])
        task.category_id = data["category_id"]
    if "due_date" in data:
        if data["due_date"]:
            parsed = parse_date(data["due_date"])
            if not parsed:
                raise AppError("Formato de data inválido")
            task.due_date = parsed
        else:
            task.due_date = None
    if "tags" in data:
        task.tags = _serialize_tags(data["tags"])
    task.updated_at = utcnow()
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = _get_or_404(Task, task_id, "Task não encontrada")
    db.session.delete(task)
    db.session.commit()
    return {"message": "Task deletada com sucesso"}


def search_tasks(query, status, priority, user_id):
    filters = Task.query
    if query:
        filters = filters.filter(
            db.or_(
                Task.title.like(f"%{query}%"),
                Task.description.like(f"%{query}%"),
            )
        )
    if status:
        filters = filters.filter(Task.status == status)
    if priority:
        filters = filters.filter(Task.priority == int(priority))
    if user_id:
        filters = filters.filter(Task.user_id == int(user_id))
    return [task.to_dict() for task in filters.all()]


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()
    overdue_count = sum(1 for task in Task.query.all() if task.is_overdue())
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "overdue": overdue_count,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }
