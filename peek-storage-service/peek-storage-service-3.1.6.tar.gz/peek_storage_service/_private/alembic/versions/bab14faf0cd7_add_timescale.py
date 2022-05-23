"""add timescale

Revision ID: bab14faf0cd7
Revises: 12a0ab3826f3
Create Date: 2020-05-17 16:07:17.377521

"""

# revision identifiers, used by Alembic.
revision = "bab14faf0cd7"
down_revision = "12a0ab3826f3"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # Extend the database with TimescaleDB
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")


def downgrade():
    pass
