from ..rupine_db import herokuDbAccess
from psycopg2 import sql

def getEvmLatestTokenLiquidityPools(connection, schema, chain_id):
    
    query = sql.SQL("SELECT * FROM {}.v_evm_latest_token_liquidity_pools WHERE chain_id = %s").format(sql.Identifier(schema))
    
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id], connection)    
    return result

def getEvmLatestTokenLiquidityPoolsWithoutName(connection, schema, chain_id, gteCreatedAt):
    
    query = sql.SQL("SELECT * FROM {}.v_evm_latest_token_liquidity_pools WHERE chain_id = %s AND name = 'n/a' AND created_at >= %s").format(sql.Identifier(schema))
    
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection)    
    return result

def getEvmLatestTokenLiquidityPoolsNotLaunched(connection, schema, chain_id, gteCreatedAt):
    
    query = sql.SQL("SELECT * FROM {}.v_evm_latest_token_liquidity_pools WHERE chain_id = %s AND name = 'n/a' AND created_at >= %s").format(sql.Identifier(schema))
    
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection)    
    return result