#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head
python scripts/ingest_gcat.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
