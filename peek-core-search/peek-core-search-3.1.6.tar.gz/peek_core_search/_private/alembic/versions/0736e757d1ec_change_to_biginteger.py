"""Change to BigInteger

Peek Plugin Database Migration Script

Revision ID: 0736e757d1ec
Revises: 5e2b9afbb499
Create Date: 2020-05-01 23:58:53.051782

"""

# revision identifiers, used by Alembic.
revision = "0736e757d1ec"
down_revision = "5e2b9afbb499"
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
    op.execute(_alterColumnPkBigInt("core_search", "SearchIndex"))
    op.execute(_alterColumnPkBigInt("core_search", "EncodedSearchIndexChunk"))
    op.execute(_alterColumnPkBigInt("core_search", "SearchIndexCompilerQueue"))

    op.execute(_alterColumnPkBigInt("core_search", "SearchObject"))
    op.execute(_alterColumnPkBigInt("core_search", "EncodedSearchObjectChunk"))
    op.execute(_alterColumnPkBigInt("core_search", "SearchObjectCompilerQueue"))


def downgrade():
    pass
