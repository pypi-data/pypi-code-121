from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql

def getAbi(connection, schema, token_address, chain_id):
    
    query = sql.SQL("SELECT abi FROM {}.evm_token \
           WHERE chain_id = %s AND token_address = %s").format(sql.Identifier(schema))
           
    params = (schema, chain_id, token_address)
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result[0][0]

def updateAbi(connection, schema, abi, token_address, chain_id):
    
    query = sql.SQL("UPDATE {}.evm_token \
           SET abi=%s \
           WHERE chain_id = %s AND token_address = %s").format(sql.Identifier(schema))
           
    params = (schema, abi, chain_id, token_address)
    
    herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    