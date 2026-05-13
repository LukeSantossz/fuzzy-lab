# CLAUDE.md — Ponto de Entrada do Framework de Desenvolvimento

> **Versão:** 1.1.0 | **Localização das regras:** `.claude/rules/` | **Estado:** `.claude/tasks.md` + `.claude/registry.md`

---

## Trava de Segurança (Regra 00 — Incondicional)

Nenhuma implementação, modificação, criação ou exclusão de código é permitida sem:

1. **Task registrada** em `.claude/tasks.md`
2. **Modo declarado** pelo usuário (Desenvolvimento, Review ou Tutor)
3. **Codebase reconhecida** (regra 02 executada)
4. **Registry verificado** (`.claude/registry.md` lido)

Exceções: Modo Tutor e Review podem iniciar sem task, mas qualquer modificação de código exige registro prévio. Detalhes completos: `.claude/rules/00-trava-seguranca.md`.

## Princípios Core (Regra 01)

- Pense antes de codar. Declare premissas, exponha trade-offs, pergunte se ambíguo.
- Simplicidade primeiro. Código mínimo, sem features especulativas, sem abstração prematura.
- Mudanças cirúrgicas. Toque apenas o necessário. Limpe apenas a própria sujeira.
- Todo código gerado por agente é rascunho até ser revisado e compreendido pelo desenvolvedor.

## Início de Sessão — O Que Ler

### Sempre (toda sessão):

1. Este arquivo (`CLAUDE.md`)
2. `.claude/registry.md` → estado atual, última implementação, pendências
3. `.claude/tasks.md` → **apenas a seção "Tasks Ativas"**, não carregar Tasks Concluídas

### Sob demanda (quando a condição ativar):

| Condição | Ler |
|----------|-----|
| Projeto novo ou primeira sessão | `.claude/prd.md` (se existir) |
| Task `minor` ou `major` | Regras 04 (avaliação) + 06 (CRURA) + 08 (registro) |
| Task `patch` | Apenas regra 05 (convenções) para commit |
| Modo Review ativado | Regra 03 completa (protocolo de review) |
| Modo Tutor ativado | Regra 03 completa (método de dicas progressivas) |
| Publicar no GitHub / curar portfólio | `.claude/guides/guia-portfolio.md` |
| Usar integração Codex | `.claude/guides/guia-codex.md` |
| Setup de hooks ou enforcement | Regra 09 |
| Dúvida sobre nomenclatura ou commits | Regra 05 |
| Task requer referência a padrões anteriores | Consultar base de conhecimento externa (ver seção abaixo) |

### Regras detalhadas (referência completa):

```
.claude/rules/
├── 00-trava-seguranca.md     ← condições obrigatórias
├── 01-principios.md          ← como pensar e codar
├── 02-reconhecimento.md      ← mapeamento pré-implementação
├── 03-modos-operacao.md      ← desenvolvimento / review / tutor
├── 04-avaliacao-pos.md       ← verificação pós-implementação + testes
├── 05-convencoes.md          ← nomenclatura, commits, branches
├── 06-crura.md               ← fluxo CRURA + checklist unificado
├── 07-integridade.md         ← regras invioláveis
├── 08-registro-projeto.md    ← registry + recuperação de sessão
└── 09-enforcement.md         ← hooks git automatizados
```

## Recuperação de Sessão

Se a sessão anterior foi interrompida (timeout, limite de contexto, crash):

1. Ler `registry.md` → última implementação e estado registrado
2. Ler `tasks.md` → task ativa e último Log de Andamento
3. Verificar branch atual (`git branch --show-current`) e último commit (`git log -1 --oneline`)
4. Comparar estado real vs registrado. Reportar divergências ao usuário.
5. Retomar do ponto documentado no Log de Andamento.

## Base de Conhecimento Externa

Caminho: C:\Users\lucas\OneDrive\Desktop\llm-wiki\wiki\
Índice: wiki/index.md

**Regras de uso:**
- APENAS CONSULTA — não modificar, criar ou atualizar arquivos nesta pasta
- Consultar antes de: decidir stack, investigar bugs recorrentes, tomar decisões arquiteturais
- O índice `index.md` é o ponto de entrada para navegação

## Informações do Projeto

- **Nome:** fuzzy-lab
- **Stack:** Python 3.10+, NumPy, scikit-fuzzy, PyTorch (ANFIS)
- **Repositório:** lucas/fuzzy-lab

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

## Task Management

Task registration and tracking is managed in `.claude/tasks.md`. See `.claude/rules/` for the complete development workflow.
