import csv
import sys
from datetime import timezone
from io import StringIO
from typing import Iterable

import requests
from dateutil import parser
from sqlalchemy.dialects.postgresql import insert

from app.db import SessionLocal
from app.models import Launch

GCAT_URL = "https://planet4589.org/space/gcat/tsv/derived/launchlog.tsv"
REQUIRED_COLUMNS = {
    "Launch_Tag",
    "Launch_Date",
    "Launch_Code",
    "Piece",
    "LV_Type",
    "Launch_Site",
    "Launch_Agency",
    "LV_State",
    "Name",
    "PLName",
    "Sat_Owner",
    "Sat_State",
}


def parse_launch_datetime(value: str):
    if not value:
        return None, None
    try:
        dt = parser.parse(value)
    except (ValueError, TypeError):
        return None, value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt, value


def download_tsv(url: str) -> str:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.text


def validate_columns(fieldnames: Iterable[str]):
    missing = REQUIRED_COLUMNS.difference(fieldnames)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_list}")


def ingest_rows(rows: Iterable[dict]):
    session = SessionLocal()
    try:
        for row in rows:
            launch_datetime, launch_date_raw = parse_launch_datetime(row.get("Launch_Date"))

            record = {
                "source": "gcat",
                "launch_tag": row.get("Launch_Tag") or None,
                "piece": row.get("Piece") or None,
                "launch_datetime_utc": launch_datetime,
                "launch_date_raw": launch_date_raw or None,
                "lv_type": row.get("LV_Type") or None,
                "launch_site": row.get("Launch_Site") or None,
                "launch_agency": row.get("Launch_Agency") or None,
                "lv_state": row.get("LV_State") or None,
                "launch_code": row.get("Launch_Code") or None,
                "name": row.get("Name") or None,
                "plname": row.get("PLName") or None,
                "sat_owner": row.get("Sat_Owner") or None,
                "sat_state": row.get("Sat_State") or None,
                "is_orbital": True,
                "is_launch_attempt": True,
                "raw": row,
            }

            stmt = (
                insert(Launch)
                .values(**record)
                .on_conflict_do_nothing(index_elements=["launch_tag", "piece"])
            )
            session.execute(stmt)
        session.commit()
    finally:
        session.close()


def main():
    print(f"Downloading {GCAT_URL}...")
    tsv_text = download_tsv(GCAT_URL)
    reader = csv.DictReader(StringIO(tsv_text), delimiter="\t")
    validate_columns(reader.fieldnames or [])
    ingest_rows(reader)
    print("Ingestion complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        sys.exit(1)
