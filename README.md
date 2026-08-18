# Desafio Skills — refactor-arch

Skill de auditoria e refatoração arquitetural para Claude Code. Analisa qualquer backend, classifica anti-patterns (CRITICAL → LOW) e reestrutura o projeto para MVC, preservando o contrato HTTP público.

Ferramenta: **Claude Code** (`claude "/refactor-arch"`).
Skill: `.claude/skills/refactor-arch/` (copiada nos 3 projetos-alvo).

---

## A) Análise Manual

Antes de escrever a skill, os três projetos foram lidos arquivo a arquivo. Abaixo estão os problemas de maior impacto (mínimo exigido: 5 por projeto, com ≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW). A varredura completa está em [`reports/`](reports/).

### Projeto 1 — `code-smells-project/` (Python + Flask 3.1.1, e-commerce SQLite)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | SQL Injection por concatenação e `POST /admin/query` | `models.py:28`, `app.py:59-78` | Input vira SQL; o endpoint admin executa qualquer comando |
| CRITICAL | Credenciais hardcoded e senha em claro | `app.py:7`, `database.py:75-82` | SECRET_KEY e senhas de seed no git |
| CRITICAL | God file (`models.py` ~315 linhas, 4 domínios) | `models.py:1-315` | Mudança de pedido quebra produto/usuário |
| HIGH | Conexão SQLite global + `check_same_thread=False` | `database.py:4-10` | Estado compartilhado, testes e threads inseguros |
| MEDIUM | N+1 em listagem de pedidos | `models.py:171-233` | Query por item × produto |
| MEDIUM | `/admin/reset-db` sem autenticação | `app.py:47-56` | POST anônimo zera o banco |
| LOW | Magic numbers no relatório de vendas | `models.py:256-262` | Regras de desconto espalhadas |
| LOW | `print` no lugar de logging; `id` sombreia builtin | `controllers.py:8` | Ruído operacional e leitura ruim |

### Projeto 2 — `ecommerce-api-legacy/` (Node.js + Express 4, LMS + checkout)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | God class `AppManager` | `src/AppManager.js:4-139` | Schema, HTTP, pagamento e relatório no mesmo objeto |
| CRITICAL | Segredos `pk_live_` / senha de DB no código | `src/utils.js:1-7` | Gateway “live” versionado |
| HIGH | `badCrypto` (Base64 truncado) | `src/utils.js:17-23` | Não é hash; senhas reversíveis |
| HIGH | Callback hell no checkout | `src/AppManager.js:28-77` | Erros parciais e fluxo ilegível |
| MEDIUM | N+1 no relatório financeiro | `src/AppManager.js:80-128` | 1 query por curso × matrícula × user × payment |
| MEDIUM | DELETE de usuário deixa órfãos | `src/AppManager.js:131-137` | Integridade referencial quebrada |
| LOW | Nomes `u`, `e`, `p`, `cid`, `cc` | `src/AppManager.js:29-33` | Contrato HTTP opaco |
| LOW | `sqlite3.verbose()` e `totalRevenue` morto | `AppManager.js:1`, `utils.js:10` | Debug em produção + estado morto |

### Projeto 3 — `task-manager-api/` (Python + Flask 3.0 + SQLAlchemy, organização parcial)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | Hash MD5 de senha | `models/user.py:29-32` | Algoritmo quebrado para credenciais |
| CRITICAL | `to_dict()` e login devolvem `password` | `models/user.py:16-25`, `routes/user_routes.py:207-210` | Hash vaza em JSON |
| HIGH | Rotas gordas, sem controllers | `routes/task_routes.py` | HTTP + SQL + overdue no mesmo handler |
| HIGH | `datetime.utcnow` e `Query.get` deprecated | `models/task.py:15`, `routes/task_routes.py:67` | API SQLAlchemy 2 / Python 3.12 |
| MEDIUM | N+1 em `GET /tasks` (User/Category por item) | `routes/task_routes.py:41-57` | Listagem principal cara |
| MEDIUM | marshmallow e python-dotenv no requirements, nunca usados | `requirements.txt:4-6` | Validação e config continuam manuais |
| LOW | Imports mortos (`os, sys, json`) | `app.py:7`, `routes/task_routes.py:7` | Ruído |
| LOW | `process_task_data` nunca chamado; `type(x) == list` | `utils/helpers.py:57` | Dead code e comparação de tipos frágil |

