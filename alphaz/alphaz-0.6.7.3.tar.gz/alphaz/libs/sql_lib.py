def get_strategies_columns(db, table):
    query   = ("SHOW COLUMNS FROM %s")
    columns = db.get_query_results(query,(table),unique=True)