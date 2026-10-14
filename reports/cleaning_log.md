# Cleaning log

Generated with `python src/clean.py`.

| Step | Rows / result | Decision |
| --- | ---: | --- |
| Price source rows | 25,209 | Parse currency text into a numeric nightly USD price. |
| Remove non-positive prices | 7 removed | Non-positive values are invalid for log-price analysis; the removal is explicit. |
| Cleaned inner-join rows | 25,202 | Join source tables one-to-one on `listing_id`. |
| Price parse failures | 0 | Flagged during parsing. |
| Extreme-price flag | 127 at ≥ $813.95 | Retained, not dropped; used for sensitivity awareness. |
| Invalid borough labels | 0 | Flagged against the five NYC boroughs. |
| Unknown room types | 0 | Flagged against three standard categories. |
| Missing last reviews | 0 | Retained and labelled missing, not imputed. |
| Missing host names | 8 | Retained; names are not treated as unique host IDs. |
| Parsed review-date range | 2019-01-01 to 2019-07-09 | Parsed with the observed month-name date format. |
