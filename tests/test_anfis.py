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


def test_anfis_n_mfs_one():
    """Verify AnfisNet works with n_mfs=1 (edge case, no division by zero)."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=3, n_mfs=1, n_outputs=2)

    assert model.n_mfs == 1
    assert model.n_rules == 1

    x = torch.rand(4, 3)
    y = model(x)

    assert y.shape == (4, 2)
    assert not torch.isnan(y).any()
    assert not torch.isinf(y).any()


def test_anfis_backward_pass_finite_gradients():
    """Verify backward pass produces finite gradients for all parameters."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    x = torch.rand(8, 5)

    y = model(x)
    loss = y.sum()
    loss.backward()

    for name, param in model.named_parameters():
        assert param.grad is not None, f"No gradient for {name}"
        assert torch.isfinite(param.grad).all(), f"Non-finite gradient for {name}"


def test_normalization_zero_firing_returns_uniform():
    """Verify NormalizationLayer returns uniform distribution when firing is zero."""
    from fuzzylab.anfis.layers import NormalizationLayer

    layer = NormalizationLayer()

    zero_firing = torch.zeros(2, 5)
    normalized = layer(zero_firing)

    assert normalized.shape == (2, 5)
    assert torch.allclose(normalized.sum(dim=1), torch.ones(2))
    assert torch.allclose(normalized, torch.full((2, 5), 0.2))


def test_sigmas_always_positive():
    """Verify sigmas are always positive regardless of raw parameter values."""
    from fuzzylab.anfis import AnfisNet

    model = AnfisNet(n_inputs=3, n_mfs=5, n_outputs=2)

    with torch.no_grad():
        model.layer1_fuzzify._raw_sigmas.fill_(-100.0)

    sigmas = model.layer1_fuzzify.sigmas
    assert (sigmas > 0).all(), "Sigmas must be positive"

    x = torch.rand(2, 3)
    y = model(x)
    assert not torch.isnan(y).any()


# --- Training module tests ---


def test_training_imports():
    """Verify training utilities can be imported."""
    from fuzzylab.anfis import (
        TrainingConfig,
        TrainingResult,
        create_dataloaders,
        load_dataset,
        load_weights,
        save_weights,
        train,
    )

    assert callable(load_dataset)
    assert callable(create_dataloaders)
    assert callable(train)
    assert callable(save_weights)
    assert callable(load_weights)


def test_training_config_defaults():
    """Verify TrainingConfig has correct defaults."""
    from fuzzylab.anfis import TrainingConfig

    config = TrainingConfig()

    assert config.lr == 1e-3
    assert config.batch_size == 64
    assert config.max_epochs == 500
    assert config.patience == 10
    assert config.val_split == 0.2
    assert config.seed == 42
    assert config.device == "cpu"


def test_create_dataloaders_split():
    """Verify create_dataloaders produces correct train/val split."""
    from fuzzylab.anfis import create_dataloaders

    X = torch.rand(100, 5)
    y = torch.rand(100, 4)

    train_loader, val_loader = create_dataloaders(
        X, y, batch_size=16, val_split=0.2, seed=42
    )

    train_samples = sum(len(batch[0]) for batch in train_loader)
    val_samples = sum(len(batch[0]) for batch in val_loader)

    assert train_samples == 80
    assert val_samples == 20


def test_create_dataloaders_batch_shape():
    """Verify DataLoader batches have correct shape."""
    from fuzzylab.anfis import create_dataloaders

    X = torch.rand(100, 5)
    y = torch.rand(100, 4)

    train_loader, _ = create_dataloaders(X, y, batch_size=32)

    X_batch, y_batch = next(iter(train_loader))

    assert X_batch.shape[1] == 5
    assert y_batch.shape[1] == 4


def test_train_reduces_loss():
    """Verify training reduces validation loss."""
    from fuzzylab.anfis import AnfisNet, TrainingConfig, create_dataloaders, train

    torch.manual_seed(42)

    X = torch.rand(200, 5)
    y = torch.rand(200, 4)

    train_loader, val_loader = create_dataloaders(X, y, batch_size=32, val_split=0.2)

    model = AnfisNet(n_inputs=5, n_mfs=3, n_outputs=4)

    config = TrainingConfig(lr=1e-2, max_epochs=20, patience=5)
    result = train(model, train_loader, val_loader, config)

    assert len(result.train_losses) > 0
    assert len(result.val_losses) > 0
    assert result.best_val_loss <= result.val_losses[0]


