"""Create Flake table

Revision ID: b8a5f5419306
Revises:
Create Date: 2022-05-19 19:58:05.102181

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "b8a5f5419306"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "flakes_flake",
        sa.Column("id", sa.UnicodeText, primary_key=True),
        sa.Column("name", sa.UnicodeText, nullable=True),
        sa.Column("data", JSONB, nullable=False),
        sa.Column(
            "modified_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "author_id",
            sa.UnicodeText,
            sa.ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column(
            "parent_id", sa.UnicodeText, sa.ForeignKey("flakes_flake.id")
        ),
        sa.Column("extras", JSONB, nullable=False),
        sa.UniqueConstraint("name", "author_id"),
    )


def downgrade():
    op.drop_table("flakes_flake")
