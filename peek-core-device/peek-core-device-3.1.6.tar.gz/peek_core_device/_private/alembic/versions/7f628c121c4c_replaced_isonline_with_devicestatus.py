"""Replaced isOnline with deviceStatus

Peek Plugin Database Migration Script

Revision ID: 7f628c121c4c
Revises: 02f9305f9e7f
Create Date: 2021-03-29 13:29:30.096962

"""

# revision identifiers, used by Alembic.
revision = '7f628c121c4c'
down_revision = '02f9305f9e7f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "DeviceInfo",
        sa.Column(
            "deviceStatus",
            sa.SmallInteger(),
            server_default="0",
            nullable=False
        ),
        schema="core_device",
    )
    op.drop_column("DeviceInfo", "isOnline", schema="core_device")


def downgrade():
    op.add_column(
        "DeviceInfo",
        sa.Column(
            "isOnline",
            sa.Boolean(),
            server_default="0",
            nullable=False
        ),
        schema="core_device",
    )
    op.execute(
        """ 
        UPDATE "core_device"."DeviceInfo" 
        SET "isOnline" = true 
        WHERE "deviceStatus" <> 0 
        """
    )
    op.drop_column("DeviceInfo", "deviceStatus", schema="core_device")
