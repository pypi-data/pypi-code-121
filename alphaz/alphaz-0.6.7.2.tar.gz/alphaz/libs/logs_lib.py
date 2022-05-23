from core import core

api     = core.api
db      = core.db

def clear_logs():
    query   = "TRUNCATE logs"
    return db.execute(query)

def get_logs(start_date=None, end_date=None, useLimit=False, pageForLimit=1):
    total = 0
    logs = []
    limit = 20
    start = (pageForLimit - 1) * limit

    query = "SELECT COUNT(*) AS count FROM logs"
    parameters = []
    if start_date is not None and end_date is not None:
        query += " AND CAST(date AS DATE) between %s and %s"
        parameters.append(start_date)
        parameters.append(end_date)       
    query+= " ORDER BY date DESC"

    rows = db.get(query, parameters)
    for row in rows:
        total = row[0]

    query = "SELECT type, origin, message, stack, date FROM logs"
    parameters = []
    if start_date is not None and end_date is not None:
        query += " AND CAST(date AS DATE) between %s and %s"
        parameters.append(start_date)
        parameters.append(end_date)       
    query+= " ORDER BY date DESC"
    if useLimit:
        query+= " LIMIT %s OFFSET %s"
        parameters.append(limit)
        parameters.append(start)

    rows = db.get(query, parameters)        
    for row in rows:
        log = {}
        log["type"] = row[0]
        log["origin"] = row[1]
        log["message"] = row[2]
        log["stack"] = row[3]
        log["date"] = row[4]
        logs.append(log)

    return {'total' : total, 'logs' : logs}