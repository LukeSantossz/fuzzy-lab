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

### TASK-012
- **Status:** pendente
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-05-10

#### Objetivo (!obrigatório)
Baixar e preparar o dataset público Kaggle "Crop Health and Environmental Stress" para treinamento do ANFIS, incluindo cálculo de Delta T.

#### Contexto (!obrigatório)
O dataset sintético gerado pelo FIS Mamdani (TASK-010) possui apenas 1012 amostras. O dataset público do Kaggle oferece 212.019 registros com dados climáticos reais (temperatura, umidade, chuva, vento) que aumentarão a capacidade de generalização do ANFIS. Delta T não está disponível diretamente e será calculado via fórmulas psicrométricas.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:**
  - `scripts/download_kaggle_dataset.py` (novo)
  - `scripts/prepare_kaggle_dataset.py` (novo)
  - `data/raw/kaggle_crop_health.csv` (download)
  - `data/processed/anfis_training_data.csv` (output processado)
- **Dependências necessárias:** `kaggle` (API), `pandas`
- **Impacto em funcionalidades existentes:** nenhum

#### Critérios de Aceite (!obrigatório)
- [ ] Dataset Kaggle baixado para `data/raw/kaggle_crop_health.csv`
- [ ] Colunas mapeadas: `Temperature` → temperatura, `Humidity` → umidade, `Rainfall` → chuva, `Wind_Speed` → vento
- [ ] Delta T calculado a partir de temperatura e umidade (fórmula de bulbo úmido)
- [ ] Labels de output gerados via FIS Mamdani (sp, wh, ir, bp)
- [ ] Inputs e outputs normalizados em [0, 1]
- [ ] Dataset final salvo em `data/processed/anfis_training_data.csv`
- [ ] Mínimo 50.000 amostras válidas após filtragem

#### Restrições (opcional)
- Usar Kaggle API para download programático
- Descartar registros com valores faltantes nas colunas de input
- Manter compatibilidade com o formato do dataset sintético existente

#### Referências (opcional)
- Dataset: https://www.kaggle.com/datasets/datasetengineer/crop-health-and-environmental-stress-dataset
- Fórmula Delta T: https://www.cropsmart.com.au/blogs/news/using-delta-t-for-assessing-spray-conditions

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| —    | —      | —              | —               |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** [YYYY-MM-DD]
- **Branch:** [nome da branch utilizada]
- **Commit(s):** [hash ou mensagem]
- **Avaliação pós-implementação:** [aprovado / aprovado com ressalvas / reprovado]
- **Observações:** [notas relevantes para futuras tasks]

---

### TASK-013
- **Status:** pendente
- **Modo:** desenvolvimento
- **Complexidade:** major
- **Data de criação:** 2026-05-10

#### Objetivo (!obrigatório)
Implementar a arquitetura ANFIS completa em PyTorch seguindo a estrutura de 5 layers de Jang (1993).

#### Contexto (!obrigatório)
O scaffold do ANFIS (TASK-009) possui apenas stubs com `NotImplementedError`. Esta task implementa a arquitetura real: Layer 1 (fuzzificação), Layer 2 (firing strengths), Layer 3 (normalização), Layer 4 (consequentes), Layer 5 (defuzzificação). O modelo será inicializado com parâmetros do FIS Mamdani para acelerar convergência.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:**
  - `src/fuzzylab/anfis/anfis.py` (implementar `AnfisNet`)
  - `src/fuzzylab/anfis/layers.py` (novo — layers individuais)
  - `src/fuzzylab/anfis/__init__.py` (atualizar exports)
- **Dependências necessárias:** `torch` (já listado em pyproject.toml)
- **Impacto em funcionalidades existentes:** substitui stubs por implementação real

#### Critérios de Aceite (!obrigatório)
- [ ] Classe `AnfisNet(nn.Module)` com 5 layers implementados
- [ ] Layer 1: Gaussian MFs parametrizadas (centro, sigma) para cada input
- [ ] Layer 2: Produto das ativações (firing strength de cada regra)
- [ ] Layer 3: Normalização dos firing strengths
- [ ] Layer 4: Consequentes TSK de primeira ordem (parâmetros lineares)
- [ ] Layer 5: Soma ponderada para defuzzificação
- [ ] Forward pass executando sem erros para batch_size arbitrário
- [ ] Premise parameters inicializáveis a partir do FIS Mamdani
- [ ] `build_system()` retornando instância de `AnfisNet`

