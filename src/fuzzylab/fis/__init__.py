"""Mamdani fuzzy inference (scikit-fuzzy)."""

from fuzzylab.fis.mamdani.rules import (
    build_control_system,
    build_control_system_simulation,
    combined_rules,
    irrigation_rules,
    spray_rules,
    water_stress_rules,
)

__all__ = [
    "build_control_system",
    "build_control_system_simulation",
    "combined_rules",
    "irrigation_rules",
    "spray_rules",
    "water_stress_rules",
]
