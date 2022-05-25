from psycopg2 import sql
from ..DataStructures import ObjEvmToken
from ..rupine_db import herokuDbAccess

def postEvmToken(connection, schema:str, token:ObjEvmToken):

    query = sql.SQL("INSERT INTO {}.evm_token (token_address, abi, chain_id, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash) \
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        token.token_address,
        token.abi,
        token.chain_id,
        token.symbol,
        token.name,
        token.decimals,
        token.token_class,
        token.totalsupply,
        token.keywords,
        token.telegram_link,
        token.creator_address,
        token.creation_timestamp,
        token.creation_block_number,
        token.creation_tx_hash)
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getEvmToken(connection, schema, chain_id, token_address):
    
    query = sql.SQL("SELECT * FROM {}.evm_token WHERE chain_id = %s AND token_address = %s").format(sql.Identifier(schema))
    
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,token_address], connection)    
    return result

def getEvmTokenWithoutName(connection, schema, chain_id, gteCreatedAt):
    
    query = sql.SQL("SELECT * FROM {}.evm_token WHERE chain_id = %s AND name is NULL AND created_at >= %s").format(sql.Identifier(schema))
    
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection)    
    return result