#### Restrições (opcional)
- Manter interface compatível com FIS (`build_system`, `run_inference`)
- Usar `torch.nn.Parameter` para parâmetros treináveis
- Suportar GPU (device-agnostic)

#### Referências (opcional)
- Jang, J.-S. R. (1993). ANFIS: Adaptive-Network-Based Fuzzy Inference System
- Task 11 do Notion (fuzzy_lab_tasks.md)

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| —    | —      | —              | —               |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** [YYYY-MM-DD]
- **Branch:** [nome da branch utilizada]
- **Commit(s):** [hash ou mensagem]
- **Avaliação pós-implementação:** [aprovado / aprovado com ressalvas / reprovado]
- **Observações:** [notas relevantes para futuras tasks]

---

### TASK-014
- **Status:** pendente
- **Modo:** desenvolvimento
- **Complexidade:** major
- **Data de criação:** 2026-05-10

#### Objetivo (!obrigatório)
Implementar e executar o loop de treinamento do ANFIS usando o dataset preparado na TASK-012.

#### Contexto (!obrigatório)
Com a arquitetura ANFIS implementada (TASK-013) e o dataset preparado (TASK-012), esta task treina o modelo para aproximar o comportamento do FIS Mamdani. O treinamento ajusta premise parameters (centros e sigmas das MFs) e consequent parameters (coeficientes TSK).

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:**
  - `src/fuzzylab/anfis/training.py` (novo — loop de treinamento)
  - `notebooks/anfis_training.ipynb` (novo — experimentos e visualização)
  - `data/models/anfis_weights.pt` (output — pesos treinados)
- **Dependências necessárias:** nenhuma adicional (torch já presente)
- **Impacto em funcionalidades existentes:** nenhum

#### Critérios de Aceite (!obrigatório)
- [ ] DataLoader configurado com batch_size=64, shuffle=True
- [ ] Split treino/validação (80/20)
- [ ] Loop de treinamento com Adam optimizer (lr=1e-3)
- [ ] Loss function: MSE para os 4 outputs
- [ ] Early stopping com patience=10 baseado em validation loss
- [ ] MSE de validação abaixo de 0.05 ao final do treino
- [ ] Curva de loss (treino e validação) plotada no notebook
- [ ] Weights salvos em `data/models/anfis_weights.pt`

#### Restrições (opcional)
- Testar learning rates: {1e-2, 1e-3, 1e-4}
- Máximo 500 epochs
- Fixar seed para reprodutibilidade

#### Referências (opcional)
- Task 12 do Notion (fuzzy_lab_tasks.md)

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| —    | —      | —              | —               |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** [YYYY-MM-DD]
- **Branch:** [nome da branch utilizada]
- **Commit(s):** [hash ou mensagem]
- **Avaliação pós-implementação:** [aprovado / aprovado com ressalvas / reprovado]
- **Observações:** [notas relevantes para futuras tasks]

---

### TASK-015
- **Status:** pendente
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-05-10

#### Objetivo (!obrigatório)
Validar quantitativamente o grau de aproximação entre o ANFIS treinado e o FIS Mamdani original.

#### Contexto (!obrigatório)
Esta task verifica se o ANFIS aprendeu a função de mapeamento do Mamdani com fidelidade suficiente para uso como substituto diferenciável. A validação usa um conjunto de dados independente do treinamento e compara outputs em cenários climáticos extremos.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:**
  - `notebooks/anfis_training.ipynb` (adicionar seção de validação)
  - `src/fuzzylab/anfis/evaluation.py` (novo — métricas de comparação)
- **Dependências necessárias:** `scikit-learn` (para métricas R², MAE)
- **Impacto em funcionalidades existentes:** nenhum

#### Critérios de Aceite (!obrigatório)
- [ ] Conjunto de validação gerado independentemente (20% holdout ou novo sampling)
- [ ] MSE calculado para cada um dos 4 outputs
- [ ] R² calculado para cada um dos 4 outputs
- [ ] MAE calculado para cada um dos 4 outputs
- [ ] Tabela comparativa em Markdown documentada no notebook
- [ ] 3 cenários climáticos testados: seca extrema, condições ideais, saturação/tempestade
- [ ] Meta mínima: R² > 0.90 para pelo menos 3 dos 4 outputs

#### Restrições (opcional)
- Usar mesma normalização do treinamento
- Documentar cenários com outputs lado a lado (Mamdani vs ANFIS)

