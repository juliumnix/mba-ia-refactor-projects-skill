from flask import Blueprint, jsonify, request

from controllers import task_controller


task_bp = Blueprint("tasks", __name__)


def _respond(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@task_bp.get("/tasks")
def get_tasks():
    return _respond(task_controller.list_tasks())


@task_bp.get("/tasks/search")
def search_tasks():
    return _respond(
        task_controller.search_tasks(
            request.args.get("q", ""),
            request.args.get("status", ""),
            request.args.get("priority", ""),
            request.args.get("user_id", ""),
        )
    )


@task_bp.get("/tasks/stats")
def task_stats():
    return _respond(task_controller.task_stats())


@task_bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    return _respond(task_controller.get_task(task_id))


@task_bp.post("/tasks")
def create_task():
    return _respond(task_controller.create_task(request.get_json(silent=True)))


@task_bp.put("/tasks/<int:task_id>")
def update_task(task_id):
    return _respond(task_controller.update_task(task_id, request.get_json(silent=True)))


@task_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    return _respond(task_controller.delete_task(task_id))
