"""Clean and join NYC Airbnb source files, retaining transparent quality flags."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ingest import ROOT, read_raw


PROCESSED_DIR = ROOT / "data" / "processed"
DECISIONS_PATH = ROOT / "docs" / "decisions.md"
CLEANING_LOG_PATH = ROOT / "reports" / "cleaning_log.md"
ALLOWED_ROOM_TYPES = {"Entire home/apt", "Private room", "Shared room"}
ALLOWED_BOROUGHS = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"}


def _standardize_room_type(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    mapping = {
        "entire home/apt": "Entire home/apt",
        "entire home": "Entire home/apt",
        "private room": "Private room",
        "shared room": "Shared room",
    }
    return normalized.map(mapping).astype("string")


def clean() -> tuple[pd.DataFrame, dict[str, object]]:
    """Return the cleaned inner-joined table and real cleaning-log metrics."""
    frames = read_raw()
    prices, room_types, reviews = frames["prices"].copy(), frames["room_types"].copy(), frames["reviews"].copy()
    initial_rows = len(prices)

    prices["price"] = pd.to_numeric(
        prices["price"].astype("string").str.replace(r"[^0-9.]", "", regex=True), errors="coerce"
    )
    prices["price_parse_failed"] = prices["price"].isna()
    prices["is_nonpositive_price"] = prices["price"].le(0).fillna(True)
    nonpositive_rows = int(prices["is_nonpositive_price"].sum())
    prices = prices.loc[~prices["is_nonpositive_price"]].copy()
    extreme_threshold = float(prices["price"].quantile(0.995))
    prices["is_extreme_price"] = prices["price"].ge(extreme_threshold)

    location_parts = prices["nbhood_full"].astype("string").str.split(",", n=1, expand=True)
    prices["borough"] = location_parts[0].str.strip().str.replace(r"\s+", " ", regex=True)
    prices["neighborhood"] = location_parts[1].str.strip().str.replace(r"\s+", " ", regex=True)
    prices["borough"] = prices["borough"].replace({"Staten island": "Staten Island"})
    prices["is_valid_borough"] = prices["borough"].isin(ALLOWED_BOROUGHS)

    room_types["room_type"] = _standardize_room_type(room_types["room_type"])
    room_types["is_unknown_room_type"] = ~room_types["room_type"].isin(ALLOWED_ROOM_TYPES)
    room_types["description"] = room_types["description"].astype("string").str.strip()
    description_lower = room_types["description"].fillna("").str.lower()
    for keyword in ["private", "view", "subway", "cozy", "spacious"]:
        room_types[f"mentions_{keyword}"] = description_lower.str.contains(rf"\b{keyword}\b", regex=True)
    room_types["description_length"] = room_types["description"].str.len().astype("Float64")

    reviews["host_name"] = reviews["host_name"].astype("string").str.strip()
    reviews["last_review"] = pd.to_datetime(reviews["last_review"], format="%B %d %Y", errors="coerce")
    reviews["is_missing_last_review"] = reviews["last_review"].isna()

    cleaned = prices.merge(room_types, on="listing_id", how="inner", validate="one_to_one").merge(
        reviews, on="listing_id", how="inner", validate="one_to_one"
    )
    cleaned["last_review_year"] = cleaned["last_review"].dt.year.astype("Int64")
    cleaned["last_review_month"] = cleaned["last_review"].dt.month.astype("Int64")

    metrics: dict[str, object] = {
        "source_rows": initial_rows,
        "nonpositive_rows_removed": nonpositive_rows,
        "cleaned_rows": len(cleaned),
        "price_parse_failures": int(cleaned["price_parse_failed"].sum()),
        "extreme_threshold": extreme_threshold,
        "extreme_rows_flagged": int(cleaned["is_extreme_price"].sum()),
        "invalid_borough_rows": int((~cleaned["is_valid_borough"]).sum()),
        "unknown_room_type_rows": int(cleaned["is_unknown_room_type"].sum()),
        "missing_review_rows": int(cleaned["is_missing_last_review"].sum()),
        "missing_host_rows": int(cleaned["host_name"].isna().sum()),
        "review_min": cleaned["last_review"].min(),
        "review_max": cleaned["last_review"].max(),
    }
    return cleaned, metrics


def _log_text(metrics: dict[str, object]) -> str:
    return f"""# Cleaning log

Generated with `python src/clean.py`.

| Step | Rows / result | Decision |
| --- | ---: | --- |
| Price source rows | {metrics['source_rows']:,} | Parse currency text into a numeric nightly USD price. |
| Remove non-positive prices | {metrics['nonpositive_rows_removed']:,} removed | Non-positive values are invalid for log-price analysis; the removal is explicit. |
| Cleaned inner-join rows | {metrics['cleaned_rows']:,} | Join source tables one-to-one on `listing_id`. |
| Price parse failures | {metrics['price_parse_failures']:,} | Flagged during parsing. |
| Extreme-price flag | {metrics['extreme_rows_flagged']:,} at ≥ ${metrics['extreme_threshold']:,.2f} | Retained, not dropped; used for sensitivity awareness. |
| Invalid borough labels | {metrics['invalid_borough_rows']:,} | Flagged against the five NYC boroughs. |
| Unknown room types | {metrics['unknown_room_type_rows']:,} | Flagged against three standard categories. |
| Missing last reviews | {metrics['missing_review_rows']:,} | Retained and labelled missing, not imputed. |
| Missing host names | {metrics['missing_host_rows']:,} | Retained; names are not treated as unique host IDs. |
| Parsed review-date range | {metrics['review_min']:%Y-%m-%d} to {metrics['review_max']:%Y-%m-%d} | Parsed with the observed month-name date format. |
"""


if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CLEANING_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_frame, cleaning_metrics = clean()
    cleaned_frame.to_parquet(PROCESSED_DIR / "listings_clean.parquet", index=False)
    cleaned_frame.to_csv(PROCESSED_DIR / "listings_clean.csv", index=False)
    log = _log_text(cleaning_metrics)
    CLEANING_LOG_PATH.write_text(log, encoding="utf-8")
    decisions = DECISIONS_PATH.read_text(encoding="utf-8")
    marker = "\n## Phase 2: cleaning\n"
    if marker in decisions:
        before, after = decisions.split(marker, 1)
        next_section = after.find("\n## ")
        suffix = after[next_section:] if next_section >= 0 else "\n"
        decisions = before.rstrip() + "\n"
    else:
        suffix = "\n"
    DECISIONS_PATH.write_text(
        decisions + "\n## Phase 2: cleaning\n\n" + log.replace("# Cleaning log\n\n", "").rstrip() + suffix,
        encoding="utf-8",
    )
    print(f"Wrote {len(cleaned_frame):,} cleaned listings to {PROCESSED_DIR}")
