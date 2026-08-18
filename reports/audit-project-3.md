================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy, flask-cors, marshmallow, requests, python-dotenv
Domain:        Task Manager API (tarefas, usuários, categorias)
Architecture:  Parcialmente organizada — models/routes existem, mas a borda HTTP concentra regras
Source files:  14 files analyzed
DB tables:     tasks, users, categories
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   14 analyzed | ~1100 lines of code

Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3

Findings

[CRITICAL] Weak cryptography (MD5)
File: models/user.py:27-32
ID: AP-07
Description: `set_password` / `check_password` usam `hashlib.md5(pwd.encode()).hexdigest()` sem salt. Senhas de seed são curtas (`1234`, `abcd`, `pass` em seed.py:19-33).
Impact: MD5 é quebrado para senhas; rainbow tables recuperam as contas admin imediatamente.
Recommendation: T-07 — `werkzeug.security.generate_password_hash` (pbkdf2/scrypt). Também AP-08.

[CRITICAL] Sensitive Data Exposure
File: models/user.py:16-25
ID: AP-04
Description: `User.to_dict()` inclui `'password': self.password`. `POST /login` devolve `user.to_dict()` (`routes/user_routes.py:207-210`), vazando o hash MD5. Token `'fake-jwt-token-' + str(user.id)` não autentica nada.
Impact: Qualquer login bem-sucedido entrega o hash; GET /users/<id> também vazava a senha.
Recommendation: T-04 — serializer público sem password; token assinado (itsdangerous).

[CRITICAL] Hardcoded Secrets
File: app.py:13
ID: AP-02
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'`. SMTP em `services/notification_service.py:7-10` com `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'`.
Impact: Segredo de sessão e senha de e-mail no git; dotenv está no requirements mas não é usado.
Recommendation: T-02 — `config/settings.py` + `.env`; NotificationService lê `current_app.config`.

[HIGH] Fat Controller / regras na borda HTTP
File: routes/task_routes.py:11-63
ID: AP-05
Description: Blueprints em `routes/` fazem query, validação, serialização, cálculo de overdue e lookups de User/Category. Não existe camada controller. `utils/helpers.py:process_task_data` duplica validação e não é chamado.
Impact: Rotas de 300 linhas; lógica de overdue copiada em 4 lugares.
Recommendation: T-05 — views magras + `controllers/`; `Task.is_overdue()` único.

[HIGH] Global / composition fraca
File: app.py:9-34
ID: AP-06
Description: `app = Flask(__name__)` global, `db.create_all()` no import, config inline. Sem factory testável nem error handler central — cada rota tem `try/except` próprio (às vezes `except:` nu em task_routes.py:62).
Impact: Testes precisam do app real; erros viram 500 genérico ou passam silenciosos.
Recommendation: T-06 + T-09 — `create_app()` e `register_error_handlers`.

[HIGH] Deprecated API: datetime.utcnow + Query.get
File: models/task.py:15-16
ID: AP-08
Description: `default=datetime.utcnow` em Task/User/Category e dezenas de comparações em routes (task_routes.py:31, 72, 215, 285; report_routes.py:35-71). `Task.query.get(task_id)` em `routes/task_routes.py:67` (padrão SQLAlchemy 1.x, deprecated no 2.0 / Flask-SQLAlchemy 3).
Impact: Datetimes naive; warnings e quebra futura; `Query.get` some na API 2.0.
Recommendation: T-10 — `datetime.now(timezone.utc)` e `db.session.get(Model, id)`.

[MEDIUM] N+1 queries
File: routes/task_routes.py:41-57
ID: AP-09
Description: `GET /tasks` faz `Task.query.all()` e, por item, `User.query.get(t.user_id)` e `Category.query.get(t.category_id)`. `GET /users` usa `len(u.tasks)` (lazy). `GET /categories` conta tasks por categoria em loop (`report_routes.py:163`).
Impact: 1+2N queries na listagem principal da API.
Recommendation: T-08 — `joinedload(Task.user, Task.category)` e `GROUP BY` para counts.

[MEDIUM] Missing validation / deps não usadas
File: requirements.txt:4-6
ID: AP-10
Description: `marshmallow` e `python-dotenv` listados e nunca importados. Validação manual duplicada em POST/PUT de tasks. `type(tags) == list` (task_routes.py:141).
Impact: Dependências mortas; mensagens e regras divergem entre endpoints.
Recommendation: schemas Marshmallow + `isinstance`; `load_dotenv()` no boot.

[MEDIUM] Relatórios e categorias no mesmo blueprint
File: routes/report_routes.py:157-223
ID: AP-05
Description: CRUD de `/categories` vive em `report_routes.py`, misturando reporting com cadastro de categoria.
Impact: Fronteira de domínio errada (View de relatório alterando catálogo).
Recommendation: T-05 — category no report controller separado ou próprio controller; views só roteiam.

[MEDIUM] Delete sem invariante de categoria
File: routes/report_routes.py:211-223
ID: AP-10
Description: `DELETE /categories/<id>` remove a categoria sem tratar tasks órfãs (`category_id` FK nullable, mas dados ficam inconsistentes para a UI).
Impact: Tasks apontam para categoria inexistente.
Recommendation: nullificar `category_id` ou restringir delete se houver tasks.

[LOW] Dead code / unused imports
File: app.py:7
ID: AP-12
Description: `import os, sys, json, datetime` em app.py — só `datetime` é usado. `routes/task_routes.py:7` importa `json, os, sys, time` sem uso. `requests` no requirements sem import. `process_task_data` e `generate_id` (helpers.py:31-34 com import inline de uuid) nunca são usados pelas rotas.
Impact: Ruído e falsa impressão de I/O/JSON no entrypoint.
Recommendation: T-12 — remover imports e funções mortas.

[LOW] Magic numbers / poor naming
File: routes/task_routes.py:96-114
ID: AP-11
Description: Limites `len(title) < 3`, `> 200`, `priority < 1 or > 5` repetidos. `MIN_PASSWORD_LENGTH = 4` em helpers (linha 114) não é aplicado de um único lugar nas rotas de user (copia `len(password) < 4`).
Impact: Regras divergentes se um lado for atualizado.
Recommendation: constantes em `config/settings.py`.

[LOW] Nested overdue conditionals
File: models/task.py:50-60
ID: AP-11
Description: `is_overdue` com 4 níveis de if/else booleanos; a mesma árvore está copiada nas rotas em vez de reutilizar o método.
Impact: Bugs de timezone/status corrigidos num lugar e esquecidos noutro.
Recommendation: um método no model e serialização no controller.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y (execução do desafio — confirmação implícita)

Notas da Fase 3
- Estrutura evoluiu (não foi destruída): `models/` permanece; `routes/` virou `views/` + `controllers/`.
- Contrato HTTP preservado (`/tasks`, `/users`, `/login`, `/reports/*`, `/categories`, `/health`).
- Login deixa de devolver password; token passa a ser assinado com SECRET_KEY.
