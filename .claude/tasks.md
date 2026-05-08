# TASKS.md — Registro de Tasks para Implementação

> **Este arquivo é o ponto de entrada obrigatório para qualquer implementação.**
> Nenhum agente de IA pode modificar a codebase sem uma task formalmente registrada aqui.
> Consulte `.claude/rules/00-trava-seguranca.md` para as regras completas.

---

## Como Usar

1. Copie o template da Seção "Template de Task" abaixo.
2. Preencha todos os campos obrigatórios (marcados com `!`).
3. Adicione a task preenchida na Seção "Tasks Ativas".
4. Inicie a sessão com o agente informando o modo de operação desejado (Desenvolvimento, Review ou Tutor).
5. Ao concluir, mova a task para "Tasks Concluídas" com o resultado preenchido.

---

## Template de Task

```markdown
### TASK-[NNN]
- **Status:** pendente | em andamento | concluída | descartada | revertida
- **Modo:** desenvolvimento | review | tutor
- **Complexidade:** patch | minor | major
- **Data de criação:** [YYYY-MM-DD]

#### Objetivo (!obrigatório)
[Descreva de forma direta o que precisa ser feito. Uma frase clara.
Teste: se alguém ler apenas esta linha, entende o que será entregue?]

#### Contexto (!obrigatório)
[Por que essa mudança é necessária? Qual problema resolve?
Se houver link de issue, PR, ou card de projeto, inclua aqui.]

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:** [listar os arquivos ou áreas que serão tocados]
- **Dependências necessárias:** [novas dependências ou "nenhuma"]
- **Impacto em funcionalidades existentes:** [descrever ou "nenhum"]

#### Critérios de Aceite (!obrigatório)
[Liste as entregas concretas que definem a task como concluída.
Cada critério deve ser verificável — sim ou não, passou ou não passou.]
- [ ] [Critério 1]
- [ ] [Critério 2]
- [ ] [Critério 3]

#### Restrições (opcional)
[Limitações técnicas, de tempo, de escopo, ou decisões já tomadas que o agente deve respeitar.
Ex: "Não alterar o módulo X", "Manter compatibilidade com a versão Y", "Não adicionar dependências novas".]

#### Referências (opcional)
[Links de documentação, PRs anteriores, issues relacionadas, artigos técnicos relevantes.]

#### Log de Andamento (atualizado pelo agente)
> Registro cronológico do progresso da task. O agente adiciona uma entrada a cada sessão em que a task for trabalhada, incluindo sessões onde houve travamento ou interrupção. Nunca remova entradas anteriores.

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| —    | —      | —              | —               |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** [YYYY-MM-DD]
- **Branch:** [nome da branch utilizada]
- **Commit(s):** [hash ou mensagem]
- **Avaliação pós-implementação:** [aprovado / aprovado com ressalvas / reprovado]
- **Observações:** [notas relevantes para futuras tasks]
```

### Classificação de Complexidade

A complexidade determina o nível de cerimônia na avaliação pós-implementação (ver `.claude/rules/04-avaliacao-pos.md`):

| Nível | Quando usar | Exemplos |
|-------|-------------|----------|
| **patch** | Mudança trivial, sem risco de efeito colateral | Renomear variável, corrigir typo, ajustar espaçamento, remover import não utilizado |
| **minor** | Mudança localizada em um módulo, risco baixo | Implementar função isolada, corrigir bug em um arquivo, adicionar teste |
| **major** | Mudança estrutural, múltiplos arquivos, risco de impacto em cascata | Nova feature com múltiplos módulos, refatoração arquitetural, migração de dependência |

---

## Tasks Ativas

> Tasks em andamento ou pendentes de implementação. O agente só pode trabalhar em tasks listadas aqui.
> **Regra de ordenação:** A primeira task listada é a task ativa. O agente trabalha nela até conclusão, descarte ou bloqueio explícito pelo usuário. Para mudar a prioridade, o usuário reordena as tasks nesta seção.

### TASK-000
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** major
- **Data de criação:** 2026-05-07

#### Objetivo (!obrigatório)
Configurar o ambiente de desenvolvimento com hooks de enforcement e sincronizar histórico de tasks do CLAUDE.md para o sistema `.claude/`.

#### Contexto (!obrigatório)
O projeto possui tasks concluídas (TASK-001 a TASK-009) registradas no CLAUDE.md, mas o sistema `.claude/` está com templates vazios. Os hooks de git não estão instalados. Esta task de bootstrap configura o projeto conforme as diretrizes.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:** `.claude/tasks.md`, `.claude/registry.md`, `.claude/hooks/*`
- **Dependências necessárias:** nenhuma
- **Impacto em funcionalidades existentes:** nenhum

