import os


def _bool_env(name, default="false"):
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def load_settings():
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-only-change-me"),
        "DEBUG": _bool_env("DEBUG", "false"),
        "HOST": os.environ.get("HOST", "0.0.0.0"),
        "PORT": int(os.environ.get("PORT", "5000")),
        "DATABASE_PATH": os.environ.get("DATABASE_PATH", "loja.db"),
        "AMBIENTE": os.environ.get("AMBIENTE", "development"),
        "APP_VERSION": os.environ.get("APP_VERSION", "1.0.0"),
        "CATEGORIAS_VALIDAS": (
            "informatica",
            "moveis",
            "vestuario",
            "geral",
            "eletronicos",
            "livros",
        ),
        "STATUS_PEDIDO": ("pendente", "aprovado", "enviado", "entregue", "cancelado"),
        "NOME_MIN": 2,
        "NOME_MAX": 200,
        "DISCOUNT_TIERS": (
            (10000, 0.10),
            (5000, 0.05),
            (1000, 0.02),
        ),
    }
