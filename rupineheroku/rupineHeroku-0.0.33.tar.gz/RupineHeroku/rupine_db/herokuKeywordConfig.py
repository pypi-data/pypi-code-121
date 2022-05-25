from psycopg2 import sql
from ..rupine_db import herokuDbAccess

def postKeywords(connection, schema:str, keyword, keyword_detail, reference, method, value, message):

    query = sql.SQL("INSERT INTO {}.keyword_config (keyword, keyword_detail, reference, method, value, message) \
           VALUES (%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        keyword,
        keyword_detail,
        reference,
        method,
        value,
        message
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getKeywords(connection, schema):
    
    query = sql.SQL("SELECT * FROM {}.keyword_config").format(sql.Identifier(schema))
    
    params =()
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result
 
    