---

## B) Construção da Skill

### Decisões de design

A skill segue progressive disclosure do Claude Code:

1. **YAML frontmatter** — `name: refactor-arch` e `description` em terceira pessoa, com gatilhos (`/refactor-arch`, auditoria MVC, legado Flask/Express).
2. **`SKILL.md`** — só o protocolo das 3 fases (o que imprimir, quando parar, o que validar). Não duplica o catálogo.
3. **`references/`** — conhecimento de domínio carregado sob demanda.

| Arquivo | Papel |
|---|---|
| `references/project-analysis.md` | Heurísticas de linguagem/framework/DB/arquitetura |
| `references/anti-patterns.md` | Catálogo AP-01..AP-12 com sinais e severidade |
| `references/deprecated-apis.md` | Tabela de APIs obsoletas (obrigatório AP-08) |
| `references/report-template.md` | Formato exato do relatório da Fase 2 |
| `references/mvc-guidelines.md` | Camadas alvo e mapeamento Flask ↔ Express |
| `references/refactoring-playbook.md` | T-01..T-10 com antes/depois Python e JS |

Fases **1 e 2 são somente leitura**. A Fase 2 imprime `Proceed with refactoring (Phase 3)? [y/n]` e não escreve arquivo algum até a confirmação.

### Anti-patterns no catálogo (e por quê)

| ID | Padrão | Severidade | Motivo de inclusão |
|---|---|---|---|
| AP-01 | God Class / God File | CRITICAL | Presente nos 3 projetos em graus diferentes |
| AP-02 | Hardcoded Secrets | CRITICAL | SECRET_KEY, SMTP, `pk_live_` |
| AP-03 | SQL Injection | CRITICAL | Concatenação SQL (projeto 1) |
| AP-04 | Sensitive Data Exposure | CRITICAL | Health, `to_dict`, logs de cartão |
| AP-05 | Fat Controller | HIGH | Rotas/handlers fazendo SQL |
| AP-06 | Global Mutable State | HIGH | `db_connection`, `globalCache` |
| AP-07 | Weak crypto | HIGH | MD5, texto plano, `badCrypto` |
| AP-08 | Deprecated APIs | MEDIUM/HIGH | `utcnow`, `Query.get`, `sqlite3.verbose` |
| AP-09 | N+1 | MEDIUM | Pedidos, relatório LMS, tasks |
| AP-10 | Missing validation | MEDIUM | Admin aberto, deps não usadas |
| AP-11 | Magic numbers / naming | LOW | Descontos, `u/e/p`, priority 1–5 |
| AP-12 | Dead code | LOW | Imports e funções órfãs |

AP-08 é explícito: a skill **deve** reportar APIs deprecated quando existirem, com substituto moderno.

### Agnóstica de tecnologia

- Detecção por artefato (`requirements.txt`, `package.json`, imports), nunca pelo nome da pasta.
- Sinais estruturais (`"SELECT …" + str(id)`, query dentro de `for`, `SECRET_KEY = "..."`), não “o models.py deste desafio”.
- Playbook com o **mesmo T-xx** em Python e JavaScript.
- MVC mapeado: Flask Blueprint = Express Router = View; factory `create_app` nos dois.
- Projeto 3 **evolui** `models/` existentes em vez de apagar organização útil.

A skill foi copiada identicamente para os 3 projetos. Se só funcionasse em um, estaria acoplada.

### Desafios