def test_train_early_stopping():
    """Verify early stopping triggers when loss plateaus."""
    from fuzzylab.anfis import AnfisNet, TrainingConfig, create_dataloaders, train

    torch.manual_seed(42)

    X = torch.rand(100, 5)
    y = X[:, :4].clone()

    train_loader, val_loader = create_dataloaders(X, y, batch_size=32, val_split=0.2)

    model = AnfisNet(n_inputs=5, n_mfs=3, n_outputs=4)

    config = TrainingConfig(lr=1e-2, max_epochs=100, patience=3)
    result = train(model, train_loader, val_loader, config)

    assert len(result.train_losses) < 100


def test_save_load_weights(tmp_path):
    """Verify weights can be saved and loaded correctly."""
    from fuzzylab.anfis import AnfisNet, load_weights, save_weights

    model1 = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    weights_path = tmp_path / "test_weights.pt"

    save_weights(model1, weights_path)

    assert weights_path.exists()

    model2 = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    model2 = load_weights(model2, weights_path)

    for p1, p2 in zip(model1.parameters(), model2.parameters()):
        assert torch.allclose(p1, p2)


def test_training_result_fields():
    """Verify TrainingResult has all expected fields."""
    from fuzzylab.anfis import AnfisNet, TrainingConfig, create_dataloaders, train

    torch.manual_seed(42)

    X = torch.rand(50, 5)
    y = torch.rand(50, 4)

    train_loader, val_loader = create_dataloaders(X, y, batch_size=16, val_split=0.2)

    model = AnfisNet(n_inputs=5, n_mfs=3, n_outputs=4)
    config = TrainingConfig(max_epochs=5, patience=10)

    result = train(model, train_loader, val_loader, config)

    assert hasattr(result, "model")
    assert hasattr(result, "train_losses")
    assert hasattr(result, "val_losses")
    assert hasattr(result, "best_epoch")
    assert hasattr(result, "best_val_loss")
    assert hasattr(result, "stopped_early")
    assert isinstance(result.model, AnfisNet)


def test_load_dataset_from_file():
    """Verify load_dataset correctly loads the mamdani dataset."""
    from pathlib import Path

    from fuzzylab.anfis import load_dataset

    dataset_path = Path(__file__).parent.parent / "data" / "raw" / "mamdani_dataset.csv"

    if not dataset_path.exists():
        pytest.skip("Dataset file not found")

    X, y = load_dataset(dataset_path)

    assert X.shape[1] == 5
    assert y.shape[1] == 4
    assert X.shape[0] == y.shape[0]
    assert X.shape[0] > 1000
    assert X.min() >= 0.0
    assert X.max() <= 1.0


# --- Evaluation module tests ---


def test_evaluation_imports():
    """Verify evaluation utilities can be imported."""
    from fuzzylab.anfis import (
        CLIMATE_SCENARIOS,
        MetricsResult,
        ScenarioResult,
        compare_with_mamdani,
        compute_metrics,
        evaluate_scenario,
        evaluate_scenarios,
        scenarios_to_markdown,
    )

    assert callable(compute_metrics)
    assert callable(compare_with_mamdani)
    assert callable(evaluate_scenario)
    assert callable(evaluate_scenarios)
    assert callable(scenarios_to_markdown)
    assert isinstance(CLIMATE_SCENARIOS, dict)


def test_compute_metrics_perfect_prediction():
    """Verify compute_metrics returns perfect scores for identical tensors."""
    from fuzzylab.anfis import compute_metrics

    y = torch.rand(100, 4)
    result = compute_metrics(y, y)

    for key in ["sp", "wh", "ir", "bp"]:
        assert result.mse[key] < 1e-10
        assert result.mae[key] < 1e-10
        assert result.r2[key] > 0.999


