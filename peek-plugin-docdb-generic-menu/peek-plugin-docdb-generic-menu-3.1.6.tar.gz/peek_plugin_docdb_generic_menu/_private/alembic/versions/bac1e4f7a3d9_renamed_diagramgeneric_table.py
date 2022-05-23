"""Renamed DiagramGeneric table

Peek Plugin Database Migration Script

Revision ID: bac1e4f7a3d9
Revises: 1f288982a4e2
Create Date: 2019-06-13 17:05:23.123698

"""

# revision identifiers, used by Alembic.
revision = "bac1e4f7a3d9"
down_revision = "1f288982a4e2"
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
                        AND table_name = 'GenericDiagramMenu'
                  )
                THEN
                  EXECUTE ' ALTER TABLE pl_docdb_generic_menu."GenericDiagramMenu" 
                            RENAME TO "Menu" ';
                END IF;
            END
            $$;
        """
    op.execute(renameToDocDbSql)


def downgrade():
    op.rename_table(
        "DiagramGenericMenu", "GenericDiagramMenu", schema="pl_diagram_generic_menu"
    )
