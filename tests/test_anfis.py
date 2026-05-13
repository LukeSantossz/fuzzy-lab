"""Tests for the ANFIS subpackage."""

import pytest
import torch


def test_anfis_imports():
    """Verify that the ANFIS public interface can be imported."""
    from fuzzylab.anfis import AnfisNet, build_system, run_inference

    assert callable(build_system)
    assert callable(run_inference)
    assert AnfisNet is not None


def test_anfis_instantiation():
    """Verify AnfisNet can be instantiated with default parameters."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)

    assert model.n_inputs == 5
    assert model.n_mfs == 7
    assert model.n_outputs == 4
    assert model.n_rules == 7


def test_anfis_forward_pass_shape():
    """Verify forward pass produces correct output shape."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    x = torch.rand(1, 5)
    y = model(x)

    assert y.shape == (1, 4)


def test_anfis_forward_pass_batch():
    """Verify forward pass works with arbitrary batch size."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    x = torch.rand(32, 5)
    y = model(x)

    assert y.shape == (32, 4)


def test_build_system_returns_anfis():
    """Verify build_system returns an AnfisNet instance."""
    from fuzzylab.anfis import AnfisNet, build_system

    system = build_system()

    assert isinstance(system, AnfisNet)


def test_run_inference_returns_dict():
    """Verify run_inference returns dict with expected keys."""
    from fuzzylab.anfis import build_system, run_inference

    system = build_system()
    inputs = {
        "Temperatura": 25.0,
        "Umidade": 60.0,
        "Chuva": 10.0,
        "Vento": 5.0,
        "Delta T": 8.0,
    }
    outputs = run_inference(system, inputs)

    assert isinstance(outputs, dict)
    assert set(outputs.keys()) == {"sp", "wh", "ir", "bp"}
    assert all(isinstance(v, float) for v in outputs.values())


def test_anfis_parameters_trainable():
    """Verify model parameters have requires_grad=True."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    params = list(model.parameters())

    assert len(params) > 0
    assert all(p.requires_grad for p in params)


def test_anfis_premise_parameters():
    """Verify premise parameters (centers, sigmas) can be get/set."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    premise = model.get_premise_parameters()

    assert "centers" in premise
    assert "sigmas" in premise
    assert premise["centers"].shape == (5, 7)
    assert premise["sigmas"].shape == (5, 7)

    new_centers = torch.ones(5, 7) * 0.5
    model.set_premise_parameters(centers=new_centers)

    updated = model.get_premise_parameters()
    assert torch.allclose(updated["centers"], new_centers)


def test_initialize_from_mamdani():
    """Verify initialize_from_mamdani sets correct premise parameters."""
    from fuzzylab.anfis import AnfisNet, initialize_from_mamdani

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    model = initialize_from_mamdani(model)

    premise = model.get_premise_parameters()

    expected_centers = torch.linspace(0.0, 1.0, 7)
    for i in range(5):
        assert torch.allclose(premise["centers"][i], expected_centers)

    expected_sigma = 1.0 / (2.0 * 6)
    assert torch.allclose(premise["sigmas"], torch.full((5, 7), expected_sigma))


def test_initialize_from_mamdani_forward_pass():
    """Verify model works correctly after Mamdani initialization."""
    from fuzzylab.anfis import AnfisNet, initialize_from_mamdani

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    model = initialize_from_mamdani(model)

    x = torch.rand(1, 5)
    y = model(x)

    assert y.shape == (1, 4)
    assert not torch.isnan(y).any()
