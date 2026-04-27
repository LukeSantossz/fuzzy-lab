"""Tests for the ANFIS subpackage."""

import pytest


def test_anfis_imports():
    """Verify that the ANFIS public interface can be imported."""
    from fuzzylab.anfis import build_system, run_inference

    assert callable(build_system)
    assert callable(run_inference)


def test_build_system_raises_not_implemented():
    """Verify that build_system raises NotImplementedError (placeholder)."""
    from fuzzylab.anfis import build_system

    with pytest.raises(NotImplementedError, match="ANFIS module is not yet implemented"):
        build_system()


def test_run_inference_raises_not_implemented():
    """Verify that run_inference raises NotImplementedError (placeholder)."""
    from fuzzylab.anfis import run_inference

    with pytest.raises(NotImplementedError, match="ANFIS module is not yet implemented"):
        run_inference(None, {})