#### Critérios de Aceite (!obrigatório)
- [x] Git hooks instalados e funcionais (`core.hooksPath` configurado)
- [x] `registry.md` preenchido com estado atual do projeto
- [x] Histórico de tasks (TASK-001 a TASK-009) migrado para seção Tasks Concluídas
- [x] TASK-010 registrada na seção Tasks Ativas

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| 2026-05-07 | 1 | Bootstrap: hooks, registry, histórico migrado | concluída |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** 2026-05-07
- **Branch:** dev
- **Commit(s):** `6c209d7 chore: add claude code enforcement system with git hooks and project registry`
- **Avaliação pós-implementação:** aprovado
- **Observações:** Histórico legado em CLAUDE.md pode ser removido após verificação

---

### TASK-011
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-05-07

#### Objetivo (!obrigatório)
Limpar estrutura do projeto removendo arquivos vazios e eliminando duplicação de documentação.

#### Contexto (!obrigatório)
Auditoria identificou arquivos vazios sem propósito, duplicação entre CLAUDE.md e .claude/tasks.md, e mudanças pendentes no git. Limpeza necessária antes de prosseguir com TASK-010.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:**
  - `src/fuzzylab/fis/engine.py` (deletar)
  - `src/fuzzylab/anfis/clustering.py` (deletar)
  - `tests/test_timeseries.py` (deletar)
  - `CLAUDE.md` (simplificar — remover histórico de tasks)
  - `requirements.txt` (confirmar deleção)
  - `notebooks/fis_mamdani.ipynb` (verificar e commitar)
- **Dependências necessárias:** nenhuma
- **Impacto em funcionalidades existentes:** nenhum — arquivos deletados são vazios/não utilizados

#### Critérios de Aceite (!obrigatório)
- [x] Arquivos vazios deletados: `fis/engine.py`, `anfis/clustering.py`, `test_timeseries.py`
- [x] `CLAUDE.md` simplificado (sem seção "Registro de Tasks")
- [x] Deleção de `requirements.txt` commitada
- [x] Mudanças do notebook verificadas e commitadas
- [x] Todos os testes continuam passando (24 testes)
- [x] Working tree limpo após commits

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| 2026-05-07 | 1 | Deletados 3 arquivos vazios, simplificado CLAUDE.md, 4 commits atômicos | concluída |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** 2026-05-07
- **Branch:** dev
- **Commit(s):** `e4b8af7`, `5041eaa`, `2e5645c`, `d99cdb4`
- **Avaliação pós-implementação:** aprovado
- **Observações:** 24 testes passando. CLAUDE.md reduzido de 317 para 78 linhas.

---

### TASK-010
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-04-30

#### Objetivo (!obrigatório)
Gerar dataset de treinamento (≥1000 amostras) a partir do FIS Mamdani para treinar o ANFIS.

#### Contexto (!obrigatório)
O ANFIS precisa de dados rotulados para treinamento. O FIS Mamdani serve como oráculo: alimentamos combinações de inputs e coletamos os outputs correspondentes. Próximo passo da Fase 2.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:** `src/fuzzylab/fis/mamdani.py` (leitura), `data/raw/mamdani_dataset.csv` (escrita), script/notebook de geração
- **Dependências necessárias:** nenhuma (usa numpy e fuzzylab.fis já instalados)
- **Impacto em funcionalidades existentes:** nenhum

#### Critérios de Aceite (!obrigatório)
- [x] Mínimo de 1.000 amostras no dataset
- [x] Cobertura uniforme dos 5 universos de discurso (temperatura, umidade, chuva, vento, delta_t)
- [x] 4 colunas de output correspondentes aos consequentes (sp, wh, ir, bp)
- [x] Inputs e outputs normalizados em [0, 1]
- [x] Arquivo salvo em `data/raw/mamdani_dataset.csv`

#### Restrições (opcional)
Tratar exceções do FIS para combinações extremas de input — descartar amostras inválidas.

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| 2026-05-07 | 1 | Script generate_dataset.py criado, dataset gerado (1012 amostras) | concluída |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** 2026-05-07
- **Branch:** dev
- **Commit(s):** feat(data): add training dataset generator for ANFIS
- **Avaliação pós-implementação:** aprovado
- **Observações:** 12 combinações de borda descartadas (NaN outputs). Dataset final: 1012 amostras, 9 colunas normalizadas.

## Tasks Concluídas

> Tasks finalizadas. Movidas para cá após conclusão e atualização do Registro de Projeto (`registry.md`). Nunca remova entradas — o histórico é cumulativo.

### TASK-001
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** major
- **Data de criação:** 2026-03-18

#### Objetivo
Migrar projeto para estrutura de pacote com subpacotes `fis`, `anfis`, `timeseries`.

#### Resultado
- **Data de conclusão:** 2026-03-18
- **Branch:** refactor/TASK-001-package-structure
- **Commit(s):** `refactor: migrate to package structure with three fuzzy submodules`
- **Avaliação pós-implementação:** aprovado

---

### TASK-002
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-03-18

#### Objetivo
Implementar membership functions dos 4 consequentes e primeira simulação ponta a ponta.

#### Resultado
- **Data de conclusão:** 2026-03-18
- **Branch:** feat/TASK-002-consequent-membership
- **Commit(s):** `feat(fis): add consequent membership functions and first simulation`
- **Avaliação pós-implementação:** aprovado

---

