================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~781 lines of code

Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] God Class / God File
File: models.py:1-315
ID: AP-01
Description: Um único módulo concentra CRUD de produtos, usuários e pedidos, relatórios de vendas, busca dinâmica e atualização de estoque — SQL, regras de negócio e serialização no mesmo arquivo.
Impact: Impossível testar um domínio em isolamento; qualquer mudança de pedido arrisca produtos e usuários.
Recommendation: T-01 — separar em models/produto_model.py, usuario_model.py e pedido_model.py.

[CRITICAL] SQL Injection / query construída por string
File: models.py:28
ID: AP-03
Description: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` concatena identificadores na SQL. O mesmo padrão se repete em criar/atualizar produto (47-50, 57-60), login (109-111), pedidos (140-165, 174-193) e busca com LIKE (285-299).
Impact: Um cliente pode alterar ou extrair o banco inteiro via payload.
Recommendation: T-03 — placeholders `?` e tuplas de parâmetros.

[CRITICAL] SQL Injection via endpoint administrativo
File: app.py:59-78
ID: AP-03
Description: `POST /admin/query` lê `dados.get("sql")` e executa a string crua em `cursor.execute(query)` sem autenticação.
Impact: RCE lógico no banco (DROP, SELECT de senhas, UPDATE em massa) para qualquer chamador da API.
Recommendation: T-03 — remover a rota; operações admin devem ser nomeadas e autenticadas.

[CRITICAL] Hardcoded Secrets
File: app.py:7
ID: AP-02
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`. A mesma chave reaparece em `controllers.py:289`. Senhas de seed em texto plano em `database.py:75-82` (`admin123`, `123456`).
Impact: Compromete sessões/assinaturas e credenciais de contas de exemplo que imitam produção (`DEBUG = True` em app.py:8).
Recommendation: T-02 — `src/config/settings.py` + variáveis de ambiente; hash no seed (T-07).

[CRITICAL] Sensitive Data Exposure
File: controllers.py:276-289
ID: AP-04
Description: `GET /health` devolve `secret_key`, `debug`, `db_path` e `ambiente: producao`. `GET /usuarios` inclui o campo `senha` (`models.py:79-86`). Login compara senha em claro no SQL.
Impact: Qualquer health-check vaza o segredo da aplicação; listagem de usuários vaza credenciais.
Recommendation: T-04 — serializer público sem senha; health só com status/contagens.

[HIGH] Weak / homemade cryptography
File: models.py:109-111
ID: AP-07
Description: Autenticação faz `WHERE email = '" + email + "' AND senha = '" + senha + "'` — senha armazenada e comparada em texto plano (também no INSERT em 126-128).
Impact: Vazamento do banco equivale a comprometimento imediato de todas as contas.
Recommendation: T-07 — `werkzeug.security.generate_password_hash` / `check_password_hash`.

[HIGH] Global Mutable State / sem DI
File: database.py:4-10
ID: AP-06
Description: `db_connection = None` global com `sqlite3.connect(..., check_same_thread=False)` compartilhado por toda a aplicação.
Impact: Estado implícito, difícil de testar e inseguro em threads do Flask.
Recommendation: T-06 — conexão por request (`g.db`) e factory `create_app`.

[HIGH] Fat Controller / regras na borda HTTP
File: controllers.py:188-220
ID: AP-05
Description: `criar_pedido` valida HTTP, chama o model e dispara email/SMS/push via `print` no mesmo handler. `/health` ainda executa SQL direto (`264-274`).
Impact: Efeitos colaterais acoplados ao Flask; duplicação de try/except em cada função.
Recommendation: T-05 + T-09 — controller magro + NotificationService + error handler único.

[MEDIUM] N+1 queries
File: models.py:171-233
ID: AP-09
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem SELECT de pedidos, depois itens por pedido, depois nome do produto por item (loops com cursor2/cursor3).
Impact: Latência cresce com o número de pedidos × itens.
Recommendation: T-08 — JOIN único e agrupamento em memória.

[MEDIUM] Missing validation / superfície perigosa
File: app.py:47-56
ID: AP-10
Description: `POST /admin/reset-db` apaga todas as tabelas sem autenticação. Rotas de produto validam campos, mas `/admin/*` não tem middleware de auth.
Impact: Um POST anônimo zera o e-commerce.
Recommendation: T-09/T-10 — autenticar admin ou restringir a ambientes de teste documentados.

[MEDIUM] Deprecated API: Flask debug hardcoded
File: app.py:8
ID: AP-08
Description: `app.config["DEBUG"] = True` e `app.run(..., debug=True)` em `0.0.0.0` (app.py:89) expõem o debugger Werkzeug.
Impact: Debugger interativo em rede; API considerada obsoleta/perigosa para qualquer deploy.
Recommendation: T-10 — `DEBUG` via env, default false.

[LOW] Magic numbers / poor naming
File: models.py:256-262
ID: AP-11
Description: Faixas de desconto `10000/0.1`, `5000/0.05`, `1000/0.02` literais. Parâmetro `id` sombreia o builtin em vários métodos.
Impact: Regras de negócio escondidas; leitura e refatoração mais difíceis.
Recommendation: T-02 — `DISCOUNT_TIERS` em config; nomear `produto_id`.

[LOW] Dead code / logging via print
File: controllers.py:8
ID: AP-12
Description: `print("Listando " + str(len(produtos)) + " produtos")` e equivalentes em criar/deletar/login. Sem logger estruturado.
Impact: Ruído em stdout; sem níveis nem correlação de request.
Recommendation: substituir por `logging` no composition root.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y (execução do desafio — confirmação implícita)

Notas da Fase 3
- `POST /admin/query` foi removido (era a própria falha CRITICAL).
- `POST /admin/reset-db` permanece para reseed local, sem SQL arbitrário.
- Contrato público preservado: `/produtos`, `/usuarios`, `/login`, `/pedidos`, `/relatorios/vendas`, `/health`.
