# Playbook de refatoração (Fase 3)

Cada transformação (T-01..T-10) tem sinais, passos e exemplos **Python e JavaScript**. Aplique só o que o relatório da Fase 2 listou, mas a estrutura MVC (T-05 + T-06 + T-09) é obrigatória nos três tipos de projeto.

Não copie estes snippets literalmente se os nomes de domínio forem outros — adapte agregados (produto vs course vs task).

---

## T-01 Extrair God Class por domínio

**Resolve:** AP-01

**Passos:** identifique agregados; crie `models/<agregado>_model.*`; mova queries; apague o arquivo-deus ou deixe um facade deprecado por no máximo um commit.

### Antes (Python)

```python
# models.py — produtos + usuarios + pedidos no mesmo arquivo
def get_produto_por_id(id):
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

### Depois (Python)

```python
# src/models/produto_model.py
def get_by_id(conn, produto_id):
    row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return dict(row) if row else None
```

### Antes (JS)

```javascript
class AppManager {
    setupRoutes(app) { app.post('/api/checkout', (req, res) => { /* SQL + HTTP + pagamento */ }); }
}
```

### Depois (JS)

```javascript
// src/models/courseModel.js — só persistência
// src/controllers/checkoutController.js — orquestra
// src/views/checkoutRoutes.js — router
```

---

## T-02 Secrets para config + ambiente

**Resolve:** AP-02

**Passos:** criar `src/config/settings.*`; ler env com default **inseguro só para dev local**; adicionar `.env.example`; nunca commitar `.env`.

### Antes (Python)

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

### Depois (Python)

```python
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```

### Antes (JS)

```javascript
const config = { paymentGatewayKey: "pk_live_1234567890abcdef", port: 3000 };
```

### Depois (JS)

```javascript
module.exports = {
    port: Number(process.env.PORT) || 3000,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_dev_only",
};
```

---

## T-03 Queries parametrizadas / ORM

**Resolve:** AP-03

### Antes (Python)

```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```

### Depois (Python)

```python
row = conn.execute(
    "SELECT id, nome, email, tipo FROM usuarios WHERE email = ? AND senha_hash = ?",
    (email, senha_hash),
).fetchone()
```

### Antes (JS)

```javascript
db.get(`SELECT * FROM users WHERE email = '${e}'`, callback); // nunca faça isto
```

### Depois (JS)

```javascript
const user = await dbGet(db, "SELECT id, name, email FROM users WHERE email = ?", [email]);
```

Remova endpoints `POST /admin/query` que executam SQL do body. Substitua, se necessário, por operações nomeadas autenticadas.

---

## T-04 Remover dados sensíveis da resposta

**Resolve:** AP-04

### Antes (Python)

```python
return {"id": row["id"], "email": row["email"], "senha": row["senha"]}
# health:
return jsonify({"secret_key": app.config["SECRET_KEY"], "debug": True})
```

### Depois (Python)

```python
def to_public_dict(row):
    return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}

def health():
    return jsonify({"status": "ok", "database": "connected"})
```

### Antes (JS)

```javascript
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

### Depois (JS)

```javascript
logger.info("checkout_payment_attempt", { courseId, last4: String(card).slice(-4) });
```

---

## T-05 Split View × Controller × Model

**Resolve:** AP-05

### Antes (Python / Flask)

```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    result = []
    for t in tasks:
        # serializa, busca user, busca category, calcula overdue...
    return jsonify(result)
```

### Depois (Python / Flask)

```python
# views/task_views.py
@task_bp.get("/tasks")
def get_tasks():
    return jsonify(task_controller.list_tasks()), 200

# controllers/task_controller.py
def list_tasks():
    return task_model.list_with_relations()
```

### Antes (JS)

```javascript
app.get('/api/admin/financial-report', (req, res) => { /* queries N+1 aqui */ });
```

### Depois (JS)

```javascript
router.get("/financial-report", reportController.financialReport);
```

---

## T-06 Composition root + DI (sem globais)

**Resolve:** AP-06

### Antes (Python)

```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
    return db_connection
```

### Depois (Python)

```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(config or load_settings())
    register_error_handlers(app)
    app.register_blueprint(produto_views.bp)
    init_db(app)
    return app
```

Use `g.db` + `teardown_appcontext` no Flask, ou passe `db` para models no Express (`createModels(db)`).

### Antes (JS)

