# Análise de projeto (Fase 1)

Heurísticas agnósticas para detectar linguagem, framework, banco e arquitetura. Avalie **evidência de arquivo**, não o nome da pasta do repositório.

## 1. Linguagem

Percorra a raiz e `src/` (e equivalentes). Use o primeiro match forte; confirme com um segundo sinal.

| Sinal | Linguagem |
|-------|-----------|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | Python |
| `package.json`, `package-lock.json`, `*.js` / `*.ts` (sem `deno.json`) | JavaScript / TypeScript |
| `go.mod`, `*.go` | Go |
| `Gemfile`, `*.rb` | Ruby |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `Cargo.toml`, `*.rs` | Rust |
| `composer.json`, `*.php` | PHP |
| `*.csproj`, `Program.cs` | C# |

Conte **arquivos-fonte** com extensão da linguagem detectada, excluindo vendor/venv/node_modules. Esse número vai em `Source files`.

## 2. Framework e versão

Leia o manifest e os imports/requires do entry point.

### Python

- `from flask import` / `Flask(` → Flask. Versão: pin em `requirements.txt` (`flask==3.1.1`) ou metadado equivalente.
- `FastAPI(` / `from fastapi` → FastAPI.
- `django` em requirements ou `manage.py` → Django.
- `flask_sqlalchemy` / `SQLAlchemy(` → anote o ORM como dependência, não como framework principal.

### Node.js

- `require('express')` / `from 'express'` → Express. Versão: `dependencies.express` em `package.json`.
- `fastify`, `koa`, `nest`, `hono` → o framework correspondente.

`Dependencies:` liste 3–8 libs relevantes (CORS, ORM, driver de banco, validação). Ignore devDependencies de tooling se não afetam runtime.

## 3. Banco de dados

| Sinal | Banco |
|-------|-------|
| `sqlite3`, `*.db`, `sqlite:///` | SQLite |
| `psycopg`, `postgres://`, `pg` | PostgreSQL |
| `pymongo`, `mongodb://` | MongoDB |
| `CREATE TABLE`, models SQLAlchemy/`sequelize.define` | Extraia nomes de tabelas |
| Nenhum persistência | `DB tables: n/a` |

Para SQLite/SQL, extraia tabelas de `CREATE TABLE`, `__tablename__`, ou `INSERT INTO`. Liste em `DB tables:` separadas por vírgula.

Memória (`:memory:`) ainda conta: descreva as tabelas criadas no boot.

## 4. Entry point e composição

Procure, nesta ordem: `if __name__ == "__main__"`, `app.run(`, `app.listen(`, campo `"main"` do `package.json`, `cmd/` em Go, `manage.py`.

O arquivo que instancia o framework é o **composition root** atual.

## 5. Domínio

Inferir do vocabulário (rotas, models, seeds), não do README se o código contradisser.

Exemplos de formulação (1 linha):

- Rotas `/produtos`, `/pedidos`, `/usuarios` → `E-commerce API (produtos, pedidos, usuários)`
- `/api/checkout`, `courses`, `enrollments` → `LMS API com fluxo de checkout (cursos, matrículas, pagamentos)`
- `/tasks`, `/users`, `/categories` → `Task Manager API (tarefas, usuários, categorias)`

## 6. Arquitetura atual

Classifique com base em **pastas e responsabilidades**, não em rótulos de arquivo.

| Evidência | Classificação |
|-----------|----------------|
| 1–5 arquivos na raiz misturando HTTP + SQL + regras | `Monolítica — tudo em N arquivos, sem separação de camadas` |
| Pasta `models/` + rotas que ainda fazem query/validação | `Parcialmente organizada — models/routes existem, mas a borda HTTP concentra regras` |
| `models/` + `views/`/`routes/` + `controllers/` com papéis claros | `MVC (ou próximo) — verificar vazamentos entre camadas` |
| God class única registrada nas rotas | `God Object — uma classe concentra persistência, HTTP e regras` |

Anote também: há config extraída? error handler global? DI ou globais?

## 7. Mapa rápido de camadas (para a Fase 3)

Preencha mentalmente (não precisa imprimir, mas use na auditoria):

- **View/Route:** onde o HTTP é declarado (`@app.route`, `app.get`, `Blueprint`, `Router`).
- **Controller:** orquestra o caso de uso. Se inexistente, as rotas *são* o controller gordo.
- **Model:** acesso a dados. Se SQL vive nas rotas, o model está ausente de fato.

## 8. Checklist da Fase 1 (não imprimir)

- [ ] Linguagem bate com as extensões
- [ ] Framework + versão extraídos do manifest quando existir
- [ ] Domínio descreve o negócio, não a pasta
- [ ] `Source files` é a contagem real (não um chute)
- [ ] Tabelas listadas ou `n/a`