#### Referências (opcional)
- Task 13 do Notion (fuzzy_lab_tasks.md)

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| —    | —      | —              | —               |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** [YYYY-MM-DD]
- **Branch:** [nome da branch utilizada]
- **Commit(s):** [hash ou mensagem]
- **Avaliação pós-implementação:** [aprovado / aprovado com ressalvas / reprovado]
- **Observações:** [notas relevantes para futuras tasks]

---

### TASK-016
- **Status:** pendente
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-05-10

#### Objetivo (!obrigatório)
Implementar a suíte de testes unitários do subpacote ANFIS, validando interface pública e fidelidade numérica.

#### Contexto (!obrigatório)
Esta é a task de encerramento da Fase 2 (Sprint 2). Os testes garantem que a interface `build_system`/`run_inference` funciona corretamente e que o ANFIS mantém proximidade aceitável com o Mamdani nos cenários de validação.

#### Escopo Técnico (!obrigatório)
- **Arquivos/módulos envolvidos:**
  - `tests/test_anfis.py` (substituir stubs por testes reais)
- **Dependências necessárias:** nenhuma adicional
- **Impacto em funcionalidades existentes:** nenhum

#### Critérios de Aceite (!obrigatório)
- [ ] `pytest tests/test_anfis.py` passando sem falhas
- [ ] Teste de instanciação: `AnfisNet(n_inputs=5, n_mfs=7)` sem erros
- [ ] Teste de forward pass: input shape `(1, 5)` produz output shape `(1, 4)`
- [ ] Teste de interface: `build_system()` retorna modelo válido
- [ ] Teste de interface: `run_inference()` retorna dict com chaves `sp`, `wh`, `ir`, `bp`
- [ ] Teste de proximidade: outputs ANFIS vs Mamdani dentro de 15% nos 3 cenários de validação
- [ ] Teste de gradientes: `model.parameters()` retorna parâmetros com `requires_grad=True`

#### Restrições (opcional)
- Fixar seed nos testes para reprodutibilidade
- Usar weights pré-treinados de `data/models/anfis_weights.pt`

#### Referências (opcional)
- Task 14 do Notion (fuzzy_lab_tasks.md)
- Testes existentes em `tests/test_fis.py` como referência de estilo

#### Log de Andamento (atualizado pelo agente)

| Data | Sessão | Ação Realizada | Status ao Final |
|------|--------|----------------|-----------------|
| —    | —      | —              | —               |

#### Resultado (preenchido ao concluir)
- **Data de conclusão:** [YYYY-MM-DD]
- **Branch:** [nome da branch utilizada]
- **Commit(s):** [hash ou mensagem]
- **Avaliação pós-implementação:** [aprovado / aprovado com ressalvas / reprovado]
- **Observações:** [notas relevantes para futuras tasks]

---

## Tasks Concluídas

> Tasks finalizadas. Movidas para cá após conclusão e atualização do Registro de Projeto (`registry.md`). Nunca remova entradas — o histórico é cumulativo.

### TASK-000
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** major
- **Data de criação:** 2026-05-07

#### Objetivo
Configurar o ambiente de desenvolvimento com hooks de enforcement e sincronizar histórico de tasks do CLAUDE.md para o sistema `.claude/`.

#### Resultado
- **Data de conclusão:** 2026-05-07
- **Branch:** dev
- **Commit(s):** `6c209d7 chore: add claude code enforcement system with git hooks and project registry`
- **Avaliação pós-implementação:** aprovado
- **Observações:** Histórico legado em CLAUDE.md removido após verificação

---

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

### TASK-010
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-04-30

#### Objetivo
Gerar dataset de treinamento (≥1000 amostras) a partir do FIS Mamdani para treinar o ANFIS.

#### Resultado
- **Data de conclusão:** 2026-05-07
- **Branch:** dev
- **Commit(s):** `feat(data): add training dataset generator for ANFIS`
- **Avaliação pós-implementação:** aprovado
- **Observações:** 12 combinações de borda descartadas (NaN outputs). Dataset final: 1012 amostras, 9 colunas normalizadas.

---

### TASK-011
- **Status:** concluída
- **Modo:** desenvolvimento
- **Complexidade:** minor
- **Data de criação:** 2026-05-07

#### Objetivo
Limpar estrutura do projeto removendo arquivos vazios e eliminando duplicação de documentação.

#### Resultado
- **Data de conclusão:** 2026-05-07
- **Branch:** dev
- **Commit(s):** `e4b8af7`, `5041eaa`, `2e5645c`, `d99cdb4`
- **Avaliação pós-implementação:** aprovado
- **Observações:** 24 testes passando. CLAUDE.md reduzido de 317 para 78 linhas.

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
