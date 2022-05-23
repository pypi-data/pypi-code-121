"""add color

Peek Plugin Database Migration Script

Revision ID: 0338181f05cf
Revises: af33359d5854
Create Date: 2020-06-06 20:06:52.966899

"""

# revision identifiers, used by Alembic.
revision = "0338181f05cf"
down_revision = "af33359d5854"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.add_column(
        "EventDBPropertyValue", sa.Column("color", sa.String()), schema="pl_eventdb"
    )


def downgrade():
    op.drop_column("EventDBPropertyValue", "color", schema="pl_eventdb")
