from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql

def postDXSToken(connection, schema, data):

    query = sql.SQL("INSERT INTO {}.dxs_token (timestamp,token_symbol_a,token_symbol_b,blockchain,dex_name,detail,price_usd,transactions,volume,price_change_5m,price_change_1h,price_change_6h,price_change_24h,liquidity,fully_diluted_valuation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        data['timestamp'],
        data['token_symbol_a'],
        data['token_symbol_b'],
        data['blockchain'],
        data['dex_name'],
        data['detail'],
        data['price_usd'],
        data['transactions'],
        data['volume'],
        data['price_change_5m'],
        data['price_change_1h'],
        data['price_change_6h'],
        data['price_change_24h'],
        data['liquidity'],
        data['fully_diluted_valuation'])
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

