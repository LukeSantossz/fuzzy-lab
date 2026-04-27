"""Neuro-fuzzy (ANFIS) subpackage — PyTorch-based adaptive inference.

This subpackage provides an Adaptive Neuro-Fuzzy Inference System (ANFIS)
implementation that combines fuzzy logic with neural network learning.

Public interface
----------------
- ``build_system(config)``: build an ANFIS network.
- ``run_inference(system, inputs)``: run inference on an ANFIS network.

Note
----
This module is currently a placeholder. All public functions raise
``NotImplementedError`` until the implementation is complete.
"""

from fuzzylab.anfis.engine import build_system, run_inference

__all__ = [
    "build_system",
    "run_inference",
]
