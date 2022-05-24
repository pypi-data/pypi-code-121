SQL_HISTORY_RANGE = """
                      SELECT min({key_field}) as min_id, 
                             max({key_field}) as max_id 
                       FROM {name}
                    """

SQL_HISTORY_RANGE_NO_INT = """
                            SELECT min(__id__) as min_id, max(__id__) as max_id 
                            FROM (
                                SELECT ROW_NUMBER() OVER (ORDER BY id) as "__id__",
                                                                          *
                                FROM {name}
                            ) AS subquery
                            """

SQL_HISTORY_NO_INT = """
                            SELECT {fields} 
                            FROM (
                                SELECT ROW_NUMBER() OVER (ORDER BY {key_field}) as "__id__",
                                                                          *
                                FROM {name}
                            ) AS subquery
                            WHERE __id__ BETWEEN '{range_from}' AND '{range_to}'
                            """

SQL_HISTORY = """
                 SELECT {fields} 
                    FROM public.{name} 
                 WHERE {key_field} BETWEEN '{range_from}' AND '{range_to}'
               """

SQL_PG_TABLES = """
                   SELECT table_name
                      FROM information_schema.tables
                   WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                      AND table_name not in ({tables_to_exclude})
                """

SQL_CH_TABLES = """
                   SELECT name
                       FROM system.tables
                   WHERE database = '{database}'
                        AND name not in ({tables_to_exclude})
                """

SQL_CH_SCHEMA = """SELECT name, type, comment 
                   FROM system.columns 
                   WHERE database='{database}' AND table='{table}'
                         AND name NOT IN ({exclude_columns})   
                """

SQL_SORT_PART = """SELECT DISTINCT sorting_key, partition_key
                    FROM system.tables
                    WHERE name = '{name}'
                          AND database = '{database}'
                """

SQL_CREATE_AS = """CREATE TABLE {staging_database}.{temp_table_prefix}{table} ON CLUSTER '{{cluster}}' AS {database}.{table} 
                   ENGINE=ReplicatedMergeTree() 
                   PARTITION BY {temp_table_partition_by} ORDER BY ({temp_table_order_by})
                """

SQL_DROP_TABLE = """DROP TABLE IF EXISTS {database}.{prefix}{table} ON CLUSTER '{{cluster}}'"""

SQL_PARTS = """SELECT partition, count() cnt 
               FROM system.parts 
               WHERE database='{database}' AND table='{table}' and active
               GROUP BY partition 
                 HAVING cnt > 1
            """

SQL_EXCHANGE_TABLE = """EXCHANGE TABLES {database_staging}.{prefix}{table} AND {database}.{table} ON CLUSTER '{{cluster}}' """