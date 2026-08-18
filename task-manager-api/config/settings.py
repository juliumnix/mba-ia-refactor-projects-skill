import os


def _bool_env(name, default="false"):
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def load_settings():
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-only-change-me"),
        "SQLALCHEMY_DATABASE_URI": os.environ.get(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///tasks.db"
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "DEBUG": _bool_env("DEBUG", "false"),
        "HOST": os.environ.get("HOST", "0.0.0.0"),
        "PORT": int(os.environ.get("PORT", "5000")),
        "SMTP_HOST": os.environ.get("SMTP_HOST", "localhost"),
        "SMTP_PORT": int(os.environ.get("SMTP_PORT", "587")),
        "SMTP_USER": os.environ.get("SMTP_USER", "dev@localhost"),
        "SMTP_PASSWORD": os.environ.get("SMTP_PASSWORD", "dev-only-change-me"),
        "VALID_STATUSES": ("pending", "in_progress", "done", "cancelled"),
        "VALID_ROLES": ("user", "admin", "manager"),
        "MIN_TITLE_LENGTH": 3,
        "MAX_TITLE_LENGTH": 200,
        "MIN_PASSWORD_LENGTH": 4,
        "DEFAULT_PRIORITY": 3,
        "MIN_PRIORITY": 1,
        "MAX_PRIORITY": 5,
        "DEFAULT_COLOR": "#000000",
    }
