import smtplib

from flask import current_app

from utils.helpers import utcnow


class NotificationService:
    def __init__(self, notifications=None):
        self.notifications = notifications if notifications is not None else []

    def send_email(self, to, subject, body):
        try:
            host = current_app.config["SMTP_HOST"]
            port = current_app.config["SMTP_PORT"]
            user = current_app.config["SMTP_USER"]
            password = current_app.config["SMTP_PASSWORD"]
            server = smtplib.SMTP(host, port, timeout=5)
            server.starttls()
            server.login(user, password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(user, to, message)
            server.quit()
            current_app.logger.info("email_sent to=%s", to)
            return True
        except Exception as exc:
            current_app.logger.warning("email_failed to=%s error=%s", to, exc)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {
                "type": "task_assigned",
                "user_id": user.id,
                "task_id": task.id,
                "timestamp": utcnow(),
            }
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [item for item in self.notifications if item["user_id"] == user_id]
