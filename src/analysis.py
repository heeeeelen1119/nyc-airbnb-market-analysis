"""Generate descriptive analysis, interpretable OLS outputs, and labeled figures."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from ingest import ROOT


DATA_PATH = ROOT / "data" / "processed" / "listings_clean.parquet"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"
MIN_GROUP_LISTINGS = 30
RECENT_CUTOFF = pd.Timestamp("2019-06-01")


def _save_table(frame: pd.DataFrame, name: str) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    frame.to_csv(TABLES / f"{name}.csv", index=False)


def _write_svg(path: Path, title: str, body: list[str], subtitle: str = "") -> None:
    document = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="680" viewBox="0 0 1100 680">',
        '<rect width="1100" height="680" fill="#ffffff"/>',
        f'<text x="55" y="48" font-family="Arial, sans-serif" font-size="25" font-weight="700" fill="#172554">{escape(title)}</text>',
        f'<text x="55" y="76" font-family="Arial, sans-serif" font-size="14" fill="#475569">{escape(subtitle)}</text>',
        *body,
        '</svg>',
    ]
    path.write_text("\n".join(document), encoding="utf-8")


def _bar_chart(path: Path, title: str, labels: list[str], values: list[float], x_label: str, subtitle: str = "") -> None:
    max_value = max(values) if values else 1
    body = ['<line x1="300" y1="110" x2="300" y2="620" stroke="#94a3b8"/>']
    bar_height = min(28, 480 / max(len(labels), 1))
    for index, (label, value) in enumerate(zip(labels, values)):
        y = 115 + index * (bar_height + 5)
        width = 680 * value / max_value
        body.extend([
            f'<text x="288" y="{y + bar_height * .72:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#334155">{escape(label)}</text>',
            f'<rect x="300" y="{y:.1f}" width="{width:.1f}" height="{bar_height:.1f}" rx="3" fill="#2563eb"/>',
            f'<text x="{310 + width:.1f}" y="{y + bar_height * .72:.1f}" font-family="Arial" font-size="12" fill="#0f172a">{value:,.1f}</text>',
        ])
    body.append(f'<text x="640" y="655" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">{escape(x_label)}</text>')
    _write_svg(path, title, body, subtitle)


def _line_chart(path: Path, title: str, labels: list[str], values: list[float], y_label: str) -> None:
    max_value = max(values) if values else 1
    min_value = min(values) if values else 0
    spread = max(max_value - min_value, 1)
    x_values = [100 + 880 * index / max(len(values) - 1, 1) for index in range(len(values))]
    y_values = [590 - 420 * (value - min_value) / spread for value in values]
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(x_values, y_values))
    body = ['<line x1="80" y1="590" x2="1000" y2="590" stroke="#94a3b8"/>', '<line x1="80" y1="120" x2="80" y2="590" stroke="#94a3b8"/>', f'<polyline points="{points}" fill="none" stroke="#0f766e" stroke-width="4"/>']
    for x, y, label, value in zip(x_values, y_values, labels, values):
        body.extend([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#0f766e"/>', f'<text x="{x:.1f}" y="620" text-anchor="middle" font-family="Arial" font-size="12" fill="#334155">{escape(label)}</text>', f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#0f172a">{value:,.0f}</text>'])
    body.append(f'<text x="35" y="350" transform="rotate(-90 35 350)" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">{escape(y_label)}</text>')
    _write_svg(path, title, body)


def _scatter_chart(path: Path, title: str, x_values: np.ndarray, y_values: np.ndarray) -> None:
    x_min, x_max = float(x_values.min()), float(x_values.max())
    y_min, y_max = float(y_values.min()), float(y_values.max())
    x_spread, y_spread = max(x_max - x_min, .01), max(y_max - y_min, .01)
    body = ['<line x1="80" y1="590" x2="1000" y2="590" stroke="#94a3b8"/>', '<line x1="80" y1="120" x2="80" y2="590" stroke="#94a3b8"/>']
    zero_y = 590 - 450 * (0 - y_min) / y_spread
    body.append(f'<line x1="80" y1="{zero_y:.1f}" x2="1000" y2="{zero_y:.1f}" stroke="#64748b" stroke-dasharray="5 5"/>')
    for x_value, y_value in zip(x_values, y_values):
        x = 80 + 920 * (x_value - x_min) / x_spread
        y = 590 - 450 * (y_value - y_min) / y_spread
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#7c3aed" fill-opacity=".28"/>')
    body.extend(['<text x="540" y="645" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">Fitted log(price)</text>', '<text x="35" y="350" transform="rotate(-90 35 350)" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">Residual</text>'])
    _write_svg(path, title, body, "Random sample of residuals; dashed line is zero.")


def run_analysis(frame: pd.DataFrame) -> dict[str, object]:
    """Write analysis tables, figures, model artifacts, and headline metrics."""
    FIGURES.mkdir(parents=True, exist_ok=True)

    market = (
        frame.groupby(["borough", "room_type"], observed=True)["price"]
        .agg(listing_count="size", mean_price="mean", median_price="median", p25_price=lambda x: x.quantile(.25), p75_price=lambda x: x.quantile(.75))
        .reset_index()
    )
    _save_table(market, "market_overview")

    groups = (
        frame.groupby(["borough", "neighborhood", "room_type"], observed=True)["price"]
        .agg(listing_count="size", median_price="median")
        .reset_index()
        .query("listing_count >= @MIN_GROUP_LISTINGS")
        .sort_values("median_price", ascending=False)
    )
    _save_table(groups, "price_premium_groups")

    neighborhood = (
        frame.groupby(["borough", "neighborhood"], observed=True)["price"]
        .agg(listing_count="size", median_price="median")
        .reset_index()
    )
    neighborhood["median_price_rank"] = neighborhood.groupby("borough")["median_price"].rank(ascending=False, method="min")
    neighborhood["listing_count_rank"] = neighborhood.groupby("borough")["listing_count"].rank(ascending=False, method="first")
    _save_table(neighborhood.sort_values(["borough", "median_price_rank"]), "neighborhood_ranking")

    recency_label = np.select(
        [frame["last_review"].isna(), frame["last_review"].ge(RECENT_CUTOFF)],
        ["Missing", "Recent (Jun-Jul 2019)"],
        default="Stale (before Jun 2019)",
    )
    review_recency = pd.Series(recency_label, name="review_recency").value_counts().rename_axis("review_recency").reset_index(name="listing_count")
    review_recency["listing_share_pct"] = 100 * review_recency["listing_count"] / len(frame)
    _save_table(review_recency, "review_recency")

    host_counts = frame.dropna(subset=["host_name"]).groupby("host_name").size().sort_values(ascending=False)
    top_ten_listings = int(host_counts.head(10).sum())
    host_summary = pd.DataFrame(
        [{"host_name_group": "Top 10 host names", "listings": top_ten_listings, "listing_share_pct": 100 * top_ten_listings / host_counts.sum()}]
    )
    _save_table(host_summary, "host_concentration")

    signal_rows = []
    for signal in ["mentions_private", "mentions_view", "mentions_subway", "mentions_cozy", "mentions_spacious"]:
        for present, subset in frame.groupby(signal, observed=True):
            signal_rows.append({"signal": signal.replace("mentions_", ""), "present": bool(present), "listing_count": len(subset), "mean_price": subset.price.mean(), "median_price": subset.price.median()})
    _save_table(pd.DataFrame(signal_rows), "text_signal_prices")

    model_frame = frame.dropna(subset=["description_length"]).copy()
    model_frame["log_price"] = np.log(model_frame["price"])
    for signal in ["mentions_private", "mentions_view", "mentions_subway", "mentions_cozy", "mentions_spacious"]:
        model_frame[signal] = model_frame[signal].astype(int)
    formula = "log_price ~ C(room_type) + C(borough) + mentions_private + mentions_view + mentions_subway + mentions_cozy + mentions_spacious + description_length"
    model = smf.ols(formula, data=model_frame).fit()
    conf = model.conf_int()
    regression = pd.DataFrame({
        "term": model.params.index,
        "coefficient_log_points": model.params.values,
        "approx_pct_effect": (np.exp(model.params.values) - 1) * 100,
        "ci_low_log_points": conf.iloc[:, 0].values,
        "ci_high_log_points": conf.iloc[:, 1].values,
        "p_value": model.pvalues.values,
    })
    _save_table(regression, "regression_coefficients")
    (REPORTS / "regression_summary.txt").write_text(model.summary().as_text(), encoding="utf-8")

    plot_data = market.sort_values("median_price", ascending=False)
    _bar_chart(FIGURES / "median_price_by_borough_room_type.svg", "Median nightly price by borough and room type", (plot_data.borough + " — " + plot_data.room_type).tolist(), plot_data.median_price.tolist(), "Median price (USD per night)")
    borough_medians = frame.groupby("borough").price.median().sort_values(ascending=False)
    _bar_chart(FIGURES / "median_price_by_borough.svg", "Median nightly price by borough", borough_medians.index.tolist(), borough_medians.tolist(), "Median price (USD per night)", "Median is used because prices are right-skewed.")
    monthly = frame.dropna(subset=["last_review"]).groupby(frame.dropna(subset=["last_review"])["last_review"].dt.to_period("M")).size()
    _line_chart(FIGURES / "last_review_by_month.svg", "Listings by month of latest review", monthly.index.astype(str).tolist(), monthly.astype(float).tolist(), "Listings")
    residual_sample = pd.DataFrame({"fitted": model.fittedvalues, "residual": model.resid}).sample(min(800, len(model.resid)), random_state=42)
    _scatter_chart(FIGURES / "regression_residuals.svg", "OLS residuals versus fitted log price", residual_sample.fitted.to_numpy(), residual_sample.residual.to_numpy())

    top_group = groups.iloc[0]
    bottom_group = groups.iloc[-1]
    metrics: dict[str, object] = {
        "listings": int(len(frame)), "mean_price": round(float(frame.price.mean()), 2), "median_price": round(float(frame.price.median()), 2),
        "top_price_group": f"{top_group.borough}, {top_group.neighborhood} — {top_group.room_type}", "top_group_median_price": round(float(top_group.median_price), 2),
        "bottom_price_group": f"{bottom_group.borough}, {bottom_group.neighborhood} — {bottom_group.room_type}", "bottom_group_median_price": round(float(bottom_group.median_price), 2),
        "minimum_group_listing_count": MIN_GROUP_LISTINGS, "recent_review_share_pct": round(float(review_recency.loc[review_recency.review_recency.eq('Recent (Jun-Jul 2019)'), 'listing_share_pct'].iloc[0]), 2),
        "top_ten_host_name_share_pct": round(float(host_summary.listing_share_pct.iloc[0]), 2), "model_r_squared": round(float(model.rsquared), 3), "model_n": int(model.nobs),
        "residual_mean": round(float(model.resid.mean()), 6), "residual_std": round(float(model.resid.std()), 3),
    }
    (REPORTS / "analysis_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    metrics = run_analysis(pd.read_parquet(DATA_PATH))
    print(json.dumps(metrics, indent=2))
