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
