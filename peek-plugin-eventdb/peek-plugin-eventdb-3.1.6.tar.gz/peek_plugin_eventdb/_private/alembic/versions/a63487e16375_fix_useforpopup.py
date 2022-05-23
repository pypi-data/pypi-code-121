"""fix_useforpopup

Peek Plugin Database Migration Script

Revision ID: a63487e16375
Revises: 0338181f05cf
Create Date: 2020-07-14 12:50:01.280980

"""

# revision identifiers, used by Alembic.
revision = "a63487e16375"
down_revision = "0338181f05cf"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.alter_column(
        "EventDBProperty",
        "useForPopup",
        new_column_name="useForPopup_",
        schema="pl_eventdb",
    )

    op.add_column(
        "EventDBProperty", sa.Column("useForPopup", sa.Boolean()), schema="pl_eventdb"
    )

    op.execute(
        """UPDATE "pl_eventdb"."EventDBProperty"
                  SET "useForPopup" = ("useForPopup_" is not null) """
    )

    op.drop_column("EventDBProperty", "useForPopup_", schema="pl_eventdb")


def downgrade():
    pass
