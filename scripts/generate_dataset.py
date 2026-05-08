"""Generate training dataset from Mamdani FIS.

This script samples the input space uniformly, runs inference on each sample,
and saves the normalized results to data/raw/mamdani_dataset.csv.

Usage:
    python scripts/generate_dataset.py [--samples N]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from fuzzylab.fis import build_system, run_inference

# Input ranges (from mamdani.py antecedent definitions)
INPUT_RANGES = {
    "Temperatura": (0.0, 60.0),
    "Umidade": (0.0, 100.0),
    "Chuva": (0.0, 500.0),
    "Vento": (0.0, 150.0),
    "Delta T": (0.0, 40.0),
}

# Output ranges (from mamdani.py consequent definitions)
OUTPUT_RANGES = {
    "sp": (0.0, 10.0),
    "wh": (0.0, 1.0),
    "ir": (0.0, 10.0),
    "bp": (0.0, 100.0),
}

INPUT_NAMES = list(INPUT_RANGES.keys())
OUTPUT_NAMES = ["sp", "wh", "ir", "bp"]


def generate_grid_samples(points_per_dim: int = 4) -> np.ndarray:
    """Generate a uniform grid over the input space.

    Uses interior points (avoiding exact boundaries) to reduce
    edge-case failures in fuzzy inference.
    """
    grids = []
    for name in INPUT_NAMES:
        lo, hi = INPUT_RANGES[name]
        margin = (hi - lo) * 0.02
        grids.append(np.linspace(lo + margin, hi - margin, points_per_dim))

    mesh = np.meshgrid(*grids, indexing="ij")
    samples = np.stack([g.ravel() for g in mesh], axis=1)
    return samples


def normalize_inputs(raw: np.ndarray) -> np.ndarray:
    """Normalize inputs to [0, 1] based on known ranges."""
    normalized = np.zeros_like(raw)
    for i, name in enumerate(INPUT_NAMES):
        lo, hi = INPUT_RANGES[name]
        normalized[:, i] = (raw[:, i] - lo) / (hi - lo)
    return normalized


def normalize_outputs(raw: np.ndarray) -> np.ndarray:
    """Normalize outputs to [0, 1] based on known ranges."""
    normalized = np.zeros_like(raw)
    for i, name in enumerate(OUTPUT_NAMES):
        lo, hi = OUTPUT_RANGES[name]
        normalized[:, i] = (raw[:, i] - lo) / (hi - lo)
    return normalized


def run_batch_inference(
    samples: np.ndarray,
    verbose: bool = True,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Run inference on all samples, collecting valid results.

    Returns
    -------
    valid_inputs : ndarray
        Input samples that produced valid outputs.
    valid_outputs : ndarray
        Corresponding output values.
    n_failed : int
        Number of samples that failed inference.
    """
    system = build_system()
    valid_inputs = []
    valid_outputs = []
    n_failed = 0

    total = len(samples)
    for idx, sample in enumerate(samples):
        if verbose and (idx + 1) % 200 == 0:
            print(f"  Processing {idx + 1}/{total}...", flush=True)

        inputs = {name: float(sample[i]) for i, name in enumerate(INPUT_NAMES)}

        try:
            outputs = run_inference(system, inputs)

            if any(np.isnan(v) for v in outputs.values()):
                n_failed += 1
                continue

            output_values = [outputs[name] for name in OUTPUT_NAMES]
            valid_inputs.append(sample)
            valid_outputs.append(output_values)

        except Exception:
            n_failed += 1
            continue

    return (
        np.array(valid_inputs),
        np.array(valid_outputs),
        n_failed,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Mamdani training dataset")
    parser.add_argument(
        "--samples",
        type=int,
        default=1024,
        help="Target number of samples (actual grid will be closest power)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/mamdani_dataset.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    points_per_dim = max(4, int(round(args.samples ** (1 / 5))))
    actual_samples = points_per_dim**5
    print(f"Generating {actual_samples} samples ({points_per_dim} points per dimension)")

    print("Building sample grid...")
    samples = generate_grid_samples(points_per_dim)

    print(f"Running inference on {len(samples)} samples...")
    valid_inputs, valid_outputs, n_failed = run_batch_inference(samples, verbose=True)

    print(f"Valid samples: {len(valid_inputs)}, Failed: {n_failed}")

    if len(valid_inputs) < 1000:
        print(f"WARNING: Only {len(valid_inputs)} valid samples (target: 1000)")

    print("Normalizing to [0, 1]...")
    norm_inputs = normalize_inputs(valid_inputs)
    norm_outputs = normalize_outputs(valid_outputs)

    header = ",".join(INPUT_NAMES + OUTPUT_NAMES)
    data = np.hstack([norm_inputs, norm_outputs])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    np.savetxt(output_path, data, delimiter=",", header=header, comments="", fmt="%.6f")
    print(f"Saved {len(data)} samples to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
