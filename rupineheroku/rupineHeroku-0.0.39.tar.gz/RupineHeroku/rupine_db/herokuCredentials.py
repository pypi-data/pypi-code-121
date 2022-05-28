from psycopg2 import sql
from ..rupine_db import herokuDbAccess

def getCredential(connection, schema, chain_id):
    
    username = getCredential(connection, schema, 'ankr_prod', 'USERNAME', chain_id)
    password = getCredential(connection, schema, 'ankr_prod', 'PASSWORD', chain_id)

    return ':'.join([username,password])

def getCredential(connection, schema, credential_name, credential_type, chain_id):
    
    query = sql.SQL("SELECT credentials_value \
           FROM {}.credentials \
           WHERE credentials_name = %s AND  credentials_type = %s AND chain_id = %s").format(sql.Identifier(schema))
    
    params = (credential_name, credential_type, chain_id)
    
    retVal = herokuDbAccess.fetchDataInDatabase(query, params, connection)
    return retVal[0][0]
    