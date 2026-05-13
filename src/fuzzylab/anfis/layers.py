"""ANFIS layer implementations following Jang (1993) architecture.

This module implements the 5 layers of the ANFIS architecture:
- Layer 1: Fuzzification (Gaussian membership functions)
- Layer 2: Rule firing strengths (product of memberships)
- Layer 3: Normalized firing strengths
- Layer 4: TSK consequents (first-order linear)
- Layer 5: Defuzzification (weighted sum)

Note: This implementation uses a diagonal rule architecture where n_rules = n_mfs,
not the full cartesian grid (n_mfs^n_inputs). This is a design choice for
computational efficiency and works well when MFs are aligned across inputs.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

_SIGMA_EPS = 1e-4


class GaussianMFLayer(nn.Module):
    """Layer 1: Gaussian membership functions for fuzzification.

    Each input variable has n_mfs Gaussian membership functions,
    parameterized by center (c) and width (sigma).

    Sigmas are stored as raw (unconstrained) parameters and transformed
    via softplus to ensure positivity during forward pass.

    Parameters
    ----------
    n_inputs : int
        Number of input variables.
    n_mfs : int
        Number of membership functions per input.
    """

    def __init__(self, n_inputs: int, n_mfs: int) -> None:
        super().__init__()
        self.n_inputs = n_inputs
        self.n_mfs = n_mfs

        self.centers = nn.Parameter(torch.zeros(n_inputs, n_mfs))
        self._raw_sigmas = nn.Parameter(torch.zeros(n_inputs, n_mfs))

        self._init_parameters()

    @property
    def sigmas(self) -> torch.Tensor:
        """Return positive sigmas via softplus transformation."""
        return F.softplus(self._raw_sigmas) + _SIGMA_EPS

    def _init_parameters(self) -> None:
        """Initialize centers uniformly across [0, 1] and sigmas to overlap."""
        with torch.no_grad():
            for i in range(self.n_inputs):
                self.centers[i] = torch.linspace(0, 1, self.n_mfs)
            if self.n_mfs > 1:
                target_sigma = 1.0 / (2.0 * (self.n_mfs - 1))
            else:
                target_sigma = 0.5
            raw_init = torch.log(torch.exp(torch.tensor(target_sigma - _SIGMA_EPS)) - 1)
            self._raw_sigmas.fill_(raw_init.item())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute membership degrees for all inputs.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, n_inputs).

        Returns
        -------
        torch.Tensor
            Membership degrees of shape (batch_size, n_inputs, n_mfs).
        """
        x = x.unsqueeze(2)
        sigmas = self.sigmas
        memberships = torch.exp(-((x - self.centers) ** 2) / (2 * sigmas**2))
        return memberships


class RuleFiringLayer(nn.Module):
    """Layer 2: Compute rule firing strengths.

    Uses T-norm (product) to combine membership degrees.
    With n_inputs and n_mfs, creates n_mfs rules where rule i
    uses membership function i from each input.
    """

    def __init__(self, n_inputs: int, n_mfs: int) -> None:
        super().__init__()
        self.n_inputs = n_inputs
        self.n_mfs = n_mfs
        self.n_rules = n_mfs

    def forward(self, memberships: torch.Tensor) -> torch.Tensor:
        """Compute firing strength for each rule.

        Parameters
        ----------
        memberships : torch.Tensor
            Membership degrees of shape (batch_size, n_inputs, n_mfs).

        Returns
        -------
        torch.Tensor
            Firing strengths of shape (batch_size, n_rules).
        """
        firing = torch.prod(memberships, dim=1)
        return firing


class NormalizationLayer(nn.Module):
    """Layer 3: Normalize firing strengths.

    When all firing strengths are zero (underflow), returns uniform
    distribution to maintain valid probability semantics.
    """

    def forward(self, firing: torch.Tensor) -> torch.Tensor:
        """Normalize firing strengths to sum to 1.

        Parameters
        ----------
        firing : torch.Tensor
            Raw firing strengths of shape (batch_size, n_rules).

        Returns
        -------
        torch.Tensor
            Normalized firing strengths of shape (batch_size, n_rules).
            Guaranteed to sum to 1 along dim=1.
        """
        total = firing.sum(dim=1, keepdim=True)
        n_rules = firing.shape[1]
        uniform = torch.full_like(firing, 1.0 / n_rules)
        is_zero = total < 1e-8
        normalized = torch.where(is_zero, uniform, firing / (total + 1e-8))
        return normalized


class TSKConsequentLayer(nn.Module):
    """Layer 4: First-order TSK consequents (unweighted).

    Each rule computes a linear consequent: f_i = p_i0 + p_i1*x1 + ... + p_in*xn
    for each output variable. The weighting by normalized firing strengths
    is performed in Layer 5 (DefuzzificationLayer).

    Parameters
    ----------
    n_inputs : int
        Number of input variables.
    n_rules : int
        Number of rules.
    n_outputs : int
        Number of output variables.
    """

    def __init__(self, n_inputs: int, n_rules: int, n_outputs: int) -> None:
        super().__init__()
        self.n_inputs = n_inputs
        self.n_rules = n_rules
        self.n_outputs = n_outputs

        self.coeffs = nn.Parameter(torch.zeros(n_rules, n_outputs, n_inputs + 1))
        self._init_parameters()

    def _init_parameters(self) -> None:
        """Initialize coefficients near 0.5 with small noise."""
        with torch.no_grad():
            nn.init.normal_(self.coeffs, mean=0.5, std=0.1)

    def forward(
        self, x: torch.Tensor, normalized_firing: torch.Tensor
    ) -> torch.Tensor:
        """Compute TSK consequent outputs for each rule.

        Note: normalized_firing is accepted for interface consistency but
        not used here. Weighting occurs in DefuzzificationLayer.

        Parameters
        ----------
        x : torch.Tensor
            Original inputs of shape (batch_size, n_inputs).
        normalized_firing : torch.Tensor
            Normalized firing strengths (unused, for interface consistency).

        Returns
        -------
        torch.Tensor
            Rule outputs of shape (batch_size, n_rules, n_outputs).
        """
        batch_size = x.shape[0]
        ones = torch.ones(batch_size, 1, device=x.device, dtype=x.dtype)
        x_extended = torch.cat([ones, x], dim=1)

        rule_outputs = torch.einsum("bi,roi->bro", x_extended, self.coeffs)
        return rule_outputs


class DefuzzificationLayer(nn.Module):
    """Layer 5: Defuzzification via weighted sum."""

    def forward(
        self, rule_outputs: torch.Tensor, normalized_firing: torch.Tensor
    ) -> torch.Tensor:
        """Compute final outputs as weighted sum of rule outputs.

        Parameters
        ----------
        rule_outputs : torch.Tensor
            Rule outputs of shape (batch_size, n_rules, n_outputs).
        normalized_firing : torch.Tensor
            Normalized firing strengths of shape (batch_size, n_rules).

        Returns
        -------
        torch.Tensor
            Final outputs of shape (batch_size, n_outputs).
        """
        weighted = rule_outputs * normalized_firing.unsqueeze(2)
        return weighted.sum(dim=1)