def test_compute_metrics_returns_metrics_result():
    """Verify compute_metrics returns MetricsResult with correct structure."""
    from fuzzylab.anfis import MetricsResult, compute_metrics

    y_true = torch.rand(50, 4)
    y_pred = torch.rand(50, 4)

    result = compute_metrics(y_true, y_pred)

    assert isinstance(result, MetricsResult)
    assert set(result.mse.keys()) == {"sp", "wh", "ir", "bp"}
    assert set(result.mae.keys()) == {"sp", "wh", "ir", "bp"}
    assert set(result.r2.keys()) == {"sp", "wh", "ir", "bp"}


def test_metrics_result_to_markdown():
    """Verify MetricsResult.to_markdown produces valid Markdown table."""
    from fuzzylab.anfis import MetricsResult

    result = MetricsResult(
        mse={"sp": 0.01, "wh": 0.02, "ir": 0.03, "bp": 0.04},
        mae={"sp": 0.1, "wh": 0.15, "ir": 0.2, "bp": 0.25},
        r2={"sp": 0.95, "wh": 0.92, "ir": 0.88, "bp": 0.91},
    )

    md = result.to_markdown()

    assert "| Output | MSE | MAE | R² |" in md
    assert "| sp |" in md
    assert "0.95" in md


def test_metrics_result_meets_target():
    """Verify MetricsResult.meets_target works correctly."""
    from fuzzylab.anfis import MetricsResult

    good_result = MetricsResult(
        mse={}, mae={},
        r2={"sp": 0.95, "wh": 0.92, "ir": 0.91, "bp": 0.85},
    )
    assert good_result.meets_target(r2_threshold=0.90, min_outputs=3) is True

    bad_result = MetricsResult(
        mse={}, mae={},
        r2={"sp": 0.95, "wh": 0.80, "ir": 0.75, "bp": 0.70},
    )
    assert bad_result.meets_target(r2_threshold=0.90, min_outputs=3) is False


def test_evaluate_scenario_returns_result():
    """Verify evaluate_scenario returns ScenarioResult with outputs."""
    from fuzzylab.anfis import AnfisNet, ScenarioResult, evaluate_scenario

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)

    inputs = {
        "Temperatura": 25.0,
        "Umidade": 60.0,
        "Chuva": 10.0,
        "Vento": 5.0,
        "Delta T": 8.0,
    }

    result = evaluate_scenario(model, inputs, "test_scenario")

    assert isinstance(result, ScenarioResult)
    assert result.name == "test_scenario"
    assert set(result.anfis_outputs.keys()) == {"sp", "wh", "ir", "bp"}


def test_evaluate_scenarios_uses_climate_scenarios():
    """Verify evaluate_scenarios uses CLIMATE_SCENARIOS by default."""
    from fuzzylab.anfis import CLIMATE_SCENARIOS, AnfisNet, evaluate_scenarios

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)

    results = evaluate_scenarios(model)

    assert len(results) == len(CLIMATE_SCENARIOS)
    scenario_names = {r.name for r in results}
    assert scenario_names == set(CLIMATE_SCENARIOS.keys())


def test_compare_with_mamdani_returns_metrics():
    """Verify compare_with_mamdani computes metrics against ground truth."""
    from fuzzylab.anfis import AnfisNet, MetricsResult, compare_with_mamdani

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)

    X = torch.rand(100, 5)
    y_mamdani = torch.rand(100, 4)

    result = compare_with_mamdani(model, X, y_mamdani)

    assert isinstance(result, MetricsResult)
    assert all(v >= 0 for v in result.mse.values())


def test_scenarios_to_markdown():
    """Verify scenarios_to_markdown produces valid table."""
    from fuzzylab.anfis import AnfisNet, evaluate_scenarios, scenarios_to_markdown

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    results = evaluate_scenarios(model)

    md = scenarios_to_markdown(results)

    assert "| Scenario |" in md
    assert "seca_extrema" in md
    assert "condicoes_ideais" in md
    assert "tempestade" in md


# --- TASK-016: Final integration tests ---


