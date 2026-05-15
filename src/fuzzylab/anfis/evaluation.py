"""ANFIS evaluation utilities.

This module provides metrics and comparison functions to validate
how well the ANFIS approximates the FIS Mamdani.

Public interface
----------------
- ``compute_metrics(y_true, y_pred)``: Compute MSE, MAE, R² per output.
- ``compare_systems(anfis_model, mamdani_sim, inputs)``: Compare outputs.
- ``evaluate_scenarios(anfis_model, scenarios)``: Evaluate on climate scenarios.
- ``MetricsResult``: Dataclass with per-output metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import torch

from fuzzylab.anfis.anfis import AnfisNet
from fuzzylab.anfis.engine import INPUT_NAMES, INPUT_RANGES, OUTPUT_NAMES, OUTPUT_RANGES

OUTPUT_KEYS = ["sp", "wh", "ir", "bp"]


@dataclass
class MetricsResult:
    """Per-output evaluation metrics.

    Attributes
    ----------
    mse : dict[str, float]
        Mean Squared Error per output.
    mae : dict[str, float]
        Mean Absolute Error per output.
    r2 : dict[str, float]
        R² (coefficient of determination) per output.
    """

    mse: dict[str, float]
    mae: dict[str, float]
    r2: dict[str, float]

    def to_markdown(self) -> str:
        """Format metrics as Markdown table."""
        lines = [
            "| Output | MSE | MAE | R² |",
            "|--------|-----|-----|-----|",
        ]
        for key in OUTPUT_KEYS:
            mse = self.mse.get(key, float("nan"))
            mae = self.mae.get(key, float("nan"))
            r2 = self.r2.get(key, float("nan"))
            lines.append(f"| {key} | {mse:.6f} | {mae:.6f} | {r2:.4f} |")
        return "\n".join(lines)

    def meets_target(self, r2_threshold: float = 0.90, min_outputs: int = 3) -> bool:
        """Check if R² meets target for minimum number of outputs."""
        passing = sum(1 for v in self.r2.values() if v >= r2_threshold)
        return passing >= min_outputs


def compute_metrics(
    y_true: torch.Tensor,
    y_pred: torch.Tensor,
    output_names: Sequence[str] | None = None,
) -> MetricsResult:
    """Compute evaluation metrics per output.

    Parameters
    ----------
    y_true : torch.Tensor
        Ground truth of shape (n_samples, n_outputs).
    y_pred : torch.Tensor
        Predictions of shape (n_samples, n_outputs).
    output_names : sequence of str, optional
        Names for each output column. Defaults to OUTPUT_KEYS.

    Returns
    -------
    MetricsResult
        Per-output MSE, MAE, and R².
    """
    if output_names is None:
        output_names = OUTPUT_KEYS

    y_true = y_true.detach()
    y_pred = y_pred.detach()

    n_outputs = y_true.shape[1]
    mse_dict = {}
    mae_dict = {}
    r2_dict = {}

    for i, name in enumerate(output_names[:n_outputs]):
        true_i = y_true[:, i]
        pred_i = y_pred[:, i]

        mse = torch.mean((true_i - pred_i) ** 2).item()
        mae = torch.mean(torch.abs(true_i - pred_i)).item()

        ss_res = torch.sum((true_i - pred_i) ** 2)
        ss_tot = torch.sum((true_i - torch.mean(true_i)) ** 2)

        if ss_tot > 1e-10:
            r2 = 1 - (ss_res / ss_tot).item()
        else:
            r2 = float("nan")

        mse_dict[name] = mse
        mae_dict[name] = mae
        r2_dict[name] = r2

    return MetricsResult(mse=mse_dict, mae=mae_dict, r2=r2_dict)


def normalize_inputs(inputs: Mapping[str, float]) -> list[float]:
    """Normalize raw inputs to [0, 1] range.

    Parameters
    ----------
    inputs : mapping
        Raw input values keyed by variable name.

    Returns
    -------
    list[float]
        Normalized values in INPUT_NAMES order.
    """
    normalized = []
    for name in INPUT_NAMES:
        value = inputs[name]
        lo, hi = INPUT_RANGES[name]
        norm = (value - lo) / (hi - lo)
        norm = max(0.0, min(1.0, norm))
        normalized.append(norm)
    return normalized


def denormalize_outputs(outputs_norm: Sequence[float]) -> dict[str, float]:
    """Denormalize outputs from [0, 1] to original ranges.

    Parameters
    ----------
    outputs_norm : sequence of float
        Normalized outputs in OUTPUT_NAMES order.

    Returns
    -------
    dict[str, float]
        Denormalized outputs keyed by name.
    """
    result = {}
    for i, name in enumerate(OUTPUT_NAMES):
        lo, hi = OUTPUT_RANGES[name]
        norm = max(0.0, min(1.0, outputs_norm[i]))
        result[name] = lo + norm * (hi - lo)
    return result


@dataclass
class ScenarioResult:
    """Result of evaluating a single scenario.

    Attributes
    ----------
    name : str
        Scenario name.
    inputs : dict[str, float]
        Raw input values.
    anfis_outputs : dict[str, float]
        ANFIS outputs (denormalized).
    mamdani_outputs : dict[str, float] | None
        Mamdani outputs (denormalized), if available.
    """

    name: str
    inputs: dict[str, float]
    anfis_outputs: dict[str, float]
    mamdani_outputs: dict[str, float] | None = None

    def to_markdown_row(self) -> str:
        """Format as Markdown table row."""
        anfis_str = ", ".join(f"{k}={v:.2f}" for k, v in self.anfis_outputs.items())
        if self.mamdani_outputs:
            mamdani_str = ", ".join(
                f"{k}={v:.2f}" for k, v in self.mamdani_outputs.items()
            )
            return f"| {self.name} | {anfis_str} | {mamdani_str} |"
        return f"| {self.name} | {anfis_str} | — |"


CLIMATE_SCENARIOS = {
    "seca_extrema": {
        "Temperatura": 40.0,
        "Umidade": 15.0,
        "Chuva": 0.0,
        "Vento": 10.0,
        "Delta T": 20.0,
    },
    "condicoes_ideais": {
        "Temperatura": 25.0,
        "Umidade": 60.0,
        "Chuva": 5.0,
        "Vento": 5.0,
        "Delta T": 8.0,
    },
    "tempestade": {
        "Temperatura": 20.0,
        "Umidade": 95.0,
        "Chuva": 100.0,
        "Vento": 50.0,
        "Delta T": 2.0,
    },
}


def evaluate_scenario(
    model: AnfisNet,
    inputs: Mapping[str, float],
    scenario_name: str = "unnamed",
) -> ScenarioResult:
    """Evaluate ANFIS on a single scenario.

    Parameters
    ----------
    model : AnfisNet
        ANFIS model.
    inputs : mapping
        Raw input values.
    scenario_name : str
        Name for the scenario.

    Returns
    -------
    ScenarioResult
        Scenario evaluation result.
    """
    normalized = normalize_inputs(inputs)
    x = torch.tensor([normalized], dtype=torch.float32)

    model.eval()
    with torch.no_grad():
        y = model(x)

    outputs_norm = y[0].tolist()
    anfis_outputs = denormalize_outputs(outputs_norm)

    return ScenarioResult(
        name=scenario_name,
        inputs=dict(inputs),
        anfis_outputs=anfis_outputs,
        mamdani_outputs=None,
    )


def evaluate_scenarios(
    model: AnfisNet,
    scenarios: Mapping[str, Mapping[str, float]] | None = None,
) -> list[ScenarioResult]:
    """Evaluate ANFIS on multiple climate scenarios.

    Parameters
    ----------
    model : AnfisNet
        ANFIS model.
    scenarios : mapping, optional
        Dictionary of scenario_name -> inputs. Defaults to CLIMATE_SCENARIOS.

    Returns
    -------
    list[ScenarioResult]
        Results for each scenario.
    """
    if scenarios is None:
        scenarios = CLIMATE_SCENARIOS

    results = []
    for name, inputs in scenarios.items():
        result = evaluate_scenario(model, inputs, name)
        results.append(result)

    return results


def compare_with_mamdani(
    anfis_model: AnfisNet,
    X: torch.Tensor,
    y_mamdani: torch.Tensor,
) -> MetricsResult:
    """Compare ANFIS predictions against Mamdani ground truth.

    Parameters
    ----------
    anfis_model : AnfisNet
        ANFIS model.
    X : torch.Tensor
        Normalized inputs of shape (n_samples, n_inputs).
    y_mamdani : torch.Tensor
        Normalized Mamdani outputs of shape (n_samples, n_outputs).

    Returns
    -------
    MetricsResult
        Comparison metrics.
    """
    anfis_model.eval()
    with torch.no_grad():
        y_anfis = anfis_model(X)

    return compute_metrics(y_mamdani, y_anfis)


def scenarios_to_markdown(results: Sequence[ScenarioResult]) -> str:
    """Format scenario results as Markdown table."""
    has_mamdani = any(r.mamdani_outputs is not None for r in results)

    if has_mamdani:
        lines = [
            "| Scenario | ANFIS Outputs | Mamdani Outputs |",
            "|----------|---------------|-----------------|",
        ]
    else:
        lines = [
            "| Scenario | ANFIS Outputs |",
            "|----------|---------------|",
        ]

    for r in results:
        lines.append(r.to_markdown_row())

    return "\n".join(lines)
