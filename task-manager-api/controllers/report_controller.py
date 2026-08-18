from datetime import timedelta, timezone

from flask import current_app

from database import db
from errors import AppError, NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utcnow


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()
    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()
    priorities = {
        1: "critical",
        2: "high",
        3: "medium",
        4: "low",
        5: "minimal",
    }
    tasks_by_priority = {
        label: Task.query.filter_by(priority=value).count()
        for value, label in priorities.items()
    }
    all_tasks = Task.query.all()
    overdue_list = []
    for task in all_tasks:
        if task.is_overdue():
            overdue_list.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (utcnow() - _aware(task.due_date)).days,
                }
            )
    seven_days_ago = utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done", Task.updated_at >= seven_days_ago
    ).count()
    user_stats = []
    for user in User.query.all():
        user_tasks = Task.query.filter_by(user_id=user.id).all()
        total = len(user_tasks)
        completed = sum(1 for task in user_tasks if task.status == "done")
        user_stats.append(
            {
                "user_id": user.id,
                "user_name": user.name,
                "total_tasks": total,
                "completed_tasks": completed,
                "completion_rate": calculate_percentage(completed, total),
            }
        )
    return {
        "generated_at": str(utcnow()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
            "cancelled": cancelled,
        },
        "tasks_by_priority": tasks_by_priority,
        "overdue": {"count": len(overdue_list), "tasks": overdue_list},
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = sum(1 for task in tasks if task.status == "done")
    pending = sum(1 for task in tasks if task.status == "pending")
    in_progress = sum(1 for task in tasks if task.status == "in_progress")
    cancelled = sum(1 for task in tasks if task.status == "cancelled")
    overdue = sum(1 for task in tasks if task.is_overdue())
    high_priority = sum(1 for task in tasks if task.priority <= 2)
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        },
    }


def list_categories():
    categories = Category.query.all()
    result = []
    counts = dict(
        db.session.query(Task.category_id, db.func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    for category in categories:
        data = category.to_dict()
        data["task_count"] = counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(payload):
    if not payload:
        raise AppError("Dados inválidos")
    name = payload.get("name")
    if not name:
        raise AppError("Nome é obrigatório")
    category = Category()
    category.name = name
    category.description = payload.get("description", "")
    category.color = payload.get("color", current_app.config["DEFAULT_COLOR"])
    db.session.add(category)
    db.session.commit()
    return category.to_dict(), 201


def update_category(cat_id, payload):
    category = db.session.get(Category, cat_id)
    if not category:
        raise NotFoundError("Categoria não encontrada")
    if not payload:
        raise AppError("Dados inválidos")
    if "name" in payload:
        category.name = payload["name"]
    if "description" in payload:
        category.description = payload["description"]
    if "color" in payload:
        category.color = payload["color"]
    db.session.commit()
    return category.to_dict()


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        raise NotFoundError("Categoria não encontrada")
    db.session.delete(category)
    db.session.commit()
    return {"message": "Categoria deletada"}


def _aware(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
