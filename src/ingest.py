"""Read the three NYC Airbnb source files with explicit file-format handling."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
EXPECTED_FILES = {
    "prices": "airbnb_price.csv",
    "room_types": "airbnb_room_type.xlsx",
    "reviews": "airbnb_last_review.tsv",
}


def source_paths(raw_dir: Path = RAW_DIR) -> dict[str, Path]:
    """Return validated raw-input paths, raising a useful error when missing."""
    paths = {name: raw_dir / filename for name, filename in EXPECTED_FILES.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing raw source file(s): " + ", ".join(missing))
    return paths


def read_raw(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Load CSV, XLSX, and TSV inputs without coercing columns prematurely."""
    paths = source_paths(raw_dir)
    return {
        "prices": pd.read_csv(paths["prices"]),
        "room_types": pd.read_excel(paths["room_types"], engine="openpyxl"),
        "reviews": pd.read_csv(paths["reviews"], sep="\t"),
    }
