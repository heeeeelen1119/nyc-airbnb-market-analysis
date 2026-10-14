from pathlib import Path
import sys

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _data():
    return pd.read_parquet(ROOT / "data" / "processed" / "listings_clean.parquet")


def test_sql_and_pandas_match_for_overall_count_and_mean():
    frame = _data()
    with duckdb.connect() as connection:
        connection.register("listings", frame)
        sql_count, sql_mean = connection.execute("SELECT COUNT(*), AVG(price) FROM listings").fetchone()
    assert sql_count == len(frame)
    assert round(sql_mean, 8) == round(frame.price.mean(), 8)


def test_sql_and_pandas_match_for_room_type_medians():
    frame = _data()
    expected = frame.groupby("room_type")["price"].median().sort_index()
    with duckdb.connect() as connection:
        connection.register("listings", frame)
        result = connection.execute("SELECT room_type, quantile_cont(price, 0.5) AS median_price FROM listings GROUP BY room_type ORDER BY room_type").fetchdf().set_index("room_type")["median_price"]
    pd.testing.assert_series_equal(result, expected, check_names=False, check_index_type=False, check_dtype=False)


def test_sql_and_pandas_match_for_borough_listing_counts():
    frame = _data()
    expected = frame.groupby("borough").size().sort_index()
    with duckdb.connect() as connection:
        connection.register("listings", frame)
        result = connection.execute("SELECT borough, COUNT(*) AS listings FROM listings GROUP BY borough ORDER BY borough").fetchdf().set_index("borough")["listings"]
    pd.testing.assert_series_equal(result, expected, check_names=False, check_index_type=False)
