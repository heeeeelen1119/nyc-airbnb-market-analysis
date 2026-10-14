# Decisions and cleaning log

This document is updated by the profiling and cleaning workflow. It records observed row counts, data-quality decisions, database fallback decisions, and any execution failures.

## Initial setup

- The raw source files are intentionally ignored by Git because they are third-party learning-platform inputs.
- The planned relational key is `listing_id`; its uniqueness and the actual join coverage will be verified before cleaning.
