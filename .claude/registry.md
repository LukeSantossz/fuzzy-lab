# Registro de Projeto — Estado e Histórico

> Este arquivo contém o estado atual e histórico do projeto. É atualizado pelo agente ao final de cada implementação.
> As **regras** sobre como atualizar este registro estão em `.claude/rules/08-registro-projeto.md`.

---

## Informações do Projeto

- **Nome:** fuzzy-lab
- **Stack:** Python 3.10+, NumPy, scikit-fuzzy, PyTorch (ANFIS)
- **Repositório:** lucas/fuzzy-lab
- **Estrutura:** src layout com subpacotes `fis` (ativo), `anfis` (scaffold), `timeseries` (placeholder)

## Histórico de Implementações

> Registro de conclusões. Cada entrada representa uma task finalizada. O agente adiciona uma nova linha após cada task concluída. Nunca remova entradas anteriores.

| # | Data | Task | Complexidade | Escopo Alterado | Resultado | Observações |
|---|------|------|--------------|-----------------|-----------|-------------|
| 1 | 2026-03-18 | TASK-001 — Migração estrutura pacote | major | 8 arquivos — estrutura raiz | aprovado | Subpacotes fis, anfis, timeseries criados |
| 2 | 2026-03-18 | TASK-002 — Membership consequentes | minor | 2 arquivos — fis/mamdani | aprovado | 4 consequentes (sp, wh, ir, bp) |
| 3 | 2026-03-26 | TASK-003 — Regras pulverização | minor | 1 arquivo — notebook | aprovado | 11 regras de spray |
| 4 | 2026-03-26 | TASK-004 — Regras water/irrigation | minor | 2 arquivos — fis | aprovado | 6 regras water_stress + 3 irrigation |
| 5 | 2026-03-26 | TASK-005 — Regras produtividade | minor | 1 arquivo — notebook | aprovado | 7 regras cruzando múltiplos inputs |
| 6 | 2026-03-26 | TASK-006 — Validação universos | minor | 2 arquivos — notebook, figures | aprovado | Visualizações salvas |
| 7 | 2026-04-15 | TASK-007 — Migração para módulo | major | 3 arquivos — fis | aprovado | API pública build_system/run_inference |
| 8 | 2026-04-20 | TASK-008 — Testes + README | minor | 4 arquivos — tests, README | aprovado | 24 testes passando |
| 9 | 2026-04-25 | TASK-009 — Scaffold ANFIS | minor | 5 arquivos — anfis | aprovado | Stubs NotImplementedError |
| 10 | 2026-05-07 | TASK-000 — Bootstrap .claude | major | 2 arquivos — .claude | aprovado | Hooks instalados, histórico sincronizado |
| 11 | 2026-05-07 | TASK-011 — Limpeza estrutura | minor | 6 arquivos — src, tests, docs | aprovado | 3 vazios deletados, CLAUDE.md simplificado |
| 12 | 2026-05-07 | TASK-010 — Dataset treinamento | minor | 2 arquivos — scripts, data | aprovado | 1012 amostras, checklist agêntico aplicado |

## Estado da Codebase

> Atualizado a cada implementação ou verificação pós-pull. Reflete o snapshot mais recente do projeto.

- **Última atualização:** 2026-05-07
- **Último responsável:** agente (sessão TASK-010)
- **Branch ativa:** dev
- **Dependências alteradas recentemente:** nenhuma
- **Testes passando:** sim — 24 testes (pytest)
- **Divergências externas pendentes:** nenhuma
- **Última task concluída:** TASK-010 — Dataset treinamento ANFIS

## Pendências Conhecidas

- Próximo passo: implementar treinamento ANFIS usando dataset gerado
- Warnings de depreciação no skfuzzy (np.maximum com >2 args)

## Decisões Técnicas Relevantes

> Decisões tomadas durante implementações que afetam futuras tasks. Inclua justificativa breve.

| Data | Decisão | Justificativa |
|------|---------|---------------|
| 2026-03-18 | src layout com setuptools | Padrão moderno, isolamento de imports, compatibilidade com pip install -e |
| 2026-04-15 | Rule registry em mamdani.py | Permite seleção de subconjuntos de regras via config["rule_groups"] |
| 2026-04-15 | Variáveis em português | Domínio agrícola brasileiro, consistência com terminologia técnica local |
| 2026-04-25 | ANFIS espelha interface FIS | Mesma API (build_system, run_inference) para troca transparente |

## Padrões Recorrentes Observados

| Padrão | Frequência | Impacto | Ação Corretiva |
|--------|------------|---------|----------------|
| Warnings skfuzzy depreciação | toda execução | baixo | aguardar update skfuzzy ou suprimir warnings |

---

## Notas de Sessão

> Espaço para anotações pontuais sobre contextos que influenciam futuras sessões.

- **2026-05-07:** Bootstrap do sistema `.claude/`. Histórico migrado do CLAUDE.md. Hooks instalados.
