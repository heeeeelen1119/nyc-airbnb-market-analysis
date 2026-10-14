"""Run data-quality checks against the generated cleaned listing table."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from clean import ALLOWED_BOROUGHS, ALLOWED_ROOM_TYPES, ROOT


CLEAN_PATH = ROOT / "data" / "processed" / "listings_clean.parquet"


def load_cleaned(path: Path = CLEAN_PATH) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Cleaned data missing: {path}. Run python src/clean.py first.")
    return pd.read_parquet(path)


def quality_checks(frame: pd.DataFrame) -> dict[str, bool]:
    review_years = frame["last_review"].dropna().dt.year
    required = ["listing_id", "price", "borough", "neighborhood", "room_type"]
    return {
        "listing_id is unique": frame["listing_id"].is_unique,
        "prices are positive": frame["price"].gt(0).all(),
        "room types are allowed": set(frame["room_type"].dropna()).issubset(ALLOWED_ROOM_TYPES),
        "boroughs are valid": set(frame["borough"].dropna()).issubset(ALLOWED_BOROUGHS),
        "review dates are plausible": review_years.between(2010, 2020).all(),
        "key columns have no nulls": not frame[required].isna().any().any(),
    }


if __name__ == "__main__":
    checks = quality_checks(load_cleaned())
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    if not all(checks.values()):
        raise SystemExit(1)
