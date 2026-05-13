"""Neuro-fuzzy (ANFIS) subpackage — PyTorch-based adaptive inference.

This subpackage provides an Adaptive Neuro-Fuzzy Inference System (ANFIS)
implementation that combines fuzzy logic with neural network learning.

Public interface
----------------
- ``build_system(config)``: build an ANFIS network.
- ``run_inference(system, inputs)``: run inference on an ANFIS network.
- ``initialize_from_mamdani(model)``: initialize ANFIS from FIS Mamdani.
- ``AnfisNet``: The ANFIS neural network class.
"""

from fuzzylab.anfis.anfis import AnfisNet
from fuzzylab.anfis.engine import build_system, initialize_from_mamdani, run_inference

__all__ = [
    "AnfisNet",
    "build_system",
    "initialize_from_mamdani",
    "run_inference",
]
