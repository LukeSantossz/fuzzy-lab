![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![scikit-fuzzy](https://img.shields.io/badge/scikit--fuzzy-Mamdani-success)
![PyTorch](https://img.shields.io/badge/PyTorch-ANFIS-EE4C2C?logo=pytorch&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20development-yellow)

# fuzzy-lab

> Agricultural decision-support using fuzzy logic (IF–THEN rules), Mamdani FIS, ANFIS, and time-series analysis for spray windows, water stress, irrigation hints, and yield estimates driven by weather variables.

## Overview

Precision agriculture couples climate variables with operational limits (wind, humidity, rainfall, delta T). Crisp models are often too rigid; **fuzzy inference systems** encode uncertainty and field-aligned linguistic rules. This repository is a modular Python package: **Mamdani FIS** with [scikit-fuzzy](https://pythonhosted.org/scikit-fuzzy/), **ANFIS** with PyTorch, and a **time-series** layer (Pandas / tslearn), plus Jupyter notebooks for experiments and pytest for tests.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Fuzzy inference | [scikit-fuzzy](https://pythonhosted.org/scikit-fuzzy/) (Mamdani), NumPy |
| Neuro-fuzzy | PyTorch (ANFIS) |
| Time series | Pandas, tslearn |
| Testing | pytest |
| Experimentation | Jupyter Notebook |
| Visualization | matplotlib |

## FIS linguistic domain

**Antecedents (inputs):**

| Variable | Universe | Sets (summary) |
|----------|----------|----------------|
| Temperature | 0–60 °C | frio_extremo → crítico (7) |
| Humidity | 0–100 % | deserto → condensação (7) |
| Rainfall | 0–500 mm | seco → extrema (7) |
| Wind | 0–150 km/h | calmo → tempestade (7) |
| Delta T | 0–40 °C | inversão_térmica → extremo (7) |

**Consequents (outputs):** spray recommendation `sp` (proibida / atencao / janela_disponivel), water stress `wh` (baixo / medio / alto), irrigation recommendation `ir` (desnecessaria / opcional / recomendada), estimated productivity `bp` (baixa / medio / alta).

**Public interface** (re-exported from `fuzzylab.fis`):

```python
from fuzzylab.fis import build_system, run_inference

system = build_system()
outputs = run_inference(
    system,
    {
        "Temperatura": 28.0,
        "Umidade": 60.0,
        "Chuva": 0.0,
        "Vento": 10.0,
        "Delta T": 8.0,
    },
)
# outputs -> {"wh": ..., "ir": ..., "sp": ..., "bp": ...}
```

`build_system(config)` optionally accepts `{"rule_groups": [...]}` to include only a subset of rule builders (`spray`, `water_stress`, `irrigation`, `productivity`, `combined`).

## Getting Started

### Prerequisites

- Python 3.10 or newer
- pip
- (Optional) CUDA for GPU-accelerated PyTorch in the ANFIS module

### Installation

```bash
# Clone the repository
git clone https://github.com/<username>/fuzzy-lab.git
cd fuzzy-lab

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Editable install (recommended — import name: fuzzylab)
pip install -e .
```

Without `pip install -e .`, add `src` to `PYTHONPATH` or rely on the notebook snippet that prepends `.../src` to `sys.path`.

### Running

```bash
# Start the Jupyter server
jupyter notebook

# Main FIS experiment notebook:
# notebooks/fis_mamdani.ipynb
# (membership-function plots and 3D control surfaces are saved under notebooks/figures/)
```

```bash
# Tests
pytest tests/
```

```python
# Programmatic usage (no notebook required)
from fuzzylab.fis import build_system, run_inference

system = build_system()
outputs = run_inference(
    system,
    {"Temperatura": 28.0, "Umidade": 60.0, "Chuva": 0.0, "Vento": 10.0, "Delta T": 8.0},
)
print(outputs)  # {"wh": ..., "ir": ..., "sp": ..., "bp": ...}
```

**Environment variables:** the codebase does not require any at this stage. For PyTorch on GPU, follow upstream guidance (`CUDA_VISIBLE_DEVICES`, etc.) for your setup.

## Project Structure

```
fuzzy-lab/
├── notebooks/
│   ├── fis_mamdani.ipynb          # Mamdani FIS experiments
│   └── figures/                   # generated MF plots and control surfaces
├── data/
│   └── raw/                       # raw inputs (e.g. .gitkeep)
├── src/
│   └── fuzzylab/
│       ├── fis/
│       │   ├── mamdani.py         # Mamdani FIS module (scikit-fuzzy) — ACTIVE
│       │   └── __init__.py        # re-exports build_system / run_inference
│       ├── anfis/                 # ANFIS (placeholder)
│       └── timeseries/            # time series (placeholder)
├── tests/
│   └── test_mamdani_water_irrigation.py
├── pyproject.toml
├── venv/                          # local virtualenv (not versioned)
├── .gitignore
├── requirements.txt
└── README.md
```

## Current Status

**Status: in development — initial sprint**

| Stage | Status |
|-------|--------|
| Linguistic antecedents and consequents | Done |
| Membership functions (automf, 7 sets) | Done |
| Full spray rules (`janela_disponivel`, `atencao`, `proibida`) | Done |
| Modular package layout (`fis`, `anfis`, `timeseries`) | Done |
| Rules for water stress and irrigation | Done |
| Rules for productivity (`bet_productivity`, 7 rules) | Done |
| Public interface `build_system` / `run_inference` (flat `mamdani.py`) | Done |
| Membership-function plots and 3D control surfaces (notebook) | Done |
| ANFIS module implementation | Pending |
| Time-series module implementation | Pending |
| Calibrating universe bounds against regional climate data | Pending |
| Calibrating productivity rules against field data | Pending |

**Next steps:**

1. Flesh out the ANFIS pipeline and associated tests.
2. Implement time-series workflows and tie-ins to `data/raw/`.
3. Revisit discourse universes using field data and agronomic references.
4. Calibrate productivity rules against experimental yield datasets.

## Known issues

- Universe bounds (`np.arange`) should be checked against regional climate records and technical literature.
- Productivity rules now cover 7 scenarios but their thresholds still need calibration against experimental yield data.
- ANFIS and time-series modules are still mostly scaffolding; implementation and test coverage need to grow.
