"""Neuro-fuzzy (ANFIS) subpackage — PyTorch-based adaptive inference.

This subpackage provides an Adaptive Neuro-Fuzzy Inference System (ANFIS)
implementation that combines fuzzy logic with neural network learning.

Public interface
----------------
- ``build_system(config)``: build an ANFIS network.
- ``run_inference(system, inputs)``: run inference on an ANFIS network.
- ``initialize_from_mamdani(model)``: initialize ANFIS from FIS Mamdani.
- ``AnfisNet``: The ANFIS neural network class.

Training utilities
------------------
- ``train(model, train_loader, val_loader, config)``: training loop.
- ``load_dataset(path)``: load CSV dataset into tensors.
- ``create_dataloaders(X, y, ...)``: create train/val DataLoaders.
- ``TrainingConfig``: configuration dataclass for training.
- ``TrainingResult``: result dataclass from training.
- ``save_weights(model, path)``: save model weights.
- ``load_weights(model, path)``: load model weights.

Evaluation utilities
--------------------
- ``compute_metrics(y_true, y_pred)``: compute MSE, MAE, R² per output.
- ``compare_with_mamdani(model, X, y)``: compare ANFIS vs Mamdani.
- ``evaluate_scenarios(model, scenarios)``: evaluate on climate scenarios.
- ``MetricsResult``: dataclass with per-output metrics.
- ``ScenarioResult``: dataclass with scenario evaluation result.
- ``CLIMATE_SCENARIOS``: predefined climate scenarios for testing.
"""

from fuzzylab.anfis.anfis import AnfisNet
from fuzzylab.anfis.engine import build_system, initialize_from_mamdani, run_inference
from fuzzylab.anfis.evaluation import (
    CLIMATE_SCENARIOS,
    MetricsResult,
    ScenarioResult,
    compare_with_mamdani,
    compute_metrics,
    evaluate_scenario,
    evaluate_scenarios,
    scenarios_to_markdown,
)
from fuzzylab.anfis.training import (
    TrainingConfig,
    TrainingResult,
    create_dataloaders,
    load_dataset,
    load_weights,
    save_weights,
    train,
    train_with_lr_search,
)

__all__ = [
    "AnfisNet",
    "build_system",
    "initialize_from_mamdani",
    "run_inference",
    "TrainingConfig",
    "TrainingResult",
    "create_dataloaders",
    "load_dataset",
    "load_weights",
    "save_weights",
    "train",
    "train_with_lr_search",
    "MetricsResult",
    "ScenarioResult",
    "CLIMATE_SCENARIOS",
    "compute_metrics",
    "compare_with_mamdani",
    "evaluate_scenario",
    "evaluate_scenarios",
    "scenarios_to_markdown",
]
