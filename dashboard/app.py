"""Interactive local dashboard for the processed NYC Airbnb listings."""

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "listings_clean.parquet"
COEFFICIENTS_PATH = ROOT / "reports" / "tables" / "regression_coefficients.csv"

st.set_page_config(page_title="NYC Airbnb Market Analysis", layout="wide")


@st.cache_data
def load_data():
    return pd.read_parquet(DATA_PATH)


frame = load_data()
st.title("NYC Airbnb Market Analysis — 2019 listings")
st.caption("Descriptive listing-level analysis. Latest-review date indicates review recency, not occupancy.")

with st.sidebar:
    st.header("Filters")
    boroughs = st.multiselect("Borough", sorted(frame.borough.unique()), default=sorted(frame.borough.unique()))
    room_types = st.multiselect("Room type", sorted(frame.room_type.unique()), default=sorted(frame.room_type.unique()))
    price_range = st.slider("Nightly price (USD)", float(frame.price.min()), float(frame.price.quantile(.99)), (float(frame.price.min()), float(frame.price.quantile(.99))))

filtered = frame.loc[frame.borough.isin(boroughs) & frame.room_type.isin(room_types) & frame.price.between(*price_range)].copy()
st.metric("Filtered listings", f"{len(filtered):,}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Price distribution", "Borough comparison", "Neighborhood ranking", "Review recency", "Regression summary"])
with tab1:
    st.subheader("Nightly price distribution")
    st.bar_chart(filtered.price.value_counts(bins=30).sort_index())
with tab2:
    st.subheader("Median nightly price by borough and room type")
    comparison = filtered.groupby(["borough", "room_type"], as_index=False).agg(listings=("listing_id", "size"), median_price=("price", "median"), mean_price=("price", "mean"))
    st.dataframe(comparison.sort_values("median_price", ascending=False), use_container_width=True, hide_index=True)
    st.bar_chart(comparison.pivot(index="borough", columns="room_type", values="median_price"))
with tab3:
    st.subheader("Neighborhood ranking")
    ranks = filtered.groupby(["borough", "neighborhood"], as_index=False).agg(listings=("listing_id", "size"), median_price=("price", "median"))
    st.dataframe(ranks.sort_values(["borough", "median_price"], ascending=[True, False]), use_container_width=True, hide_index=True)
with tab4:
    st.subheader("Latest-review recency")
    recency = pd.Series(pd.cut(filtered.last_review, bins=[pd.Timestamp("1900-01-01"), pd.Timestamp("2019-06-01"), pd.Timestamp("2020-01-01")], labels=["Stale (before Jun 2019)", "Recent (Jun-Jul 2019)"])).value_counts()
    recency.loc["Missing"] = filtered.last_review.isna().sum()
    st.bar_chart(recency)
with tab5:
    st.subheader("OLS log-price model")
    st.caption("Associations conditional on room type, borough, description length, and selected description signals; not causal effects.")
    if COEFFICIENTS_PATH.is_file():
        coefficients = pd.read_csv(COEFFICIENTS_PATH)
        st.dataframe(coefficients, use_container_width=True, hide_index=True)
    else:
        st.info("Run `python src/analysis.py` to generate regression results.")
