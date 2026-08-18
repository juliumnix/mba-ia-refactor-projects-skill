# Template de relatório de auditoria (Fase 2)

Imprima o relatório neste formato. Não invente seções extra no lugar destas. É permitido adicionar uma nota curta no final (ex.: endpoints que serão removidos na Fase 3 por serem a falha).

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta / package.json name>
Stack:   <Linguagem + Framework>
Files:   <N> analyzed | ~<LOC> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[CRITICAL] <título curto alinhado ao catálogo>
File: <path>:<linha ou start-end>
ID: AP-XX
Description: <o que o código faz, com evidência>
Impact: <risco concreto>
Recommendation: <transformação do playbook, 1-3 frases>

[HIGH] ...
[MEDIUM] ...
[LOW] ...

================================
Total: <n> findings
================================
```

## Regras de preenchimento

- **Ordem:** todos os CRITICAL, depois HIGH, MEDIUM, LOW.
- **Título:** use o nome do catálogo (`God Class / God File`, `Hardcoded Secrets`, `SQL Injection`, `Deprecated API: datetime.utcnow`, …).
- **File:** caminho relativo à raiz do projeto. Linhas reais, conferidas no arquivo. Intervalo `12-48` quando o smell ocupa um bloco.
- **ID:** um de AP-01..AP-12.
- **Description:** cite trecho ou comportamento; nada de "código ruim".
- **Impact:** manutenção, segurança, performance ou teste — escolha o eixo principal.
- **Recommendation:** aponte a transformação (T-01..T-10) quando couber.

## Contagem

`Summary` deve bater com o número de blocos `Findings`. `Total:` é a soma.

Mínimo de aceite da skill: ≥5 findings e ≥1 CRITICAL ou HIGH. Se após a varredura houver menos, releia o catálogo; projetos desta skill sempre têm pelo menos esse volume.

## Após o relatório

Imprima exatamente:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Não execute a Fase 3 antes da resposta afirmativa.
