"""add plpython3u

Revision ID: 2efc91c0f0f6
Revises:
Create Date: 2020-04-24 19:43:44.230799

"""

# revision identifiers, used by Alembic.
revision = "2efc91c0f0f6"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    sql = """
        DROP EXTENSION IF EXISTS plpython3u CASCADE;

        CREATE PROCEDURAL LANGUAGE plpython3u
            HANDLER plpython3_call_handler
            INLINE plpython3_inline_handler
            VALIDATOR plpython3_validator;

        ALTER LANGUAGE plpython3u
            OWNER TO peek;
          """
    op.execute(sql)


def downgrade():
    pass
