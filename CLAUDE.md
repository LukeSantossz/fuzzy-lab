# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fuzzy-lab is an agricultural decision-support system using fuzzy logic. It provides recommendations for spray windows, water stress assessment, irrigation hints, and yield/productivity estimates driven by weather variables (temperature, humidity, rainfall, wind, delta T).

The project is structured as three subpackages under `src/fuzzylab/`:
- **fis** — Mamdani fuzzy inference system (Phase 1, complete and active)
- **anfis** — Adaptive Neuro-Fuzzy (PyTorch-based, scaffolded but all functions raise `NotImplementedError`)
- **timeseries** — Time-series analysis (empty placeholder)

## Common Commands

```bash
# Install in editable mode (required for imports to work)
pip install -e .

# Run all tests
pytest

# Run a single test file
pytest tests/test_fis.py

# Run a specific test by name
pytest tests/test_fis.py -k "test_ideal_conditions"

# Launch notebooks
jupyter notebook notebooks/
```

No linter, formatter, or CI pipeline is configured. There is no build step beyond `pip install -e .`.

## Architecture

### Package Layout (src layout)

All source code lives under `src/fuzzylab/`. The `pyproject.toml` configures `setuptools` to discover packages in `src/`, and pytest's `pythonpath` is set to `["src"]`.

### FIS Public API (`fuzzylab.fis`)

The public interface is two functions re-exported from `fis/__init__.py`:

- `build_system(config=None)` — Returns a `skfuzzy.control.ControlSystemSimulation`. Accepts an optional config dict with a `"rule_groups"` key to select which rule groups to include (default: all).
- `run_inference(system, inputs)` — Feeds input values into the simulation and returns a `dict[str, float]` with keys: `wh` (water stress 0–1), `ir` (irrigation 0–10), `sp` (spray 0–10), `bp` (productivity 0–100).

Backward-compatible helpers `build_control_system()` and `build_control_system_simulation()` also exist but prefer the two functions above.

### Rule Group Registry

Rules are organized into named groups registered in `_RULE_REGISTRY` inside `mamdani.py`: `"spray"`, `"water_stress"`, `"irrigation"`, `"productivity"`, `"combined"`. Each maps to a builder function returning `list[ctrl.Rule]`. The `build_system` config can select a subset via `config={"rule_groups": ["spray", "water_stress"]}`.

### Linguistic Variables

All variable names and membership set labels are in Portuguese. Five antecedents (Temperatura, Umidade, Chuva, Vento, Delta T) each have 7 membership sets generated via `automf`. Four consequents use 3 membership sets each.

### ANFIS Subpackage

`fuzzylab.anfis` mirrors the FIS interface (`build_system`, `run_inference`) but all functions raise `NotImplementedError`. `AnfisNet` is a stub `nn.Module`. Implementation is pending.

## Testing

Tests are in `tests/` and use pytest with no plugins. Current test files:
- `test_fis.py` — Scenario-based tests (ideal, storm, drought conditions), return types, output ranges, ordering comparisons
- `test_mamdani_water_irrigation.py` — Boundary inputs, rule group selection, public interface, cross-scenario ordering
- `test_anfis.py` — Import verification, `NotImplementedError` stubs

## Key Conventions

- Python 3.10+ required
- Core dependencies: `numpy`, `scikit-fuzzy`; ANFIS will need `torch`
- Commit messages follow Conventional Commits (`feat`, `fix`, `docs`, `chore`, `test`)
- Generated figures from notebooks go in `notebooks/figures/`
- Raw data files go in `data/raw/`

## Registro de Tasks

> Toda implementação exige uma task registrada aqui antes de qualquer modificação na codebase.

---

### Formato de Task

```
### TASK-NNN — Título descritivo
- **Tipo:** feat | fix | refactor | test | docs | chore | build | ci | revert
- **Complexidade:** patch | minor | major
- **Modo:** Desenvolvimento | Review | Tutor
- **Status:** pendente | em andamento | concluída | revertida
- **Branch:** type/TASK-NNN-descricao-curta
- **Escopo Técnico:** [lista de arquivos/módulos que serão tocados]
- **Critérios de Aceite:**
  - [ ] Critério 1
  - [ ] Critério 2
- **Log de Andamento:**
  - [data] — Descrição do progresso
- **Resultado:** [preenchido após conclusão]
```

---

### Tasks Concluídas

### TASK-001 — Migração para estrutura de pacote
- **Tipo:** refactor
- **Complexidade:** major
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** refactor/TASK-001-package-structure
- **Escopo Técnico:**
  - Hierarquia de diretórios com subpacotes `fis`, `anfis`, `timeseries`
  - `notebooks/fis_mamdani.ipynb` — migrado de `fis_mamdaniEx/climate.ipynb`
  - `__init__.py` em todos os subpacotes
  - Arquivos de requirements separados por subpacote
