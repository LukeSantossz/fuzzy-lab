"""ANFIS inference engine — PyTorch-based neuro-fuzzy system.

Public interface
----------------
- ``build_system(config)``: build an ANFIS network.
- ``run_inference(system, inputs)``: run inference on an ANFIS network.
- ``initialize_from_mamdani(model)``: initialize ANFIS parameters from FIS Mamdani.

The interface mirrors fuzzylab.fis for drop-in replacement.
"""

from __future__ import annotations

from typing import Mapping

import torch

from fuzzylab.anfis.anfis import AnfisNet

INPUT_NAMES = ["Temperatura", "Umidade", "Chuva", "Vento", "Delta T"]
OUTPUT_NAMES = ["sp", "wh", "ir", "bp"]

INPUT_RANGES = {
    "Temperatura": (0.0, 60.0),
    "Umidade": (0.0, 100.0),
    "Chuva": (0.0, 500.0),
    "Vento": (0.0, 150.0),
    "Delta T": (0.0, 40.0),
}

OUTPUT_RANGES = {
    "sp": (0.0, 10.0),
    "wh": (0.0, 1.0),
    "ir": (0.0, 10.0),
    "bp": (0.0, 100.0),
}


def build_system(config: Mapping[str, object] | None = None) -> AnfisNet:
    """Build and return an ANFIS network.

    Parameters
    ----------
    config : mapping, optional
        Configuration for the ANFIS network. Supported keys:

        - ``n_inputs``: Number of input variables (default: 5)
        - ``n_mfs``: Number of membership functions per input (default: 7)
        - ``n_outputs``: Number of output variables (default: 4)
        - ``weights_path``: Path to pretrained weights file
        - ``device``: Device to use ('cpu', 'cuda', etc.)

    Returns
    -------
    AnfisNet
        Configured ANFIS network in eval mode.
    """
    cfg = dict(config) if config else {}
    device = cfg.pop("device", "cpu")

    model = AnfisNet.from_config(cfg)
    model = model.to(device)
    model.eval()

    return model


def run_inference(
    system: AnfisNet,
    inputs: Mapping[str, float],
) -> dict[str, float]:
    """Run inference on an ANFIS network.

    Parameters
    ----------
    system : AnfisNet
        ANFIS network built by :func:`build_system`.
    inputs : mapping
        Input values keyed by variable name. Expected keys:
        ``"Temperatura"``, ``"Umidade"``, ``"Chuva"``, ``"Vento"``,
        ``"Delta T"``.

    Returns
    -------
    dict[str, float]
        Output values keyed by consequent name (``sp``, ``wh``, ``ir``,
        ``bp``). Values are denormalized to original ranges.
    """
    device = next(system.parameters()).device

    input_normalized = []
    for name in INPUT_NAMES:
        value = inputs[name]
        lo, hi = INPUT_RANGES[name]
        normalized = (value - lo) / (hi - lo)
        normalized = max(0.0, min(1.0, normalized))
        input_normalized.append(normalized)

    x = torch.tensor([input_normalized], dtype=torch.float32, device=device)

    with torch.no_grad():
        y = system(x)

    y_np = y.cpu().numpy()[0]

    outputs = {}
    for i, name in enumerate(OUTPUT_NAMES):
        lo, hi = OUTPUT_RANGES[name]
        normalized = float(y_np[i])
        normalized = max(0.0, min(1.0, normalized))
        outputs[name] = lo + normalized * (hi - lo)

    return outputs


def initialize_from_mamdani(model: AnfisNet) -> AnfisNet:
    """Initialize ANFIS premise parameters to match FIS Mamdani structure.

    The FIS Mamdani uses ``automf(7)`` which creates 7 triangular MFs
    uniformly distributed across each input's universe. This function
    initializes the ANFIS Gaussian MFs to approximate that distribution:

    - Centers are placed at normalized positions [0, 1/6, 2/6, ..., 1]
    - Sigmas are set for appropriate overlap between adjacent MFs

    Parameters
    ----------
    model : AnfisNet
        ANFIS network to initialize.

    Returns
    -------
    AnfisNet
        The same model with updated premise parameters.
    """
    n_inputs = model.n_inputs
    n_mfs = model.n_mfs

    centers = torch.zeros(n_inputs, n_mfs)
    for i in range(n_inputs):
        centers[i] = torch.linspace(0.0, 1.0, n_mfs)

    sigma = 1.0 / (2.0 * (n_mfs - 1)) if n_mfs > 1 else 0.5
    sigmas = torch.full((n_inputs, n_mfs), sigma)

    model.set_premise_parameters(centers=centers, sigmas=sigmas)

    return model
