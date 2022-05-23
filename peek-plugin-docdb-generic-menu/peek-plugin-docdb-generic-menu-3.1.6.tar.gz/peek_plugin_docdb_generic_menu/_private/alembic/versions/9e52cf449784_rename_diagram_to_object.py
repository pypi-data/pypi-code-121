"""rename diagram to object

Peek Plugin Database Migration Script

Revision ID: 9e52cf449784
Revises: bac1e4f7a3d9
Create Date: 2019-07-28 14:35:58.718257

"""

# revision identifiers, used by Alembic.
revision = "9e52cf449784"
down_revision = "bac1e4f7a3d9"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    renameToDocDbSql = """
            DO $$
            BEGIN
                IF EXISTS(
                    SELECT table_schema
                      FROM information_schema.tables
                      WHERE table_schema = 'pl_docdb_generic_menu'
                        AND table_name = 'DiagramGenericMenu'
                  )
                THEN
                  EXECUTE ' ALTER TABLE pl_docdb_generic_menu."DiagramGenericMenu" 
                            RENAME TO "Menu" ';
                END IF;
            END
            $$;
        """
    op.execute(renameToDocDbSql)


def downgrade():
    op.rename_table("Menu", "DiagramGenericMenu", schema="pl_docdb_generic_menu")
