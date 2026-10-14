from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate import ALLOWED_BOROUGHS, ALLOWED_ROOM_TYPES, load_cleaned


def test_listing_id_is_unique():
    assert load_cleaned()["listing_id"].is_unique


def test_prices_are_positive_after_cleaning():
    assert load_cleaned()["price"].gt(0).all()


def test_room_types_are_allowed():
    assert set(load_cleaned()["room_type"].dropna()).issubset(ALLOWED_ROOM_TYPES)


def test_boroughs_are_the_five_nyc_boroughs():
    assert set(load_cleaned()["borough"].dropna()).issubset(ALLOWED_BOROUGHS)


def test_review_dates_are_plausible():
    review_years = load_cleaned()["last_review"].dropna().dt.year
    assert review_years.between(2010, 2020).all()


def test_key_columns_have_no_nulls():
    frame = load_cleaned()
    assert not frame[["listing_id", "price", "borough", "neighborhood", "room_type"]].isna().any().any()
