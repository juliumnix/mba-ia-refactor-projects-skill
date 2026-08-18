# Catálogo de anti-patterns

Use estes IDs no relatório. Um finding = um local concreto (arquivo + linhas). Se o mesmo padrão se repete, agrupe no intervalo de linhas ou cite o pior caso e mencione "também em …".

Severidade padrão abaixo. **Escale** para CRITICAL se o padrão expõe dados ou permite RCE/SQLi. **Desça** para LOW se for apenas estilo isolado.

---

## AP-01 God Class / God File

**Severidade:** CRITICAL

**Sinais:**

- Um arquivo ou classe > ~200 linhas misturando persistência, HTTP, validação e regras de ≥2 agregados.
- Nomes como `Manager`, `AppManager`, `God*`, `utils` que exportam config + crypto + cache + SQL.
- `models.py` / `AppManager.js` com CRUD de várias entidades + relatórios.

**Por que importa:** impossível testar em isolamento; qualquer mudança arrisca todos os fluxos.

---

## AP-02 Hardcoded Secrets

**Severidade:** CRITICAL

**Sinais:**

- Literais: `SECRET_KEY = "..."`, `password = 'senha123'`, `pk_live_`, `sk_live_`, `smtp*password`, `dbPass`.
- Chaves de pagamento, tokens JWT, connection strings com user/pass no código.
- `DEBUG = True` combinado com secretos no mesmo bloco de config de produção.

**Não é AP-02:** placeholder óbvio em `.env.example` (`changeme`, `your-secret-here`).

---

## AP-03 SQL Injection / query construída por string

**Severidade:** CRITICAL

**Sinais:**

- Concatenação: `"SELECT ... WHERE id = " + str(id)`, `` `... ${userInput}` `` em SQL, `f"... {termo} ..."`.
- `cursor.execute(query)` onde `query` veio do body (`dados.get("sql")`).
- `LIKE '%" + termo + "%'` sem placeholders `?` / `%s`.

**Não é AP-03:** `execute("... WHERE id = ?", [id])` ou ORM com bind parameters.

---

## AP-04 Sensitive Data Exposure

**Severidade:** CRITICAL

**Sinais:**

- Endpoint de health/debug devolve `secret_key`, `db_path`, senhas, hashes de senha.
- `to_dict()` / serializer inclui `password` / `senha` / `pass`.
- `GET /usuarios` lista hash ou senha em claro.
- Logs com número de cartão, senha, token (`console.log(\`cartão ${cc}\`)`).
- Endpoint admin sem autenticação que apaga o banco ou roda SQL.

---

## AP-05 Fat Controller / regras na borda HTTP

**Severidade:** HIGH

**Sinais:**

- Handler de rota com validação + SQL + efeitos (email, SMS, pagamento) no mesmo corpo.
- Blueprint/Router que chama `Model.query` / `db.run` diretamente, sem controller.
- Duplicação do mesmo bloco de validação em POST e PUT.

**Não é AP-05:** rota que só faz bind HTTP → chama controller → `jsonify`/`res.json`.

---

## AP-06 Global Mutable State / acoplamento sem DI

**Severidade:** HIGH

**Sinais:**

- `global db_connection`, `let globalCache = {}`, `let totalRevenue = 0` compartilhados.
- Singleton de conexão SQLite com `check_same_thread=False` sem pooling consciente.
- Import de módulo de config mutável de todo lugar, sem factory.
- Classe que instancia o DB no `constructor` e registra rotas no mesmo objeto.

---

## AP-07 Weak / homemade cryptography

**Severidade:** HIGH (CRITICAL se senha em claro sem hash nenhum — combine com AP-04)

**Sinais:**

- `hashlib.md5` / `sha1` para senha.
- Loop que concatena `base64` (`badCrypto`).
- Comparação de senha em texto plano no SQL (`senha = '" + senha + "'"`).
- JWT fake (`'fake-jwt-token-' + id`) apresentado como autenticação.

**Equivalente moderno:** Argon2, bcrypt, scrypt ou `werkzeug.security.generate_password_hash` / `bcrypt.hash`.

---

## AP-08 Deprecated APIs

**Severidade:** MEDIUM (HIGH se a API deprecated for de criptografia — nesse caso também registre AP-07)

Catálogo mínimo (expanda se a stack tiver outros):

| Stack | Sinal | Equivalente moderno |
|-------|-------|---------------------|
| Python 3.12+ | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| Flask-SQLAlchemy 3 / SQLAlchemy 2 | `Model.query.get(id)` | `db.session.get(Model, id)` |
| Python | `hashlib.md5` para senha | bcrypt / werkzeug / argon2 |
| Node sqlite3 | `sqlite3.verbose()` em produção | driver sem verbose; ou `sqlite` promise API |
| Node | callbacks aninhados 4+ níveis no I/O | `async/await` ou `util.promisify` |
| Express | `res.send(htmlError)` inconsistente vs JSON | `res.status().json({ erro })` |
| JS | `var` + `==` frouxo em código novo | `const`/`let` + `===` |
| Python | `type(x) == list` | `isinstance(x, list)` |

Sempre cite o símbolo deprecated e o substituto no campo Recommendation.

---

## AP-09 N+1 queries

**Severidade:** MEDIUM

**Sinais:**

- `for row in pedidos:` seguido de `SELECT ... WHERE pedido_id =` e outro `SELECT` por item.
- `courses.forEach` → `enrollments` → `users` → `payments` (Node).
- `for t in tasks: User.query.get(t.user_id)` / `Category.query.get`.
- Relatórios que fazem `query.count()` repetido por status em vez de `GROUP BY`.

---

## AP-10 Missing validation / superfície perigosa

**Severidade:** MEDIUM

**Sinais:**

- POST/PUT sem checar body, tipos ou enums.
- Rota admin (`/admin/*`, `/api/admin/*`) sem auth/middleware.
- Delete de agregado sem cascata (usuário some, matrículas órfãs).
- Campos abreviados e não documentados (`usr`, `eml`, `c_id`) sem schema.
- Dependência de validação no manifest (`marshmallow`, `joi`, `zod`) **nunca importada**.

---

## AP-11 Magic numbers / poor naming

**Severidade:** LOW

**Sinais:**

- Literais `10000`, `0.1`, `0.05`, `priority < 1 or > 5`, `len(title) < 3` espalhados.
- Identificadores `u`, `e`, `p`, `cid`, `cc`, `t`, `d`.
- Parâmetro `id` sombreando builtin Python.
- Strings de status/categoria duplicadas em vários arquivos.

---

## AP-12 Dead code / unused imports

**Severidade:** LOW

**Sinais:**

- `import json, os, sys` no módulo e nenhum uso.
- Função `process_task_data` / `generate_id` nunca chamada pelas rotas.
- Dependência em `requirements.txt`/`package.json` sem import (`python-dotenv`, `marshmallow`, `requests`).
- Variável exportada e nunca lida (`totalRevenue`).

---

## Como classificar na fronteira

1. SQLi ou secretos no health → CRITICAL, mesmo se o arquivo for "só um controller".
2. Fat controller sem SQLi → HIGH, não CRITICAL.
3. Deprecated `utcnow` sozinho → MEDIUM (AP-08). MD5 de senha → AP-07 HIGH **e** AP-08.
4. N+1 em relatório administrativo → MEDIUM, não HIGH, a menos que derrube o processo.
5. Não conte o mesmo trecho duas vezes com IDs diferentes salvo se forem problemas distintos (ex.: concatenação SQL **e** senha em claro na mesma query = AP-03 + AP-07).
