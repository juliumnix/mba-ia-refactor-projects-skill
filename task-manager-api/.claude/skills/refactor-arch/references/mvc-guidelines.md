# Guidelines de arquitetura MVC alvo

O alvo é **MVC para APIs HTTP**, não MVC de templates server-side. "View" = a borda HTTP (rotas, serializers de resposta). Controllers orquestram. Models isolam persistência e invariantes do agregado.

## Estrutura canônica (adapte a extensão)

```
src/
├── config/          # settings a partir de env; nenhum secreto literal de produção
├── models/          # um módulo (ou classe) por agregado
├── views/           # declaração de rotas / routers / blueprints
├── controllers/     # casos de uso; sem SQL cru; sem Flask/Express se evitável
├── middlewares/     # error handler, auth, logging
└── app.py|app.js    # composition root: liga config, db, rotas, middleware
```

Nomes equivalentes aceitos (não invente uma quarta camada "service" só para duplicar o controller, a menos que o projeto já tenha services úteis — aí o controller chama o service, e o service não vaza HTTP).

## Responsabilidades

### Config

- Lê `os.environ` / `process.env` (dotenv opcional no boot).
- Expõe `SECRET_KEY`, `PORT`, `DATABASE_URL`, flags `DEBUG`.
- Fornece constantes de negócio nomeadas (limites, enums de status) — nada de magic number solto nas rotas.

### Models

- Schema, queries parametrizadas ou ORM, mapeamento linha → dict/objeto **sem** campos secretos.
- Regras que pertencem ao dado (hash de senha, `is_overdue`, estoque).
- **Não** importam Flask `request` nem `res` do Express.

### Views (Routes)

- Declaram path, método, status HTTP.
- Extraem parâmetros (`request.get_json()`, `req.params`) e delegam ao controller.
- Traduzem resultado do controller em JSON.
- **Não** abrem cursor SQL. **Não** calculam faturamento.

### Controllers

- Um controller por agregado ou caso de uso (produto, pedido, checkout, task).
- Validam entrada (ou chamam schema marshmallow/joi).
- Chamam models / services.
- Disparam efeitos colaterais (notificação) via dependência injetada, não `print` espalhado.
- **Não** registram rotas. **Não** guardam conexão global.

### Middlewares

- Error handler único: exceções de domínio → 4xx; bugs → 500 sem stack para o cliente.
- Auth, CORS, request id — aplicados no composition root.

### Composition root

- Cria o app, aplica middleware, registra views, inicializa DB.
- É o único lugar que "conhece todo mundo".
- Entry: `python -m src.app` / `python app.py` / `node src/app.js` / `npm start`.

## Mapeamento por stack

| Papel | Flask | Express |
|-------|-------|---------|
| View | `Blueprint` em `views/*.py` | `express.Router()` em `views/*.js` |
| Controller | funções/classes em `controllers/` | funções async em `controllers/` |
| Model | módulos SQL/ORM em `models/` | módulos com SQL parametrizado ou ORM |
| Errors | `@app.errorhandler` / `register_error_handlers(app)` | `app.use((err, req, res, next) => …)` |
| Config | `src/config/settings.py` | `src/config/settings.js` |

## Projeto já parcialmente organizado

Se existirem `models/`, `routes/`, `services/`:

1. Mantenha models; corrija vazamentos (senha em `to_dict`, MD5, deprecated APIs).
2. Transforme `routes/` gordas em views magras + `controllers/` novos.
3. Extraia `config/` e `middlewares/`.
4. Services que só enviam email podem permanecer; não os force a virar controller.
5. Não duplique a árvore: um único composition root.

## Contrato HTTP

Preserve paths e métodos públicos documentados pelo próprio app (índice `/`, `api.http`, prints de rotas). Status: 200/201 sucesso, 400 validação, 401 login, 404 not found, 409 conflito, 500 só para falha real.

**Exceção de segurança:** rota que executa SQL arbitrário, devolve `SECRET_KEY` ou senha em claro deve ser removida ou sanitizada. Documente no relatório da Fase 2.

## O que "pronto" significa

- Nenhum secreto no código-fonte (apenas env).
- Nenhum SQL concatenado com input.
- Nenhuma God class restando.
- Error handling em um único lugar.
- Aplicação sobe e os endpoints públicos respondem.
