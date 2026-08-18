from werkzeug.security import check_password_hash, generate_password_hash


def row_to_public_user(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def list_all(db):
    rows = db.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios ORDER BY id"
    ).fetchall()
    return [row_to_public_user(row) for row in rows]


def get_by_id(db, usuario_id):
    row = db.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
        (usuario_id,),
    ).fetchone()
    return row_to_public_user(row) if row else None


def create(db, nome, email, senha, tipo="cliente"):
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def authenticate(db, email, senha):
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if row is None:
        return None
    if not check_password_hash(row["senha"], senha):
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
