"""create launches table

Revision ID: 0001
Revises: 
Create Date: 2024-09-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "launches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(), nullable=False, server_default="gcat"),
        sa.Column("launch_tag", sa.String(), nullable=True),
        sa.Column("piece", sa.String(), nullable=True),
        sa.Column("launch_datetime_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("launch_date_raw", sa.Text(), nullable=True),
        sa.Column("lv_type", sa.Text(), nullable=True),
        sa.Column("launch_site", sa.Text(), nullable=True),
        sa.Column("launch_agency", sa.Text(), nullable=True),
        sa.Column("lv_state", sa.Text(), nullable=True),
        sa.Column("launch_code", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("plname", sa.Text(), nullable=True),
        sa.Column("sat_owner", sa.Text(), nullable=True),
        sa.Column("sat_state", sa.Text(), nullable=True),
        sa.Column("is_orbital", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_launch_attempt", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("launch_tag", "piece", name="uq_launch_tag_piece"),
    )
    op.create_index("ix_launches_launch_tag", "launches", ["launch_tag"], unique=False)
    op.create_index("ix_launches_launch_datetime_utc", "launches", ["launch_datetime_utc"], unique=False)
    op.create_index("ix_launches_launch_agency", "launches", ["launch_agency"], unique=False)
    op.create_index("ix_launches_lv_state", "launches", ["lv_state"], unique=False)
    op.create_index("ix_launches_launch_site", "launches", ["launch_site"], unique=False)
    op.create_index("ix_launches_lv_type", "launches", ["lv_type"], unique=False)
    op.create_index("ix_launches_launch_code", "launches", ["launch_code"], unique=False)


def downgrade():
    op.drop_index("ix_launches_launch_code", table_name="launches")
    op.drop_index("ix_launches_lv_type", table_name="launches")
    op.drop_index("ix_launches_launch_site", table_name="launches")
    op.drop_index("ix_launches_lv_state", table_name="launches")
    op.drop_index("ix_launches_launch_agency", table_name="launches")
    op.drop_index("ix_launches_launch_datetime_utc", table_name="launches")
    op.drop_index("ix_launches_launch_tag", table_name="launches")
    op.drop_table("launches")
