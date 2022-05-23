"""add isAlarm

Peek Plugin Database Migration Script

Revision ID: e24b71e8ebb5
Revises: a63487e16375
Create Date: 2020-07-14 22:24:49.444308

"""

# revision identifiers, used by Alembic.
revision = "e24b71e8ebb5"
down_revision = "a63487e16375"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "EventDBEvent", sa.Column("isAlarm", sa.Boolean()), schema="pl_eventdb"
    )


def downgrade():
    pass