```javascript
let globalCache = {};
let totalRevenue = 0;
```

### Depois (JS)

```javascript
function createApp({ db, config, cache }) {
    const app = express();
    app.locals.db = db;
    app.locals.config = config;
    app.locals.cache = cache || new Map();
    return app;
}
```

---

## T-07 Crypto fraca → hash adequado

**Resolve:** AP-07 (e AP-08 quando MD5)

### Antes (Python)

```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

### Depois (Python)

```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```

### Antes (JS)

```javascript
function badCrypto(pwd) {
    let hash = "";
    for (let i = 0; i < 10000; i++) hash += Buffer.from(pwd).toString("base64").substring(0, 2);
    return hash.substring(0, 10);
}
```

### Depois (JS)

```javascript
const bcrypt = require("bcryptjs");
const hashPassword = (pwd) => bcrypt.hash(pwd, 10);
const verifyPassword = (pwd, hash) => bcrypt.compare(pwd, hash);
```

Senhas de seed: grave **hash**, nunca o literal usado em produção.

---

## T-08 N+1 → JOIN / agregação

**Resolve:** AP-09

### Antes (Python)

```python
for row in pedidos:
    itens = cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        prod = cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

### Depois (Python)

```python
rows = conn.execute(
    """
    SELECT p.id, p.status, p.total, i.produto_id, i.quantidade, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.usuario_id = ?
    """,
    (usuario_id,),
).fetchall()
# agrupar em memória por p.id
```

SQLAlchemy: `select(Task).options(joinedload(Task.user), joinedload(Task.category))`.

### Antes (JS)

```javascript
courses.forEach(c => {
    db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], () => { /* users, payments */ });
});
```

### Depois (JS)

```javascript
const sql = `
  SELECT c.title AS course, p.amount, p.status, u.name AS student
  FROM courses c
  LEFT JOIN enrollments e ON e.course_id = c.id
  LEFT JOIN users u ON u.id = e.user_id
  LEFT JOIN payments p ON p.enrollment_id = e.id
`;
const rows = await dbAll(db, sql, []);
```

---

## T-09 Error handler centralizado

**Passos:** criar `middlewares/error_handler.*`; handlers HTTP só relançam ou `next(err)`; mapear `ValueError`/`NotFound` → 400/404.

### Antes (Python)

```python
try:
    ...
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

### Depois (Python)

```python
def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def bad_request(err):
        return jsonify({"erro": str(err), "sucesso": False}), 400

    @app.errorhandler(Exception)
    def internal(err):
        app.logger.exception("unhandled")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
```

### Antes (JS)

```javascript
if (err) return res.status(500).send("Erro DB");
```

### Depois (JS)

```javascript
function errorHandler(err, req, res, next) {
    const status = err.status || 500;
    res.status(status).json({ erro: status === 500 ? "Erro interno" : err.message });
}
app.use(errorHandler);
```

---

## T-10 APIs deprecated → equivalentes atuais

**Resolve:** AP-08

| Antes | Depois |
|-------|--------|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `Task.query.get(id)` | `db.session.get(Task, id)` |
| `hashlib.md5` (senha) | ver T-07 |
| `sqlite3.verbose()` | `require("sqlite3")` + wrapper promise |
| `type(tags) == list` | `isinstance(tags, list)` |
| callbacks 4 níveis | `async function checkout(req, res, next)` |

### Antes (Python)

```python
task = Task.query.get(task_id)
created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Depois (Python)

```python
from datetime import datetime, timezone
def utcnow():
    return datetime.now(timezone.utc)
task = db.session.get(Task, task_id)
```

### Antes (JS)

```javascript
const sqlite3 = require("sqlite3").verbose();
```

### Depois (JS)

```javascript
const sqlite3 = require("sqlite3");
const { promisify } = require("util");
const dbGet = (db, sql, params) => promisify(db.get.bind(db))(sql, params);
```

---

## Ordem sugerida na Fase 3

1. Criar `config/` + error handler (T-02, T-09).
2. Extrair models por domínio com queries seguras (T-01, T-03, T-08).
3. Criar controllers e views (T-05, T-06).
4. Crypto e serializers públicos (T-07, T-04).
5. Substituir APIs deprecated (T-10).
6. Apagar legado, atualizar entry (`package.json` `main`, README de como rodar).
7. Boot + curl nos endpoints públicos.
