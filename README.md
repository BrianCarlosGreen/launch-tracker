# Orbital Launch Tracker

A full-stack dashboard for historic worldwide **orbital launch attempts**, using the canonical GCAT Orbital Launch Log dataset.

**Canonical definition:** An orbital launch attempt is a **distinct `Launch_Tag` value** in the GCAT Orbital Launch Log TSV after applying optional filters. `Launch_Tag` values that are `NULL` are excluded from counts.

Primary data source: https://planet4589.org/space/gcat/tsv/derived/launchlog.tsv

## Tech stack
- **DB:** Postgres 16 (Docker Compose)
- **Backend:** Python FastAPI + SQLAlchemy + Alembic
- **Frontend:** Next.js (App Router) + TypeScript

## Prerequisites
- Docker Desktop (macOS Apple Silicon supported)

## Quick start (Docker only, no local installs)
```bash
# From the repo root

docker compose up --build
```

Open http://localhost:3000 in your browser.

To stop everything and remove the DB volume later:
```bash
docker compose down -v
```

## Optional: local development (Python + Node)
If you prefer running the API and frontend directly on your machine, follow the steps below.

### Start database
```bash
docker compose up -d db
```

### Backend setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Run migrations
```bash
cd backend
alembic upgrade head
```

### Ingest GCAT TSV
```bash
cd backend
python scripts/ingest_gcat.py
```

The ingestion script is **idempotent** and uses a unique constraint on `(launch_tag, piece)`.

### Start API
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## API overview
- `GET /api/health` → `{ "ok": true }`
- `GET /api/stats/orbital_attempts` → count of distinct `Launch_Tag`
- `GET /api/stats/attempts_by_year` → counts by year for charting
- `GET /api/launches` → deduped list of launches (one row per `Launch_Tag`)
- `GET /api/meta/schema` → ingestion metadata and counts
- `GET /api/meta/filters` → distinct filter options

### Orbital attempts definition
Counts are exact and reproducible because the tool always uses:

```
SELECT COUNT(DISTINCT launch_tag)
```

from the ingested GCAT dataset after applying filters.

## Environment variables
### Backend (`backend/.env`)
```
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/launch_tracker
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
