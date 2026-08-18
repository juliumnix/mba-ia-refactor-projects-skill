def row_to_produto(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def list_all(db):
    rows = db.execute("SELECT * FROM produtos ORDER BY id").fetchall()
    return [row_to_produto(row) for row in rows]


def get_by_id(db, produto_id):
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return row_to_produto(row) if row else None


def create(db, nome, descricao, preco, estoque, categoria):
    cursor = db.execute(
        """
        INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update(db, produto_id, nome, descricao, preco, estoque, categoria):
    db.execute(
        """
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
        WHERE id = ?
        """,
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def delete(db, produto_id):
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def search(db, termo, categoria=None, preco_min=None, preco_max=None):
    clauses = ["1=1"]
    params = []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        like = f"%{termo}%"
        params.extend([like, like])
    if categoria:
        clauses.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        params.append(preco_max)
    sql = "SELECT * FROM produtos WHERE " + " AND ".join(clauses) + " ORDER BY id"
    rows = db.execute(sql, params).fetchall()
    return [row_to_produto(row) for row in rows]