- **Critérios de Aceite:**
  - [x] Estrutura de diretórios conforme arquitetura-alvo criada
  - [x] `fis_mamdaniEx/climate.ipynb` movido para `notebooks/fis_mamdani.ipynb`
  - [x] Pasta legada `fis_mamdaniEx` removida
  - [x] Todos os `__init__.py` presentes nos subpacotes
  - [x] Arquivos de requirements criados
  - [x] Commit: `refactor: migrate to package structure with three fuzzy submodules`
- **Log de Andamento:**
  - [2026-03-18] — Task concluída. Estrutura de pacote criada conforme arquitetura-alvo.
- **Resultado:** Estrutura de pacote criada com subpacotes fis, anfis e timeseries. Notebook legado migrado.

---

### TASK-002 — Membership functions dos consequentes + primeira simulação
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** feat/TASK-002-consequent-membership
- **Escopo Técnico:**
  - `src/fuzzylab/fis/mamdani.py` — membership functions dos 4 consequentes
  - `notebooks/fis_mamdani.ipynb` — primeira simulação ponta a ponta
- **Critérios de Aceite:**
  - [x] Membership functions de todos os 4 consequentes definidas com universo de discurso adequado
  - [x] Primeira simulação ponta a ponta executada sem erros via `ControlSystemSimulation`
  - [x] Commit: `feat(fis): add consequent membership functions and first simulation`
- **Log de Andamento:**
  - [2026-03-18] — Task concluída. Membership functions dos consequentes implementadas e primeira simulação validada.
- **Resultado:** 4 consequentes (sp, wh, ir, bp) com membership functions e simulação funcional.

---

### TASK-003 — Regras de pulverização: atenção e proibida
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** feat/TASK-003-spray-rules
- **Escopo Técnico:**
  - `notebooks/fis_mamdani.ipynb` — regras `sp_atencao` e `sp_proibida`
- **Critérios de Aceite:**
  - [x] Regras `sp_atencao` (r1–r5) implementadas e testadas
  - [x] Regras `sp_proibida` (r1–r5) implementadas e testadas
  - [x] Simulações de validação nos cenários extremos executadas sem erros
  - [x] Commit: `feat(fis): add spray window attention and prohibited rules`
- **Log de Andamento:**
  - [2026-03-26] — Task concluída. Regras de pulverização migradas e validadas.
- **Resultado:** 11 regras de spray implementadas cobrindo cenários de atenção e proibição.

---

### TASK-004 — Regras de estresse hídrico e irrigação
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** feat/TASK-004-water-stress-irrigation
- **Escopo Técnico:**
  - `src/fuzzylab/fis/mamdani.py` — regras `water_stress` e `irrigation`
  - `notebooks/fis_mamdani.ipynb` — validação de cenários
- **Critérios de Aceite:**
  - [x] Mínimo 3 regras `water_stress` implementadas cobrindo cenários distintos (baixo, médio, alto)
  - [x] Mínimo 2 regras `irr_recomendation` implementadas com base no estresse calculado
  - [x] 3 cenários testados (seco, normal, chuvoso) com saídas numéricas verificáveis
  - [x] Commit: `feat(fis): add water stress and irrigation recommendation rules`
- **Log de Andamento:**
  - [2026-03-26] — Task concluída. 6 regras de water_stress + 3 regras de irrigation implementadas.
- **Resultado:** Regras de estresse hídrico e irrigação funcionais com cascata water_stress → irrigation.

---

### TASK-005 — Regras de produtividade estimada
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** feat/TASK-005-productivity-rules
- **Escopo Técnico:**
  - `notebooks/fis_mamdani.ipynb` — regras `productivity`
- **Critérios de Aceite:**
  - [x] Mínimo 3 regras `pd` implementadas cobrindo cenários distintos (alta, média, baixa produtividade)
  - [x] Simulações de validação com os cenários de teste executadas sem erros
  - [x] Commit: `feat(fis): add estimated productivity rules`
- **Log de Andamento:**
  - [2026-03-26] — Task concluída. 7 regras de produtividade implementadas.
- **Resultado:** Regras de produtividade cruzando water_stress, temperatura, umidade e chuva.

---

### TASK-006 — Validação dos universos e visualizações
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** feat/TASK-006-universe-validation
- **Escopo Técnico:**
  - `notebooks/fis_mamdani.ipynb` — plots e superfícies de controle
  - `notebooks/figures/` — imagens geradas
- **Critérios de Aceite:**
  - [x] Universos de discurso revisados e ajustados com base em referências climáticas regionais
  - [x] Plots das membership functions de todos os antecedentes e consequentes gerados e salvos
  - [x] Superfícies de controle (3D) para pelo menos 2 pares de variáveis plotadas
  - [x] Commit: `feat(fis): add membership function plots and control surface validation`
- **Log de Andamento:**
  - [2026-03-26] — Task concluída. Universos revisados, plots e superfícies de controle gerados.
- **Resultado:** Visualizações salvas em `notebooks/figures/`. Universos de discurso validados.

---

