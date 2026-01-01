from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    ok: bool


class LaunchResponse(BaseModel):
    launch_tag: Optional[str]
    launch_datetime_utc: Optional[datetime]
    launch_date_raw: Optional[str]
    launch_agency: Optional[str]
    lv_state: Optional[str]
    lv_type: Optional[str]
    launch_site: Optional[str]
    launch_code: Optional[str]
    name: Optional[str]
    plname: Optional[str]


class OrbitalAttemptsResponse(BaseModel):
    count: int


class AttemptsByYearEntry(BaseModel):
    year: int
    count: int


class SchemaMetaResponse(BaseModel):
    ingestion_version: str
    last_ingest_time: Optional[datetime]
    row_count: int
    distinct_launch_count: int


class FiltersResponse(BaseModel):
    agencies: list[str]
    states: list[str]
    lv_types: list[str]
    sites: list[str]
