"""Download Kaggle Crop Health dataset.

This script downloads the 'Crop Health and Environmental Stress' dataset
from Kaggle and extracts it to data/raw/.

Usage:
    python scripts/download_kaggle_dataset.py

Requirements:
    - Kaggle API configured (~/.kaggle/kaggle.json)
    - kaggle package installed
"""

from __future__ import annotations

import sys
from pathlib import Path

DATASET_ID = "datasetengineer/crop-health-and-environmental-stress-dataset"
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "kaggle_crop_health.csv"


def main() -> int:
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("ERROR: kaggle package not installed.")
        print("Run: pip install kaggle")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Authenticating with Kaggle API...")
    api = KaggleApi()
    api.authenticate()

    print(f"Downloading dataset: {DATASET_ID}")
    api.dataset_download_files(DATASET_ID, path=OUTPUT_DIR, unzip=True)

    csv_files = list(OUTPUT_DIR.glob("*.csv"))
    kaggle_csvs = [f for f in csv_files if "kaggle" not in f.name.lower() and f.name != "mamdani_dataset.csv"]

    if not kaggle_csvs:
        print("ERROR: No CSV file found after download.")
        return 1

    downloaded_file = kaggle_csvs[0]

    if downloaded_file.name != OUTPUT_FILE.name:
        if OUTPUT_FILE.exists():
            OUTPUT_FILE.unlink()
        downloaded_file.rename(OUTPUT_FILE)
        print(f"Renamed {downloaded_file.name} -> {OUTPUT_FILE.name}")

    print(f"Dataset saved to: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.1f} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
