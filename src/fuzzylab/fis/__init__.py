"""Fuzzy inference subpackage (Mamdani)."""

from fuzzylab.fis.mamdani import (
    all_rules,
    build_control_system,
    build_control_system_simulation,
    build_system,
    combined_rules,
    irrigation_rules,
    productivity_rules,
    run_inference,
    spray_rules,
    water_stress_rules,
)

__all__ = [
    # public interface
    "build_system",
    "run_inference",
    # rule builders
    "all_rules",
    "combined_rules",
    "irrigation_rules",
    "productivity_rules",
    "spray_rules",
    "water_stress_rules",
    # backward-compat
    "build_control_system",
    "build_control_system_simulation",
]
