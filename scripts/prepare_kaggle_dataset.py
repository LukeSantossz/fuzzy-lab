"""Prepare Kaggle dataset for ANFIS training.

This script processes the Kaggle Crop Health dataset:
1. Extracts relevant weather columns (Temperature, Humidity, Rainfall, Wind_Speed)
2. Calculates Delta T from temperature and humidity (Stull formula)
3. Generates output labels using the FIS Mamdani system
4. Normalizes all values to [0, 1]
5. Saves the processed dataset

Usage:
    python scripts/prepare_kaggle_dataset.py [--input PATH] [--output PATH]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from fuzzylab.fis import build_system, run_inference

INPUT_FILE = Path("data/raw/kaggle_crop_health.csv")
OUTPUT_FILE = Path("data/processed/anfis_training_data.csv")

KAGGLE_COLUMNS = {
    "Temperature": "Temperatura",
    "Humidity": "Umidade",
    "Rainfall": "Chuva",
    "Wind_Speed": "Vento",
}

INPUT_RANGES = {
    "Temperatura": (0.0, 60.0),
    "Umidade": (0.0, 100.0),
    "Chuva": (0.0, 500.0),
    "Vento": (0.0, 150.0),
    "Delta T": (0.0, 40.0),
}

OUTPUT_RANGES = {
    "sp": (0.0, 10.0),
    "wh": (0.0, 1.0),
    "ir": (0.0, 10.0),
    "bp": (0.0, 100.0),
}

INPUT_NAMES = ["Temperatura", "Umidade", "Chuva", "Vento", "Delta T"]
OUTPUT_NAMES = ["sp", "wh", "ir", "bp"]


def calculate_wet_bulb(temperature: np.ndarray, humidity: np.ndarray) -> np.ndarray:
    """Calculate wet bulb temperature using Stull (2011) formula.

    Parameters
    ----------
    temperature : ndarray
        Air temperature in Celsius.
    humidity : ndarray
        Relative humidity in percent (0-100).

    Returns
    -------
    ndarray
        Wet bulb temperature in Celsius.
    """
    T = temperature
    RH = humidity

    Tw = (
        T * np.arctan(0.151977 * np.sqrt(RH + 8.313659))
        + np.arctan(T + RH)
        - np.arctan(RH - 1.676331)
        + 0.00391838 * np.power(RH, 1.5) * np.arctan(0.023101 * RH)
        - 4.686035
    )

    return Tw


def calculate_delta_t(temperature: np.ndarray, humidity: np.ndarray) -> np.ndarray:
    """Calculate Delta T (dry bulb - wet bulb temperature).

    Delta T is used in agriculture to assess spray conditions.
    Values between 2-8°C are generally ideal for spraying.
    """
    wet_bulb = calculate_wet_bulb(temperature, humidity)
    delta_t = temperature - wet_bulb
    return np.clip(delta_t, 0.0, 40.0)


def filter_valid_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Filter rows to match FIS Mamdani input ranges."""
    mask = (
        (df["Temperatura"] >= 0) & (df["Temperatura"] <= 60)
        & (df["Umidade"] >= 0) & (df["Umidade"] <= 100)
        & (df["Chuva"] >= 0) & (df["Chuva"] <= 500)
        & (df["Vento"] >= 0) & (df["Vento"] <= 150)
        & (df["Delta T"] >= 0) & (df["Delta T"] <= 40)
    )
    return df[mask].copy()


def normalize_column(values: np.ndarray, col_name: str, ranges: dict) -> np.ndarray:
    """Normalize values to [0, 1] based on known ranges."""
    lo, hi = ranges[col_name]
    return (values - lo) / (hi - lo)


def run_batch_inference(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Generate FIS outputs for each row in the dataframe."""
    system = build_system()
    outputs = {name: [] for name in OUTPUT_NAMES}
    valid_mask = []

    total = len(df)
    data = df[INPUT_NAMES].values

    for idx in range(total):
        if verbose and (idx + 1) % 5000 == 0:
            print(f"  Processing {idx + 1}/{total}...", flush=True)

        row = data[idx]
        inputs = {
            "Temperatura": float(row[0]),
            "Umidade": float(row[1]),
            "Chuva": float(row[2]),
            "Vento": float(row[3]),
            "Delta T": float(row[4]),
        }

        try:
            result = run_inference(system, inputs)

            if any(np.isnan(v) for v in result.values()):
                valid_mask.append(False)
                for name in OUTPUT_NAMES:
                    outputs[name].append(np.nan)
            else:
                valid_mask.append(True)
                for name in OUTPUT_NAMES:
                    outputs[name].append(result[name])

        except Exception:
            valid_mask.append(False)
            for name in OUTPUT_NAMES:
                outputs[name].append(np.nan)

    for name in OUTPUT_NAMES:
        df[name] = outputs[name]

    return df[valid_mask].copy()


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Kaggle dataset for ANFIS")
    parser.add_argument(
        "--input",
        type=str,
        default=str(INPUT_FILE),
        help="Input CSV path (Kaggle dataset)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_FILE),
        help="Output CSV path (processed dataset)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=60000,
        help="Max samples to process (default: 60000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for sampling (default: 42)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        print("Run: python scripts/download_kaggle_dataset.py")
        return 1

    print(f"Loading dataset from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"  Raw records: {len(df)}")

    required_cols = list(KAGGLE_COLUMNS.keys())
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"ERROR: Missing columns: {missing}")
        return 1

    print("Extracting weather columns...")
    df = df[required_cols].copy()
    df.rename(columns=KAGGLE_COLUMNS, inplace=True)

    print("Removing rows with missing values...")
    before = len(df)
    df.dropna(inplace=True)
    print(f"  Removed {before - len(df)} rows with NaN")

    print("Calculating Delta T (Stull formula)...")
    df["Delta T"] = calculate_delta_t(
        df["Temperatura"].values,
        df["Umidade"].values,
    )

    print("Filtering to FIS input ranges...")
    before = len(df)
    df = filter_valid_ranges(df)
    print(f"  Removed {before - len(df)} out-of-range rows")
    print(f"  Valid records: {len(df)}")

    if len(df) < 50000:
        print(f"WARNING: Only {len(df)} valid samples (target: 50,000)")

    if len(df) > args.samples:
        print(f"Sampling {args.samples} records (seed={args.seed})...")
        df = df.sample(n=args.samples, random_state=args.seed)

    print("Generating FIS Mamdani labels...")
    df = df.reset_index(drop=True)
    df = run_batch_inference(df, verbose=True)
    print(f"  Valid after inference: {len(df)}")

    print("Normalizing to [0, 1]...")
    for col in INPUT_NAMES:
        df[col] = normalize_column(df[col].values, col, INPUT_RANGES)
    for col in OUTPUT_NAMES:
        df[col] = normalize_column(df[col].values, col, OUTPUT_RANGES)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, float_format="%.6f")

    print(f"\nDataset saved to: {output_path}")
    print(f"  Total samples: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