- **Contrato HTTP vs segurança:** `POST /admin/query` era um endpoint público cuja existência é a falha. A skill remove esse tipo de rota e documenta no relatório.
- **SQLite `:memory:` no Node** exige a mesma instância de `Database` injetada (DI), senão o seed some entre requests — reforçou T-06.
- **Projeto 3 já tinha pastas:** o playbook precisa de um modo “evoluir”, senão a Fase 3 recria um segundo app paralelo.
- **Confirmação da Fase 2** é obrigatória no SKILL.md; neste repositório a Fase 3 foi executada após a auditoria (desafio pede o código já refatorado). Os relatórios registram `> y`.

---

## C) Resultados

### Resumo das auditorias (Fase 2)

| Projeto | Stack detectada | Findings | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|---|---|
| 1 `code-smells-project` | Python + Flask 3.1.1 | 14 | 5 | 3 | 3 | 3 |
| 2 `ecommerce-api-legacy` | Node.js + Express 4.18 | 12 | 3 | 3 | 3 | 3 |
| 3 `task-manager-api` | Python + Flask 3.0 + SQLAlchemy | 13 | 3 | 3 | 4 | 3 |

Relatórios: [audit-project-1.md](reports/audit-project-1.md), [audit-project-2.md](reports/audit-project-2.md), [audit-project-3.md](reports/audit-project-3.md).

### Antes / depois

**Projeto 1**

```
antes: app.py, controllers.py, models.py, database.py

depois:
app.py                    # entry
src/app.py                # composition root
src/config/settings.py
src/models/{produto,usuario,pedido}_model.py
src/views/*_views.py
src/controllers/*_controller.py
src/middlewares/error_handler.py
src/database.py
```

**Projeto 2**

```
antes: src/app.js, src/AppManager.js, src/utils.js

depois:
src/app.js
src/config/settings.js
src/models/*.js
src/views/apiRoutes.js
src/controllers/*.js
src/middlewares/errorHandler.js
src/database.js
src/lib/{crypto,cache}.js
```

**Projeto 3**

```
antes: app.py, models/, routes/, services/, utils/

depois:
app.py                    # factory create_app
config/settings.py
models/                   # mantidos, sem MD5/utcnow
views/                    # rotas magras (ex-routes/)
controllers/
middlewares/error_handler.py
schemas/                  # marshmallow
```

### Checklist de validação

#### Projeto 1 — code-smells-project

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio descrito corretamente (e-commerce)
- [x] Número de arquivos analisados condiz (4)

Fase 2 — Auditoria
- [x] Relatório segue o template
- [x] Cada finding tem arquivo e linhas
- [x] Ordenados CRITICAL → LOW
- [x] Mínimo de 5 findings (14)
- [x] APIs deprecated incluídas (DEBUG hardcoded / debugger)
- [x] Pausa antes da Fase 3 (documentada no relatório)

Fase 3 — Refatoração
- [x] Diretórios MVC
- [x] Config extraída (`.env.example`)
- [x] Models por domínio
- [x] Views/rotas separadas
- [x] Controllers de fluxo
- [x] Error handling centralizado
- [x] Entry point `app.py` → `create_app()`
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem (`/health`, `/produtos`, `/login`, …)

#### Projeto 2 — ecommerce-api-legacy

Fase 1 — Análise
- [x] Linguagem JavaScript/Node.js
- [x] Framework Express 4.18.2
- [x] Domínio LMS + checkout
- [x] 3 arquivos-fonte analisados

Fase 2 — Auditoria
- [x] Template + linhas exatas
- [x] CRITICAL → LOW
- [x] ≥5 findings (12) com CRITICAL/HIGH
- [x] Deprecated `sqlite3.verbose` + callbacks
- [x] Confirmação Fase 3 documentada

Fase 3 — Refatoração
- [x] MVC + config + models + views + controllers
- [x] Sem secretos no código (env)
- [x] Error handler Express
- [x] `npm start` sobe na porta 3000
- [x] `POST /api/checkout` e `GET /api/admin/financial-report` OK

#### Projeto 3 — task-manager-api

Fase 1 — Análise
- [x] Python + Flask
- [x] Domínio Task Manager
- [x] Arquivos reais da árvore parcial (models/routes/services)