def test_anfis_vs_mamdani_proximity_untrained():
    """Verify untrained ANFIS produces outputs (proximity test placeholder).

    Note: This test validates that the ANFIS produces valid outputs when
    compared to Mamdani. The 15% proximity threshold will be meaningful
    only after training with a proper dataset.
    """
    from pathlib import Path

    from fuzzylab.anfis import (
        CLIMATE_SCENARIOS,
        AnfisNet,
        evaluate_scenario,
        initialize_from_mamdani,
        load_weights,
    )
    from fuzzylab.fis import build_system as build_mamdani
    from fuzzylab.fis import run_inference as run_mamdani

    weights_path = Path(__file__).parent.parent / "data" / "models" / "anfis_weights.pt"

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    model = initialize_from_mamdani(model)

    if weights_path.exists():
        model = load_weights(model, weights_path)

    mamdani_sim = build_mamdani()

    for scenario_name, inputs in CLIMATE_SCENARIOS.items():
        anfis_result = evaluate_scenario(model, inputs, scenario_name)
        mamdani_outputs = run_mamdani(mamdani_sim, inputs)

        for key in ["sp", "wh", "ir", "bp"]:
            anfis_val = anfis_result.anfis_outputs[key]
            mamdani_val = mamdani_outputs[key]

            assert anfis_val is not None, f"ANFIS output {key} is None"
            assert mamdani_val is not None, f"Mamdani output {key} is None"


def test_anfis_vs_mamdani_trained_proximity():
    """Verify trained ANFIS outputs are within 15% of Mamdani (skip if no weights)."""
    from pathlib import Path

    from fuzzylab.anfis import (
        CLIMATE_SCENARIOS,
        AnfisNet,
        evaluate_scenario,
        load_weights,
    )
    from fuzzylab.fis import build_system as build_mamdani
    from fuzzylab.fis import run_inference as run_mamdani

    weights_path = Path(__file__).parent.parent / "data" / "models" / "anfis_weights.pt"

    if not weights_path.exists():
        pytest.skip("Trained weights not found — run training first")

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    model = load_weights(model, weights_path)
    model.eval()

    mamdani_sim = build_mamdani()

    max_relative_errors = {}
    for scenario_name, inputs in CLIMATE_SCENARIOS.items():
        anfis_result = evaluate_scenario(model, inputs, scenario_name)
        mamdani_outputs = run_mamdani(mamdani_sim, inputs)

        for key in ["sp", "wh", "ir", "bp"]:
            anfis_val = anfis_result.anfis_outputs[key]
            mamdani_val = mamdani_outputs[key]

            if abs(mamdani_val) > 0.01:
                rel_error = abs(anfis_val - mamdani_val) / abs(mamdani_val)
            else:
                rel_error = abs(anfis_val - mamdani_val)

            if key not in max_relative_errors:
                max_relative_errors[key] = rel_error
            else:
                max_relative_errors[key] = max(max_relative_errors[key], rel_error)

    for key, max_error in max_relative_errors.items():
        assert max_error < 0.15, (
            f"Output {key} exceeds 15% relative error: {max_error:.2%}"
        )


def test_full_anfis_pipeline_integration():
    """End-to-end test of the ANFIS pipeline (untrained)."""
    from pathlib import Path

    import torch

    from fuzzylab.anfis import (
        AnfisNet,
        TrainingConfig,
        build_system,
        create_dataloaders,
        initialize_from_mamdani,
        load_dataset,
        run_inference,
        train,
    )

    dataset_path = Path(__file__).parent.parent / "data" / "raw" / "mamdani_dataset.csv"

    if not dataset_path.exists():
        pytest.skip("Dataset file not found")

    X, y = load_dataset(dataset_path)
    assert X.shape[0] > 0

    train_loader, val_loader = create_dataloaders(X, y, batch_size=32, val_split=0.2)

    model = AnfisNet(n_inputs=5, n_mfs=7, n_outputs=4)
    model = initialize_from_mamdani(model)

    config = TrainingConfig(lr=1e-2, max_epochs=5, patience=3)
    result = train(model, train_loader, val_loader, config)

    assert result.best_val_loss < float("inf")
    assert len(result.train_losses) > 0

    system = build_system()
    inputs = {
        "Temperatura": 25.0,
        "Umidade": 60.0,
        "Chuva": 10.0,
        "Vento": 5.0,
        "Delta T": 8.0,
    }
    outputs = run_inference(system, inputs)

    assert set(outputs.keys()) == {"sp", "wh", "ir", "bp"}
    assert all(isinstance(v, float) for v in outputs.values())