### TASK-003
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-03-26

#### Objetivo
Implementar regras de pulverização (atenção e proibida).

#### Resultado
- **Data de conclusão:** 2026-03-26
- **Branch:** feat/TASK-003-spray-rules
- **Commit(s):** `feat(fis): add spray window attention and prohibited rules`
- **Avaliação pós-implementação:** aprovado

---

### TASK-004
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-03-26

#### Objetivo
Implementar regras de estresse hídrico e irrigação.

#### Resultado
- **Data de conclusão:** 2026-03-26
- **Branch:** feat/TASK-004-water-stress-irrigation
- **Commit(s):** `feat(fis): add water stress and irrigation recommendation rules`
- **Avaliação pós-implementação:** aprovado

---

### TASK-005
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-03-26

#### Objetivo
Implementar regras de produtividade estimada.

#### Resultado
- **Data de conclusão:** 2026-03-26
- **Branch:** feat/TASK-005-productivity-rules
- **Commit(s):** `feat(fis): add estimated productivity rules`
- **Avaliação pós-implementação:** aprovado

---

### TASK-006
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-03-26

#### Objetivo
Validar universos de discurso e gerar visualizações.

#### Resultado
- **Data de conclusão:** 2026-03-26
- **Branch:** feat/TASK-006-universe-validation
- **Commit(s):** `feat(fis): add membership function plots and control surface validation`
- **Avaliação pós-implementação:** aprovado

---

### TASK-007
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** major
- **Data de criação:** 2026-04-15

#### Objetivo
Migrar lógica do notebook para módulo `mamdani.py` com interface pública.

#### Resultado
- **Data de conclusão:** 2026-04-15
- **Branch:** refactor/TASK-007-mamdani-module
- **Commit(s):** `refactor(fis): extract mamdani logic to module with standard interface`
- **Avaliação pós-implementação:** aprovado

---

### TASK-008
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-04-20

#### Objetivo
Criar bateria de testes unitários e documentação README.

#### Resultado
- **Data de conclusão:** 2026-04-20
- **Branch:** test/TASK-008-tests-readme
- **Commit(s):** `test(fis): add unit tests for mamdani inference scenarios`, `docs: add README`
- **Avaliação pós-implementação:** aprovado

---

### TASK-009
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-04-25

#### Objetivo
Criar scaffold do subpacote ANFIS espelhando interface do FIS.

#### Resultado
- **Data de conclusão:** 2026-04-25
- **Branch:** feat/TASK-009-anfis-scaffold
- **Commit(s):** `feat(anfis): scaffold anfis subpackage structure`
- **Avaliação pós-implementação:** aprovado

---

## Tasks Descartadas

> Tasks que foram canceladas ou substituídas antes da implementação. Registre o motivo.

[nenhuma task descartada]

---

## Regras de Preenchimento

1. **O campo Objetivo deve caber em uma frase.** Se não cabe, a task é grande demais — quebre em subtasks.
2. **Uma task deve ser completável em uma sessão de desenvolvimento.** Se a estimativa de implementação excede uma sessão, ou se a task afeta mais de 10 arquivos, ela deve ser decomposta em subtasks independentes. Cada subtask recebe seu próprio TASK-NNN e segue o fluxo completo. O campo Contexto da subtask deve referenciar a task mãe.
3. **Critérios de Aceite são obrigatórios e verificáveis.** "Funcionar corretamente" não é critério. "Retornar status 200 para inputs válidos e 400 para inputs inválidos" é.
4. **Escopo Técnico deve listar arquivos concretos.** "Algumas telas" não serve. "src/screens/LoginScreen.tsx, src/services/authService.ts" serve.
5. **Uma task por implementação.** Se durante o desenvolvimento surgir necessidade de outra mudança fora do escopo, registre uma nova task — não expanda a atual.
6. **Tasks não são retroativas.** Código já implementado sem task registrada deve ser revisado (Modo Review) e documentado antes de prosseguir com novas tasks.
7. **O resultado é preenchido pelo agente** ao final da implementação, junto com a atualização do Registro de Projeto.
8. **Complexidade é obrigatória.** Toda task deve ser classificada como `patch`, `minor` ou `major`. Na dúvida, classifique para cima (minor em vez de patch, major em vez de minor). A classificação determina o nível de cerimônia da avaliação pós-implementação.
9. **A ordem na seção Tasks Ativas define prioridade.** A primeira task é a ativa. O agente não pula para a segunda sem que a primeira esteja concluída, descartada ou explicitamente pausada pelo usuário.
10. **O Log de Andamento é obrigatório para tasks `minor` e `major`.** O agente registra uma entrada a cada sessão em que trabalhar na task, incluindo interrupções e travamentos. Tasks `patch` podem omitir o log. O log captura o progresso intermediário; a conclusão final é registrada no Resultado da task e no Histórico de Implementações do `registry.md`.
11. **Tasks revertidas não são deletadas.** Ao reverter uma implementação, a task original recebe status `revertida` com nota explicativa, e uma nova task `fix` ou `revert` é criada referenciando a original.