Fase 2 — Auditoria
- [x] Findings mesmo com organização parcial (13)
- [x] ≥1 CRITICAL (MD5, vazamento de password)
- [x] Deprecated `utcnow` / `Query.get`

Fase 3 — Refatoração
- [x] MVC evolutivo (models preservados)
- [x] Config + marshmallow + dotenv
- [x] Boot + `/tasks`, `/login`, `/health` OK

### Logs das aplicações após a refatoração

**Projeto 1 (Flask e-commerce)**

```
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
127.0.0.1 - - "GET /health HTTP/1.1" 200 -
127.0.0.1 - - "GET /produtos HTTP/1.1" 200 -
127.0.0.1 - - "POST /login HTTP/1.1" 200 -
```

`GET /health` → `{"status":"ok","database":"connected",...}` (sem `secret_key`).
`POST /login` `{email, senha}` do admin → `200` com dados públicos (sem hash).

**Projeto 2 (Express LMS)**

```
LMS API rodando na porta 3000...
checkout_payment_attempt { courseId: 2, last4: '4444' }
```

`GET /api/admin/financial-report` → JSON por curso.
`POST /api/checkout` com cartão Visa de teste → `{"msg":"Sucesso","enrollment_id":2}`.

**Projeto 3 (Flask Task Manager)**

```
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
127.0.0.1 - - "GET /health HTTP/1.1" 200 -
127.0.0.1 - - "GET /tasks HTTP/1.1" 200 -
127.0.0.1 - - "POST /login HTTP/1.1" 200 -
```

`GET /tasks` devolve 10 itens com `user_name` (joinedload). Login **não** inclui `password`.

### Comportamento nas stacks

A mesma skill descreveu Fase 1 de Flask monolítico, Express God Object e Flask parcialmente organizado. A Fase 3 não forçou `src/` no projeto 3 (já havia `models/`); no 1 e no 2 a árvore nasceu do zero. Crypto, config e error handler aparecem nos três, com APIs nativas de cada runtime (Werkzeug vs bcryptjs, Blueprint vs Router).

---

## D) Como executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude`)
- Python 3.12+ e pip (projetos 1 e 3)
- Node.js 18+ e npm (projeto 2)

A skill vive em cada projeto, em `.claude/skills/refactor-arch/`.

### Invocar a skill

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A Fase 2 **para** e pede:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Responda `y` somente depois de revisar o relatório. Neste repositório a Fase 3 já foi aplicada; rode a skill de novo só se quiser reauditar o código atual (espera-se poucos findings residuais LOW).

### Subir as APIs refatoradas

```bash
# Projeto 1
cd code-smells-project
pip install -r requirements.txt
python app.py
# http://localhost:5000/health  /produtos  /login

# Projeto 2
cd ecommerce-api-legacy
npm install
npm start
# http://localhost:3000/api/admin/financial-report
# POST /api/checkout  (ver api.http)

# Projeto 3
cd task-manager-api
pip install -r requirements.txt
python seed.py
python app.py
# http://localhost:5000/health  /tasks  /login
```

Copie `.env.example` e defina `SECRET_KEY` (e `PAYMENT_GATEWAY_KEY` no projeto 2) antes de qualquer ambiente compartilhado.

### Como validar a refatoração

1. O processo sobe sem traceback.
2. Health (ou o GET raiz) responde 200.
3. Um GET de listagem e um POST representativo (login ou checkout) respondem com o mesmo shape JSON de antes — **exceto** campos inseguros removidos (`senha`, `secret_key`, `password` no user).
4. Não deve restar SQL concatenado, MD5 de senha, `badCrypto` nem God class.

---

## Estrutura do repositório

```
├── README.md
├── reports/
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
├── code-smells-project/
│   ├── .claude/skills/refactor-arch/
│   ├── app.py
│   └── src/          # MVC
├── ecommerce-api-legacy/
│   ├── .claude/skills/refactor-arch/
│   └── src/          # MVC
└── task-manager-api/
    ├── .claude/skills/refactor-arch/
    ├── config/ controllers/ views/ models/ middlewares/
    └── app.py
```
