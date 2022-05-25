def create_temp_table(db, table):
    """ creates table_temp table and truncates the data if table already exists """
    temp_table = table.replace("-", "_") + "_temp"
    query = """
            create temporary table if not exists 
                "%s" (LIKE "prod2-generico"."%s");
        """ % (temp_table, table)

    db.execute(query=query)

    query = """truncate "%s";""" % (temp_table)
    db.execute(query=query)

    return temp_table


def month_diff(date_a, date_b):
    """
    This function returns month difference between calendar dates 'date_a' and 'date_b'
    """
    return 12 * (date_a.dt.year - date_b.dt.year) + (date_a.dt.month - date_b.dt.month)


def drop_table(db, table_name, is_temp=True):
    try:
        if is_temp:
            db.execute(query="""drop table "%s";""" % table_name)
        else:
            db.execute(query="""drop table "prod2-generico"."%s";""" % table_name)
        print(f"table dropped: {table_name}")
    except Exception as e:
        print(f"Error in table drop: {str(e)}")


def get_table_info(db, table_name, schema=None):
    """

    :param db: db class object
    :param table_name: table name
    :param schema: is schema is None --> temp table without schema
    :return: table info data frame
    """
    if schema:
        schema_filter = f"and table_schema = '{schema}'"
    else:
        schema_filter = ''

    query = f"""
        select
            ordinal_position as position,
            column_name,
            data_type,
            case
                when character_maximum_length is not null
                    then character_maximum_length
                else numeric_precision
            end as max_length,
            is_nullable,
            column_default as default_value
        from
            information_schema.columns
        where
            table_name = '{table_name}'
            -- enter table name here
            {schema_filter}
        order by
            ordinal_position;
    """
    db.execute(query=query)
    return db.cursor.fetch_dataframe()
