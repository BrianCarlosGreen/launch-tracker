# Orbital Launch Tracker

A full-stack dashboard for historic worldwide **orbital launch attempts**, using the canonical GCAT Orbital Launch Log dataset.

**Canonical definition:** An orbital launch attempt is a **distinct `Launch_Tag` value** in the GCAT Orbital Launch Log TSV after applying optional filters. `Launch_Tag` values that are `NULL` are excluded from counts.

Primary data source: https://planet4589.org/space/gcat/tsv/derived/launchlog.tsv

## Tech stack
- **DB:** Postgres 16 (Docker Compose)
- **Backend:** Python FastAPI + SQLAlchemy + Alembic
- **Frontend:** Next.js (App Router) + TypeScript

## Prerequisites (exactly what to install)
1. **Docker Desktop** for macOS (Apple Silicon supported)
   - Download: https://www.docker.com/products/docker-desktop/
   - After installing, **open Docker Desktop** and wait until it says “Docker Desktop is running”.

Nothing else is required. You do **not** need Python or Node installed when using the Docker-only setup.

## One-click setup (macOS Finder)
If you want a one-click experience:
1. **Download the project**:
   - If you received a ZIP, double‑click it to unzip.
   - If you have a Git link, someone can clone it for you, or you can use the Terminal option below.
2. In Finder, open the project folder (the one that contains `docker-compose.yml`).
3. Open the `scripts/` folder.
4. Double‑click **`run.command`**.
   - macOS may warn you the first time. If it does, right‑click → **Open** → **Open**.
5. Wait until the logs say the services are running.
6. Open http://localhost:3000 in your browser.

To stop everything and delete all data later, double‑click **`cleanup.command`** in the same folder.

## Quick start (Terminal, one command)
If you prefer Terminal, first make sure you have the project folder on your machine (downloaded ZIP or cloned repo), then run this **single command** from the repo root (the folder that contains `docker-compose.yml`):

```bash
docker compose up --build
```

Open http://localhost:3000 in your browser.

### How to stop everything (and delete all data)
When you’re done, return to the same Terminal window and press `Ctrl + C`, then run:
```bash
docker compose down -v
```
This stops all containers and deletes the Postgres volume (all data).

## Optional: local development (Python + Node)
If you prefer running the API and frontend directly on your machine (not required for Docker-only):

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
