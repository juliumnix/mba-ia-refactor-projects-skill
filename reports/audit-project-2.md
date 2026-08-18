================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18.2
Dependencies:  sqlite3
Domain:        LMS API com fluxo de checkout (cursos, matrículas, pagamentos)
Architecture:  God Object — AppManager concentra persistência, HTTP e regras
Source files:  3 files analyzed
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] God Class / God File
File: src/AppManager.js:4-139
ID: AP-01
Description: A classe `AppManager` cria o schema SQLite, faz seed, registra rotas, processa checkout (usuário + pagamento + matrícula + audit) e monta relatório financeiro no mesmo objeto.
Impact: Qualquer alteração de checkout arrisca o relatório e o schema; zero fronteira MVC.
Recommendation: T-01 — models por tabela, controllers por caso de uso, Router em views/.

[CRITICAL] Hardcoded Secrets
File: src/utils.js:1-7
ID: AP-02
Description: `config` embute `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (prefixo live) e credenciais SMTP no código-fonte.
Impact: Segredo de gateway de pagamento versionado; risco de cobrança real se o mock for trocado.
Recommendation: T-02 — `src/config/settings.js` lendo `process.env`.

[CRITICAL] Sensitive Data Exposure
File: src/AppManager.js:45
ID: AP-04
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` grava PAN completo e a chave live no log. Seed grava senha `'123'` em claro (`AppManager.js:18`).
Impact: PCI/logs de cartão; credenciais de usuário no dump do banco.
Recommendation: T-04 — logar só last4; T-07 — hash de senha no seed.

[HIGH] Weak / homemade cryptography
File: src/utils.js:17-23
ID: AP-07
Description: `badCrypto` concatena 10.000 vezes um recorte de Base64 e corta 10 caracteres — não é hash, não tem salt, é determinístico e truncado.
Impact: Senhas reversíveis/colidíveis; não resiste a brute force.
Recommendation: T-07 — bcrypt (`bcryptjs.hash` / `compare`).

[HIGH] Global Mutable State / sem DI
File: src/utils.js:9-15
ID: AP-06
Description: `let globalCache = {}` e `let totalRevenue = 0` no módulo; `AppManager` instancia o DB no constructor e registra rotas no mesmo this.
Impact: Cache e “faturamento” globais entre requests; testes não isolam estado.
Recommendation: T-06 — factory `createApp({ db, config, cache })`.

[HIGH] Fat Controller / callback hell
File: src/AppManager.js:28-77
ID: AP-05
Description: O handler de `POST /api/checkout` aninha 4–5 callbacks sqlite3 (curso → usuário → insert user → enrollment → payment → audit) misturando HTTP e persistência.
Impact: Tratamento de erro inconsistente (`res.status(500).send("Erro DB")`); difícil raciocinar o fluxo.
Recommendation: T-05 + T-10 — controller async/await com models injetados.

[MEDIUM] N+1 queries
File: src/AppManager.js:80-128
ID: AP-09
Description: Relatório financeiro: `SELECT * FROM courses`, depois enrollments por curso, depois user e payment por matrícula, com contadores manuais `coursesPending`/`enrPending`.
Impact: Explosão de queries; risco de resposta duplicada ou hang se um callback falhar.
Recommendation: T-08 — um JOIN e agregação em memória.

[MEDIUM] Missing validation / superfície perigosa
File: src/AppManager.js:131-137
ID: AP-10
Description: `DELETE /api/users/:id` remove o usuário e responde que matrículas/pagamentos “ficaram sujos”. Checkout aceita `usr`/`eml`/`pwd`/`c_id` sem schema. Relatório admin sem auth.
Impact: Integridade referencial quebrada; contrato HTTP opaco.
Recommendation: delete em transação com cascade; validar body no controller.

[MEDIUM] Deprecated API: sqlite3.verbose
File: src/AppManager.js:1
ID: AP-08
Description: `require('sqlite3').verbose()` habilita stack traces extras do driver em todo o processo. Callbacks aninhados são o estilo legado frente a promisify/async.
Impact: Ruído e superfície de debug em “produção”; código difícil de manter.
Recommendation: T-10 — `require("sqlite3")` + wrapper promise.

[LOW] Magic numbers / poor naming
File: src/AppManager.js:29-33
ID: AP-11
Description: Identificadores `u`, `e`, `p`, `cid`, `cc`. Pagamento aprovado se `cc.startsWith("4")` (BIN Visa hardcoded).
Impact: Leitura ruim; regra de adquirente escondida.
Recommendation: nomes completos (`name`, `email`, `card`); constante `visaPrefix` em config.

[LOW] Dead code / unused export
File: src/utils.js:10
ID: AP-12
Description: `totalRevenue` é exportado e nunca atualizado/lido pelos handlers.
Impact: Estado morto que sugere um relatório que não existe.
Recommendation: remover o export; receita vem da tabela `payments`.

[LOW] Respostas HTTP inconsistentes
File: src/AppManager.js:35
ID: AP-11
Description: Mistura `res.status(400).send("Bad Request")` (texto) com `res.json({ msg })` no sucesso.
Impact: Clientes precisam tratar text/plain e JSON no mesmo recurso.
Recommendation: T-09 — error handler JSON único.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y (execução do desafio — confirmação implícita)

Notas da Fase 3
- Contrato preservado: `POST /api/checkout` (campos `usr`, `eml`, `pwd`, `c_id`, `card`), `GET /api/admin/financial-report`, `DELETE /api/users/:id`.
- Delete passou a remover enrollments/payments em transação.
- Logs de pagamento registram apenas `last4`.
