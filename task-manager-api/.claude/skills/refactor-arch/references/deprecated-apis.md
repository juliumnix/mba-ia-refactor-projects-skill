# Referência rápida — APIs deprecated (AP-08)

Complemento de `anti-patterns.md`. Use na Fase 2 para não perder detecção e na Fase 3 junto de T-10.

## Python

| Deprecated / legado | Substituição | Notas |
|---------------------|--------------|-------|
| `datetime.datetime.utcnow()` | `datetime.now(timezone.utc)` | Removido como recomendação desde 3.12; retorna naive datetime |
| `datetime.datetime.utcfromtimestamp` | `datetime.fromtimestamp(ts, tz=timezone.utc)` | Idem |
| `Model.query.get(pk)` (Flask-SQLAlchemy 3 / SA 2) | `db.session.get(Model, pk)` | `Query.get` emite deprecation |
| `hashlib.md5` / `sha1` para senha | `werkzeug.security` / `bcrypt` / `argon2` | MD5 não é "só deprecated": é inseguro (AP-07) |
| `flask.ext.*` | `flask_*` packages | API Flask 0.x |
| `app.run(debug=True)` hardcoded em produção | `DEBUG` via env; não ligar debug em 0.0.0.0 por padrão | Superfície de debugger |

## Node.js / Express

| Deprecated / legado | Substituição | Notas |
|---------------------|--------------|-------|
| `sqlite3.verbose()` | `require("sqlite3")` | Verbose só para debug local |
| Callbacks aninhados no driver SQL | `util.promisify` ou `sqlite` wrapper | Evita callback hell (AP-05/AP-08) |
| `new Buffer()` | `Buffer.from` | Deprecated no Node |
| `req.param()` | `req.params` / `req.body` / `req.query` | Express 4+ |
| Body parser separado `body-parser` em Express 4.16+ | `express.json()` | Já preferível |
| `var` em módulo novo | `const` / `let` | Qualidade; LOW se isolado |

## Como reportar

```
[MEDIUM] Deprecated API: datetime.utcnow
File: models/task.py:15-16
ID: AP-08
Description: created_at/updated_at usam datetime.utcnow (datetime naive, deprecated).
Impact: timestamps sem timezone; quebra futura em Python 3.12+.
Recommendation: T-10 — datetime.now(timezone.utc) e helpers utcnow().
```
