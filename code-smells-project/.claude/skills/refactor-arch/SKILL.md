---
name: refactor-arch
description: >
  Analisa, audita e refatora qualquer backend para o padrão MVC. Detecta
  linguagem, framework e arquitetura; classifica anti-patterns (CRITICAL/HIGH/MEDIUM/LOW)
  com arquivo e linha; gera relatório de auditoria; reestrutura Models, Views/Routes
  e Controllers; valida boot e endpoints. Use when the user invokes /refactor-arch,
  pede auditoria arquitetural, code smells, refatoração MVC, ou revisão de projeto
  legado em Python/Flask, Node.js/Express ou outra stack de API.
---

# refactor-arch

Você é um especialista em arquitetura de software, segurança de APIs e refatoração para MVC + SOLID. Esta skill é **agnóstica de tecnologia**: nunca assuma Flask, Express ou um nome de pasta específico. Detecte a stack pelos artefatos do projeto atual e aplique as mesmas 3 fases.

## Como usar os arquivos de referência

Carregue sob demanda (progressive disclosure). Não invente regras que não estejam neles.

| Fase | Arquivo | Quando ler |
|------|---------|------------|
| 1 | [references/project-analysis.md](references/project-analysis.md) | Antes de imprimir o resumo da stack |
| 2 | [references/anti-patterns.md](references/anti-patterns.md) | Antes de varrer o código |
| 2 | [references/deprecated-apis.md](references/deprecated-apis.md) | Ao procurar AP-08 (APIs obsoletas) |
| 2 | [references/report-template.md](references/report-template.md) | Antes de emitir o relatório |
| 3 | [references/mvc-guidelines.md](references/mvc-guidelines.md) | Depois da confirmação do humano |
| 3 | [references/refactoring-playbook.md](references/refactoring-playbook.md) | Durante as transformações |

Escopo: ignore `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `dist/`, `build/`, `.git/`, `*.db`.

## Regras globais

- Fases **sequenciais**. Não pule. Não misture auditoria com escrita de código.
- Fase 1 e Fase 2 são **somente leitura**. Zero criação, edição ou deleção de arquivos.
- Cada finding precisa de **arquivo e linhas exatas** (`path:start-end` ou `path:line`).
- Findings ordenados por severidade: CRITICAL → HIGH → MEDIUM → LOW. Empate: ordem de arquivo.
- Preserve o **contrato HTTP público** (paths, métodos, status e formato JSON que clientes já usam), salvo endpoints cuja existência é ela mesma uma falha de segurança (SQL cru, dump de senha). Documente qualquer remoção no relatório.
- Não acoplar a skill a um repositório: sinais de detecção são estruturais (concatenação SQL, `SECRET_KEY = "..."`, query dentro de loop), nunca "o arquivo models.py deste desafio".

---

## Fase 1 — Análise do projeto

1. Leia `references/project-analysis.md`.
2. Identifique a raiz do projeto (diretório de trabalho atual).
3. Detecte linguagem, framework + versão, dependências, domínio, arquitetura atual, arquivos-fonte e tabelas/coleções.
4. Imprima **exatamente** este bloco (preencha os campos; não omita nenhum):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework e versão>
Dependencies:  <lista curta>
Domain:        <domínio de negócio em 1 linha>
Architecture:  <1-2 frases sobre camadas atuais>
Source files:  <N> files analyzed
DB tables:     <tabelas ou "n/a">
================================
```

5. Só então avance para a Fase 2.

---

## Fase 2 — Auditoria

1. Leia `references/anti-patterns.md` e `references/report-template.md`.
2. Varra **todo** o código-fonte no escopo. Cruze cada arquivo com o catálogo AP-01..AP-12.
3. Produza o relatório no formato do template. Mínimo: **5 findings**, sendo pelo menos **1 CRITICAL ou HIGH**. Se APIs deprecated existirem, inclua pelo menos um finding AP-08.
4. Imprima o relatório completo no terminal.
5. **PARE. Não modifique arquivo algum.** Peça confirmação com o texto:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

6. Se a resposta não for afirmativa (`y`, `yes`, `sim`), encerre sem alterar o código. Se for afirmativa, avance para a Fase 3.

---

## Fase 3 — Refatoração e validação

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. Adapte a estrutura-alvo à stack detectada (Flask Blueprints vs Express Router). Se o projeto já tiver `models/` ou `routes/`, **evolua** — não apague organização útil.
3. Aplique as transformações do playbook para cada finding da Fase 2.
4. Extraia configuração (sem segredos no código). Centralize error handling. Deixe um composition root claro (`app.py` / `app.js` / equivalente).
5. Remova ou desative os arquivos legados que foram substituídos para não deixar dois sistemas paralelos.
6. **Valide** (não declare sucesso sem evidência):
   - Instale dependências se necessário.
   - Suba a aplicação; confirme boot sem traceback.
   - Dispare os endpoints públicos originais (GET de listagem, health, e pelo menos um POST representativo). Todos devem responder (não connection refused / 500 de regressão).
   - Recoloque o catálogo: anti-patterns CRITICAL/HIGH originais devem ter sido eliminados ou mitigados.
7. Imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore de diretórios>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Marque com `✗` qualquer item que falhou e descreva o restante do trabalho. Não finja validação.

## Se algo for ambíguo

Prefira a interpretação que (1) preserva o contrato HTTP público e (2) reduz severidade de segurança. Nunca deixe SQL concatenado, senha em texto plano ou secretos no código "para não quebrar o cliente".
