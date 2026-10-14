"""Create a reproducible Markdown profile of the three raw source files."""

from __future__ import annotations

from pathlib import Path

from ingest import ROOT, read_raw


REPORT_PATH = ROOT / "reports" / "profile.md"


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_None_\n"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, separator, *body]) + "\n"


def profile() -> str:
    frames = read_raw()
    parts = ["# Raw data profile\n", "Generated with `python src/profile.py`.\n"]

    for name, frame in frames.items():
        parts.extend([f"## {name}\n", f"- Shape: **{frame.shape[0]:,} rows × {frame.shape[1]} columns**\n"])
        column_rows = [
            {
                "column": column,
                "dtype": str(frame[column].dtype),
                "null_count": int(frame[column].isna().sum()),
                "null_pct": f"{frame[column].isna().mean():.2%}",
            }
            for column in frame.columns
        ]
        parts.append(markdown_table(column_rows, ["column", "dtype", "null_count", "null_pct"]))
        if "listing_id" in frame:
            parts.append(f"- Duplicate `listing_id` rows: **{int(frame['listing_id'].duplicated().sum()):,}**\n")
        categoricals = frame.select_dtypes(include=["object", "string", "category"]).columns
        for column in categoricals:
            values = frame[column].fillna("<missing>").value_counts(dropna=False).head(20)
            rows = [{"value": str(value).replace("|", "\\|"), "count": int(count)} for value, count in values.items()]
            parts.extend([f"### Top values: `{column}`\n", markdown_table(rows, ["value", "count"])])

    id_sets = {name: set(frame["listing_id"].dropna()) for name, frame in frames.items()}
    all_three = set.intersection(*id_sets.values())
    union = set.union(*id_sets.values())
    coverage_rows = [
        {"group": "prices", "listing_ids": len(id_sets["prices"])},
        {"group": "room_types", "listing_ids": len(id_sets["room_types"])},
        {"group": "reviews", "listing_ids": len(id_sets["reviews"])},
        {"group": "all three files", "listing_ids": len(all_three)},
        {"group": "in at least one file", "listing_ids": len(union)},
    ]
    parts.extend(["## Join coverage\n", markdown_table(coverage_rows, ["group", "listing_ids"])])
    parts.append(
        "The downstream cleaned table uses an inner join on `listing_id` after confirming the key is unique in each file. "
        f"This retains {len(all_three):,} IDs shared across all three sources.\n"
    )
    return "\n".join(parts)


if __name__ == "__main__":
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(profile(), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
