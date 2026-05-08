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

## Task Management

Task registration and tracking is managed in `.claude/tasks.md`. See `.claude/rules/` for the complete development workflow.