### TASK-007 — Migração do notebook para módulo mamdani.py
- **Tipo:** refactor
- **Complexidade:** major
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** refactor/TASK-007-mamdani-module
- **Escopo Técnico:**
  - `src/fuzzylab/fis/mamdani.py` — interface `build_system()` e `run_inference()`
  - `src/fuzzylab/fis/__init__.py` — re-exports da API pública
  - `notebooks/fis_mamdani.ipynb` — migrado para importar do módulo
- **Critérios de Aceite:**
  - [x] Módulo `mamdani.py` com interface `build_system()` e `run_inference()` exportadas via `__init__.py`
  - [x] Notebook executando via `from fuzzylab.fis import build_system, run_inference` produzindo os mesmos resultados
  - [x] Módulo importável de forma independente do notebook sem erros
  - [x] Commit: `refactor(fis): extract mamdani logic to module with standard interface`
- **Log de Andamento:**
  - [2026-04-15] — Task concluída. Lógica extraída para módulo com API pública.
- **Resultado:** `mamdani.py` com 474 linhas, API pública (build_system/run_inference), rule registry, backward-compat helpers.

---

### TASK-008 — Testes test_fis.py + README
- **Tipo:** test
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** test/TASK-008-tests-readme
- **Escopo Técnico:**
  - `tests/test_fis.py` — bateria de testes unitários
  - `tests/test_mamdani_water_irrigation.py` — testes de boundary e integração
  - `README.md` — documentação do projeto
- **Critérios de Aceite:**
  - [x] Todos os testes passando via `pytest tests/` sem falhas
  - [x] Teste de cenário de condições ideais com `janela_disponivel` esperada
  - [x] Teste de cenário de tempestade com `proibida` esperada
  - [x] Teste de cenário de seca extrema com `water_stress` alto esperado
  - [x] Teste de validação dos tipos de retorno de `run_inference()`
  - [x] README publicado respondendo as 6 perguntas do README Model
  - [x] Commits: `test(fis): add unit tests for mamdani inference scenarios` e `docs: add README`
- **Log de Andamento:**
  - [2026-04-20] — Task concluída. 24 testes passando. README publicado.
- **Resultado:** 24 testes (9 em test_fis.py, 12 em test_mamdani_water_irrigation.py, 3 em test_anfis.py). README completo. Sprint 1 finalizada.

---

### TASK-009 — Estrutura do subpacote ANFIS
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** concluída
- **Branch:** feat/TASK-009-anfis-scaffold
- **Escopo Técnico:**
  - `src/fuzzylab/anfis/__init__.py` — exports de `build_system` e `run_inference`
  - `src/fuzzylab/anfis/anfis.py` — classe `AnfisNet` (stub)
  - `src/fuzzylab/anfis/engine.py` — funções de inferência (stub)
  - `requirements-anfis.txt` — dependências PyTorch
  - `tests/test_anfis.py` — testes de import e stubs
- **Critérios de Aceite:**
  - [x] `src/fuzzylab/anfis/__init__.py` exportando `build_system` e `run_inference`
  - [x] `anfis.py` com classe `AnfisNet` (stub)
  - [x] `engine.py` com funções de inferência (stub)
  - [x] `requirements-anfis.txt` com `torch` e `numpy`
  - [x] `tests/test_anfis.py` com testes de import e `NotImplementedError`
  - [x] Commit: `feat(anfis): scaffold anfis subpackage structure`
- **Log de Andamento:**
  - [2026-04-25] — Task concluída. Subpacote ANFIS scaffolded espelhando padrão FIS.
- **Resultado:** Scaffold completo. Todas as funções públicas levantam NotImplementedError. 3 testes de stub passando.

---

### Tasks Ativas

### TASK-010 — Dataset de treinamento a partir do FIS Mamdani
- **Tipo:** feat
- **Complexidade:** minor
- **Modo:** Desenvolvimento
- **Status:** pendente
- **Branch:** feat/TASK-010-mamdani-training-dataset
- **Escopo Técnico:**
  - `src/fuzzylab/fis/mamdani.py` (leitura — `run_inference()` como oráculo)
  - `data/raw/mamdani_dataset.csv` (escrita — dataset gerado)
  - Script ou notebook para geração do dataset
- **Critérios de Aceite:**
  - [ ] Mínimo de 1.000 amostras no dataset
  - [ ] Cobertura uniforme dos 5 universos de discurso (temperatura, umidade, chuva, vento, delta_t)
  - [ ] 4 colunas de output correspondentes aos consequentes (sp, wh, ir, bp)
  - [ ] Inputs e outputs normalizados em [0, 1]
  - [ ] Arquivo salvo em `data/raw/mamdani_dataset.csv`
  - [ ] Commit: `feat(anfis): generate training dataset from mamdani fis`
- **Log de Andamento:**
  - [2026-04-30] — Task registrada. Estratégia: grid uniforme ou amostragem Monte Carlo sobre os universos de discurso; execução do FIS via `run_inference()` para cada ponto; normalização min-max por coluna. Risco: FIS Mamdani pode falhar para combinações extremas de input — tratar exceções e descartar amostras inválidas.
- **Resultado:** [pendente]
