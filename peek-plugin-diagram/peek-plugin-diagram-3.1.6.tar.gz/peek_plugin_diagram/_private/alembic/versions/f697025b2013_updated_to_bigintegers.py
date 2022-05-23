"""Updated to BigIntegers

Peek Plugin Database Migration Script

Revision ID: f697025b2013
Revises: 2fc6d3246717
Create Date: 2020-04-29 08:58:57.753872

"""

# revision identifiers, used by Alembic.
revision = "f697025b2013"
down_revision = "2fc6d3246717"
branch_labels = None
depends_on = None

from alembic import op


def _alterColumnPkBigInt(schemaName, tableName):
    return """
        
        DO $$
            DECLARE
                rec RECORD;
            BEGIN
            FOR rec IN SELECT
                        tc.table_schema, 
                        tc.table_name, 
                        kcu.column_name
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                          AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema='%(schemaName)s'
                        AND ccu.table_name='%(tableName)s'
                        AND ccu.column_name='id'
            LOOP 
                EXECUTE 'ALTER TABLE "' || rec.table_schema || '"'
                        ||'."' || rec.table_name || '" '
                        || ' ALTER COLUMN "' || rec.column_name || '" TYPE bigint';
            END LOOP;
            END
        $$;
        
        ALTER TABLE %(schemaName)s."%(tableName)s" ALTER COLUMN id TYPE bigint;
        
        DROP SEQUENCE IF EXISTS %(schemaName)s."%(tableName)s_id_seq" CASCADE;

        CREATE SEQUENCE %(schemaName)s."%(tableName)s_id_seq" AS bigint
            INCREMENT 1
            START 1
            MINVALUE 0
            MAXVALUE 9223372036854775807
            CACHE 1000
            OWNED BY "%(schemaName)s"."%(tableName)s"."%(columnName)s";
    
        SELECT setval('%(schemaName)s."%(tableName)s_%(columnName)s_seq"', 
                max("%(columnName)s") + 1, FALSE)
        FROM %(schemaName)s."%(tableName)s";
        
        ALTER TABLE %(schemaName)s."%(tableName)s"
        ALTER COLUMN "%(columnName)s" SET DEFAULT 
            nextval('%(schemaName)s."%(tableName)s_%(columnName)s_seq"'::regclass);
        """ % dict(
        schemaName=schemaName, tableName=tableName, columnName="id"
    )


def upgrade():
    op.execute(_alterColumnPkBigInt("pl_diagram", "DispBase"))

    op.execute(_alterColumnPkBigInt("pl_diagram", "LiveDbDispLink"))

    op.execute(_alterColumnPkBigInt("pl_diagram", "DispCompilerQueue"))

    op.execute(_alterColumnPkBigInt("pl_diagram", "GridKeyCompilerQueue"))
    op.execute(_alterColumnPkBigInt("pl_diagram", "GridKeyIndexCompiled"))

    op.execute(_alterColumnPkBigInt("pl_diagram", "LocationIndexCompilerQueue"))
    op.execute(_alterColumnPkBigInt("pl_diagram", "LocationIndexCompiled"))

    op.execute(_alterColumnPkBigInt("pl_diagram", "BranchIndex"))
    op.execute(_alterColumnPkBigInt("pl_diagram", "BranchIndexCompilerQueue"))
    op.execute(_alterColumnPkBigInt("pl_diagram", "BranchIndexEncodedChunk"))


def downgrade():
    pass
