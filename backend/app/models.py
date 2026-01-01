from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db import Base


class Launch(Base):
    __tablename__ = "launches"
    __table_args__ = (
        UniqueConstraint("launch_tag", "piece", name="uq_launch_tag_piece"),
        Index("ix_launches_launch_tag", "launch_tag"),
        Index("ix_launches_launch_datetime_utc", "launch_datetime_utc"),
        Index("ix_launches_launch_agency", "launch_agency"),
        Index("ix_launches_lv_state", "lv_state"),
        Index("ix_launches_launch_site", "launch_site"),
        Index("ix_launches_lv_type", "lv_type"),
        Index("ix_launches_launch_code", "launch_code"),
    )

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False, default="gcat")
    launch_tag = Column(String, nullable=True)
    piece = Column(String, nullable=True)
    launch_datetime_utc = Column(DateTime(timezone=True), nullable=True)
    launch_date_raw = Column(Text, nullable=True)
    lv_type = Column(Text, nullable=True)
    launch_site = Column(Text, nullable=True)
    launch_agency = Column(Text, nullable=True)
    lv_state = Column(Text, nullable=True)
    launch_code = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    plname = Column(Text, nullable=True)
    sat_owner = Column(Text, nullable=True)
    sat_state = Column(Text, nullable=True)
    is_orbital = Column(Boolean, nullable=False, default=True)
    is_launch_attempt = Column(Boolean, nullable=False, default=True)
    raw = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
