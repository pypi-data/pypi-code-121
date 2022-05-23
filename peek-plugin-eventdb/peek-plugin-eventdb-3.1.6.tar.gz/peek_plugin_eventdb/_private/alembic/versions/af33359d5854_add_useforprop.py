"""add useForProp

Peek Plugin Database Migration Script

Revision ID: af33359d5854
Revises: 4ea424ad3883
Create Date: 2020-06-04 21:46:35.963318

"""

# revision identifiers, used by Alembic.
revision = "af33359d5854"
down_revision = "4ea424ad3883"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "EventDBProperty", sa.Column("useForPopup", sa.String()), schema="pl_eventdb"
    )


def downgrade():
    op.drop_column("EventDBProperty", "useForPopup", schema="pl_eventdb")
