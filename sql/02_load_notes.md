# Database load notes

Set `DATABASE_URL` in `.env`, start PostgreSQL with `docker compose up -d db` (or use a local PostgreSQL instance), and run `python src/load_db.py`. The loader will recreate the analytical table so it can be run repeatedly.

If PostgreSQL cannot be started, the pipeline uses DuckDB for local SQL execution and records that fallback in `docs/decisions.md`.
