# Decisions and cleaning log

This document is updated by the profiling and cleaning workflow. It records observed row counts, data-quality decisions, database fallback decisions, and any execution failures.

## Initial setup

- The raw source files are intentionally ignored by Git because they are third-party learning-platform inputs.
- The planned relational key is `listing_id`; its uniqueness and the actual join coverage will be verified before cleaning.

## Phase 1: ingestion and profiling

- All three source files contain 25,209 rows and a non-null, unique `listing_id` column.
- All 25,209 listing IDs occur in all three files. The cleaned analytical table therefore uses an inner join on `listing_id`, with no loss caused by unmatched source IDs.
- `price` is text, `room_type` has case variants, and `last_review` is text; these will be parsed and standardized in the cleaning stage.
- The raw profile identified 10 missing descriptions and 8 missing host names. Both are retained as missing values rather than imputed.

## Phase 2: cleaning

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
## Phase 4: database loading

- PostgreSQL load was unavailable: `(psycopg.OperationalError) connection is bad: connection to server at "127.0.0.1", port 5432 failed: Operation not permitted`.
- Used a local DuckDB database (`data/processed/airbnb.duckdb`) for executable SQL validation; PostgreSQL schema and loader remain provided for normal use.

## Execution notes

- The initial figure-generation run aborted twice because the sandbox could not write the default Matplotlib/font cache. The analysis pipeline writes portable SVG figures directly instead.
- The dashboard server successfully opened a listening socket when run with the permitted local-server capability, but this sandbox's client/network namespace could not connect to that socket and the browser-control connection could not initialize. The app source is present and the startup command was attempted; real dashboard screenshots could not be captured in this environment.
