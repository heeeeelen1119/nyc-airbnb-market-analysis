"""Idempotently load cleaned data into PostgreSQL, with an offline DuckDB fallback."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
from sqlalchemy import create_engine, text

from ingest import ROOT


CLEAN_PATH = ROOT / "data" / "processed" / "listings_clean.parquet"
SCHEMA_PATH = ROOT / "sql" / "01_schema.sql"
DUCKDB_PATH = ROOT / "data" / "processed" / "airbnb.duckdb"
DECISIONS_PATH = ROOT / "docs" / "decisions.md"
LOAD_COLUMNS = [
    "listing_id", "price", "nbhood_full", "borough", "neighborhood", "description", "room_type", "host_name",
    "last_review", "is_extreme_price", "description_length", "mentions_private", "mentions_view", "mentions_subway",
    "mentions_cozy", "mentions_spacious",
]


def _database_url() -> str:
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip()
    return os.getenv("DATABASE_URL", "postgresql+psycopg://airbnb:airbnb@localhost:5432/airbnb")


def load_postgres(frame: pd.DataFrame) -> None:
    engine = create_engine(_database_url())
    statements = [statement.strip() for statement in SCHEMA_PATH.read_text(encoding="utf-8").split(";") if statement.strip()]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
        frame[LOAD_COLUMNS].to_sql("listings", connection, if_exists="append", index=False, method="multi")


def load_duckdb(frame: pd.DataFrame) -> None:
    with duckdb.connect(str(DUCKDB_PATH)) as connection:
        connection.register("cleaned_frame", frame[LOAD_COLUMNS])
        connection.execute("CREATE OR REPLACE TABLE listings AS SELECT * FROM cleaned_frame")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_listings_borough ON listings (borough, room_type)")


def record_fallback(reason: str) -> None:
    heading = "## Phase 4: database loading\n"
    text_value = DECISIONS_PATH.read_text(encoding="utf-8")
    if heading in text_value:
        text_value = text_value.split(heading, 1)[0].rstrip() + "\n"
    DECISIONS_PATH.write_text(
        text_value + f"\n{heading}\n- PostgreSQL load was unavailable: `{reason}`\n"
        "- Used a local DuckDB database (`data/processed/airbnb.duckdb`) for executable SQL validation; PostgreSQL schema and loader remain provided for normal use.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    frame = pd.read_parquet(CLEAN_PATH)
    try:
        load_postgres(frame)
        print(f"Loaded {len(frame):,} rows into PostgreSQL.")
    except Exception as exc:  # documented fallback for environments without a running DB
        load_duckdb(frame)
        record_fallback(str(exc).splitlines()[0])
        print(f"PostgreSQL unavailable; loaded {len(frame):,} rows into DuckDB at {DUCKDB_PATH}.")
