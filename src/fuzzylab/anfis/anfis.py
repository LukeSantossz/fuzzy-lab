"""ANFIS network architecture — PyTorch-based neuro-fuzzy model.

This module implements the Adaptive Neuro-Fuzzy Inference System (ANFIS)
following Jang (1993). The architecture combines fuzzy logic with neural
network learning capabilities through 5 layers:

1. Fuzzification (Gaussian MFs)
2. Rule firing strengths (T-norm product)
3. Normalization
4. TSK consequents (first-order linear)
5. Defuzzification (weighted sum)
"""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn as nn

from fuzzylab.anfis.layers import (
    DefuzzificationLayer,
    GaussianMFLayer,
    NormalizationLayer,
    RuleFiringLayer,
    TSKConsequentLayer,
)


class AnfisNet(nn.Module):
    """Adaptive Neuro-Fuzzy Inference System (ANFIS) network.

    This class implements a neuro-fuzzy hybrid system that combines the
    learning capabilities of neural networks with the interpretability
    of fuzzy inference systems.

    Parameters
    ----------
    n_inputs : int
        Number of input variables (default: 5 for fuzzy-lab).
    n_mfs : int
        Number of membership functions per input (default: 7).
    n_outputs : int
        Number of output variables (default: 4 for sp, wh, ir, bp).

    Attributes
    ----------
    n_inputs : int
        Number of input variables.
    n_mfs : int
        Number of membership functions per input.
    n_outputs : int
        Number of output variables.
    n_rules : int
        Number of fuzzy rules (equals n_mfs in simplified architecture).
    """

    def __init__(
        self,
        n_inputs: int = 5,
        n_mfs: int = 7,
        n_outputs: int = 4,
    ) -> None:
        """Initialize the ANFIS network with 5 layers."""
        super().__init__()
        self.n_inputs = n_inputs
        self.n_mfs = n_mfs
        self.n_outputs = n_outputs
        self.n_rules = n_mfs

        self.layer1_fuzzify = GaussianMFLayer(n_inputs, n_mfs)
        self.layer2_firing = RuleFiringLayer(n_inputs, n_mfs)
        self.layer3_normalize = NormalizationLayer()
        self.layer4_consequent = TSKConsequentLayer(n_inputs, self.n_rules, n_outputs)
        self.layer5_defuzzify = DefuzzificationLayer()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the ANFIS network.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, n_inputs).
            Inputs should be normalized to [0, 1].

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, n_outputs).
            Outputs are in [0, 1] range (normalized).
        """
        memberships = self.layer1_fuzzify(x)
        firing = self.layer2_firing(memberships)
        normalized_firing = self.layer3_normalize(firing)
        rule_outputs = self.layer4_consequent(x, normalized_firing)
        outputs = self.layer5_defuzzify(rule_outputs, normalized_firing)

        return outputs

    def get_premise_parameters(self) -> dict[str, torch.Tensor]:
        """Get premise parameters (MF centers and sigmas).

        Returns
        -------
        dict
            Dictionary with 'centers' and 'sigmas' tensors.
        """
        return {
            "centers": self.layer1_fuzzify.centers.data.clone(),
            "sigmas": self.layer1_fuzzify.sigmas.data.clone(),
        }

    def set_premise_parameters(
        self,
        centers: torch.Tensor | None = None,
        sigmas: torch.Tensor | None = None,
    ) -> None:
        """Set premise parameters from external values.

        Parameters
        ----------
        centers : torch.Tensor, optional
            MF centers of shape (n_inputs, n_mfs).
        sigmas : torch.Tensor, optional
            MF widths of shape (n_inputs, n_mfs).
        """
        with torch.no_grad():
            if centers is not None:
                self.layer1_fuzzify.centers.copy_(centers)
            if sigmas is not None:
                self.layer1_fuzzify.sigmas.copy_(sigmas)

    def get_consequent_parameters(self) -> torch.Tensor:
        """Get TSK consequent coefficients.

        Returns
        -------
        torch.Tensor
            Coefficients of shape (n_rules, n_outputs, n_inputs + 1).
        """
        return self.layer4_consequent.coeffs.data.clone()

    def set_consequent_parameters(self, coeffs: torch.Tensor) -> None:
        """Set TSK consequent coefficients.

        Parameters
        ----------
        coeffs : torch.Tensor
            Coefficients of shape (n_rules, n_outputs, n_inputs + 1).
        """
        with torch.no_grad():
            self.layer4_consequent.coeffs.copy_(coeffs)

    @classmethod
    def from_config(cls, config: Mapping[str, object] | None = None) -> "AnfisNet":
        """Create AnfisNet from configuration dict.

        Parameters
        ----------
        config : mapping, optional
            Configuration with keys:
            - n_inputs (int): Number of inputs (default: 5)
            - n_mfs (int): MFs per input (default: 7)
            - n_outputs (int): Number of outputs (default: 4)
            - weights_path (str): Path to load pretrained weights

        Returns
        -------
        AnfisNet
            Configured network instance.
        """
        cfg = dict(config) if config else {}
        n_inputs = cfg.get("n_inputs", 5)
        n_mfs = cfg.get("n_mfs", 7)
        n_outputs = cfg.get("n_outputs", 4)

        model = cls(n_inputs=n_inputs, n_mfs=n_mfs, n_outputs=n_outputs)

        weights_path = cfg.get("weights_path")
        if weights_path:
            state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
            model.load_state_dict(state_dict)

        return model
