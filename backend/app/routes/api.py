from datetime import datetime, timezone
from typing import Optional

from dateutil import parser
from fastapi import APIRouter, Depends, Query
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Launch
from app.schemas import (
    AttemptsByYearEntry,
    FiltersResponse,
    HealthResponse,
    LaunchResponse,
    OrbitalAttemptsResponse,
    SchemaMetaResponse,
)

router = APIRouter()

INGESTION_VERSION = "v1"


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = parser.isoparse(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(ok=True)


@router.get("/stats/orbital_attempts", response_model=OrbitalAttemptsResponse)
def orbital_attempts(
    since: Optional[str] = None,
    until: Optional[str] = None,
    agency: Optional[str] = None,
    state: Optional[str] = None,
    lv_type: Optional[str] = None,
    site: Optional[str] = None,
    db: Session = Depends(get_db),
) -> OrbitalAttemptsResponse:
    since_dt = parse_iso_datetime(since)
    until_dt = parse_iso_datetime(until)

    stmt = select(func.count(func.distinct(Launch.launch_tag))).where(Launch.launch_tag.is_not(None))

    if since_dt:
        stmt = stmt.where(Launch.launch_datetime_utc >= since_dt)
    if until_dt:
        stmt = stmt.where(Launch.launch_datetime_utc < until_dt)
    if agency:
        stmt = stmt.where(Launch.launch_agency == agency)
    if state:
        stmt = stmt.where(Launch.lv_state == state)
    if lv_type:
        stmt = stmt.where(Launch.lv_type == lv_type)
    if site:
        stmt = stmt.where(Launch.launch_site == site)

    count = db.execute(stmt).scalar_one()
    return OrbitalAttemptsResponse(count=count or 0)


@router.get("/stats/attempts_by_year", response_model=list[AttemptsByYearEntry])
def attempts_by_year(
    since: Optional[str] = None,
    until: Optional[str] = None,
    agency: Optional[str] = None,
    state: Optional[str] = None,
    lv_type: Optional[str] = None,
    site: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[AttemptsByYearEntry]:
    since_dt = parse_iso_datetime(since)
    until_dt = parse_iso_datetime(until)

    year_expr = cast(func.extract("year", Launch.launch_datetime_utc), Integer)
    stmt = (
        select(year_expr.label("year"), func.count(func.distinct(Launch.launch_tag)).label("count"))
        .where(Launch.launch_tag.is_not(None))
        .where(Launch.launch_datetime_utc.is_not(None))
        .group_by("year")
        .order_by("year")
    )

    if since_dt:
        stmt = stmt.where(Launch.launch_datetime_utc >= since_dt)
    if until_dt:
        stmt = stmt.where(Launch.launch_datetime_utc < until_dt)
    if agency:
        stmt = stmt.where(Launch.launch_agency == agency)
    if state:
        stmt = stmt.where(Launch.lv_state == state)
    if lv_type:
        stmt = stmt.where(Launch.lv_type == lv_type)
    if site:
        stmt = stmt.where(Launch.launch_site == site)

    rows = db.execute(stmt).all()
    return [AttemptsByYearEntry(year=int(row.year), count=row.count) for row in rows if row.year]


@router.get("/launches", response_model=list[LaunchResponse])
def list_launches(
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    agency: Optional[str] = None,
    state: Optional[str] = None,
    lv_type: Optional[str] = None,
    site: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[LaunchResponse]:
    since_dt = parse_iso_datetime(since)
    until_dt = parse_iso_datetime(until)

    base_stmt = select(Launch).where(Launch.launch_tag.is_not(None))
    if since_dt:
        base_stmt = base_stmt.where(Launch.launch_datetime_utc >= since_dt)
    if until_dt:
        base_stmt = base_stmt.where(Launch.launch_datetime_utc < until_dt)
    if agency:
        base_stmt = base_stmt.where(Launch.launch_agency == agency)
    if state:
        base_stmt = base_stmt.where(Launch.lv_state == state)
    if lv_type:
        base_stmt = base_stmt.where(Launch.lv_type == lv_type)
    if site:
        base_stmt = base_stmt.where(Launch.launch_site == site)

    dedup_stmt = (
        base_stmt.distinct(Launch.launch_tag)
        .order_by(Launch.launch_tag, Launch.launch_datetime_utc.desc().nullslast())
        .subquery()
    )

    outer_stmt = (
        select(dedup_stmt)
        .order_by(dedup_stmt.c.launch_datetime_utc.desc().nullslast())
        .limit(limit)
        .offset(offset)
    )

    rows = db.execute(outer_stmt).all()
    return [
        LaunchResponse(
            launch_tag=row.launch_tag,
            launch_datetime_utc=row.launch_datetime_utc,
            launch_date_raw=row.launch_date_raw,
            launch_agency=row.launch_agency,
            lv_state=row.lv_state,
            lv_type=row.lv_type,
            launch_site=row.launch_site,
            launch_code=row.launch_code,
            name=row.name,
            plname=row.plname,
        )
        for row in rows
    ]


@router.get("/meta/schema", response_model=SchemaMetaResponse)
def schema_meta(db: Session = Depends(get_db)) -> SchemaMetaResponse:
    row_count = db.execute(select(func.count()).select_from(Launch)).scalar_one()
    distinct_launch_count = db.execute(
        select(func.count(func.distinct(Launch.launch_tag))).where(Launch.launch_tag.is_not(None))
    ).scalar_one()
    last_ingest_time = db.execute(select(func.max(Launch.created_at))).scalar_one()

    return SchemaMetaResponse(
        ingestion_version=INGESTION_VERSION,
        last_ingest_time=last_ingest_time,
        row_count=row_count or 0,
        distinct_launch_count=distinct_launch_count or 0,
    )


@router.get("/meta/filters", response_model=FiltersResponse)
def filter_options(db: Session = Depends(get_db)) -> FiltersResponse:
    agencies = [row[0] for row in db.execute(select(func.distinct(Launch.launch_agency)).where(Launch.launch_agency.is_not(None)).order_by(Launch.launch_agency)).all()]
    states = [row[0] for row in db.execute(select(func.distinct(Launch.lv_state)).where(Launch.lv_state.is_not(None)).order_by(Launch.lv_state)).all()]
    lv_types = [row[0] for row in db.execute(select(func.distinct(Launch.lv_type)).where(Launch.lv_type.is_not(None)).order_by(Launch.lv_type)).all()]
    sites = [row[0] for row in db.execute(select(func.distinct(Launch.launch_site)).where(Launch.launch_site.is_not(None)).order_by(Launch.launch_site)).all()]

    return FiltersResponse(
        agencies=agencies,
        states=states,
        lv_types=lv_types,
        sites=sites,
    )
