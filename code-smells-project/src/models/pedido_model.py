from flask import current_app


PEDIDO_ITEM_SQL = """
SELECT
    p.id,
    p.usuario_id,
    p.status,
    p.total,
    p.criado_em,
    i.id AS item_id,
    i.produto_id,
    i.quantidade,
    i.preco_unitario,
    pr.nome AS produto_nome
FROM pedidos p
LEFT JOIN itens_pedido i ON i.pedido_id = p.id
LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def _group_pedidos(rows):
    pedidos = {}
    order = []
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            order.append(pedido_id)
        if row["item_id"] is not None:
            pedidos[pedido_id]["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return [pedidos[pedido_id] for pedido_id in order]


def create(db, usuario_id, itens):
    total = 0
    resolved = []
    for item in itens:
        produto = db.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
            (item["produto_id"],),
        ).fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]
        resolved.append((produto, item["quantidade"]))

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for produto, quantidade in resolved:
        db.execute(
            """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
            """,
            (pedido_id, produto["id"], quantidade, produto["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto["id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def list_by_usuario(db, usuario_id):
    rows = db.execute(
        PEDIDO_ITEM_SQL + " WHERE p.usuario_id = ? ORDER BY p.id, i.id",
        (usuario_id,),
    ).fetchall()
    return _group_pedidos(rows)


def list_all(db):
    rows = db.execute(PEDIDO_ITEM_SQL + " ORDER BY p.id, i.id").fetchall()
    return _group_pedidos(rows)


def update_status(db, pedido_id, novo_status):
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()


def sales_report(db):
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    pendentes = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'"
    ).fetchone()[0]
    aprovados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'"
    ).fetchone()[0]
    cancelados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'"
    ).fetchone()[0]

    desconto = 0
    for threshold, rate in current_app.config["DISCOUNT_TIERS"]:
        if faturamento > threshold:
            desconto = faturamento * rate
            break

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
