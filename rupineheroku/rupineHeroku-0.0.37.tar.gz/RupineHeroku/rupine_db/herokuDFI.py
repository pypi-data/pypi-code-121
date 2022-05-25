from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql

def postDFIOracle(connection, schema, data):

    query = sql.SQL("INSERT INTO {}.dfi_oracle (id,key,is_live,block_number,block_median_timestamp,block_timestamp,active_price,next_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING;").format(sql.Identifier(schema))
    params = (
        data['id'],
        data['key'],
        data['is_live'],
        data['block_number'],
        data['block_median_timestamp'],
        data['block_timestamp'],
        data['active_price'],
        data['next_price']
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getOraclePrice(connection, schema, tokenSymbol:str,timestamp=None,blockNumber=None):
    tokenSymbolQuery = tokenSymbol.upper() + '-USD'
    if timestamp is None and blockNumber is None:
        return None
    elif timestamp is not None:
        query = sql.SQL("SELECT d.id, d.key, d.is_live, d.block_number, d.block_median_timestamp, d.block_timestamp, d.active_price, d.next_price, d.created_at, d.modified_at FROM {0}.dfi_oracle d \
            RIGHT JOIN (SELECT key,MIN(block_timestamp) AS min_block_timestamp FROM {0}.dfi_oracle \
            WHERE 1=1 AND block_timestamp >= %s AND key = %s GROUP BY key) cond \
            ON d.key = cond.key AND d.block_timestamp = cond.min_block_timestamp").format(sql.Identifier(schema))
        params = [timestamp,tokenSymbolQuery]
    else:
        query = sql.SQL("SELECT d.id, d.key, d.is_live, d.block_number, d.block_median_timestamp, d.block_timestamp, d.active_price, d.next_price, d.created_at, d.modified_at FROM {0}.dfi_oracle d \
            RIGHT JOIN (SELECT key,MIN(block_timestamp) AS min_block_timestamp FROM {0}.dfi_oracle \
            WHERE 1=1 AND block_number >= %s AND key = %s GROUP BY key) cond \
            ON d.key = cond.key AND d.block_timestamp = cond.min_block_timestamp").format(sql.Identifier(schema))
        params = [blockNumber,tokenSymbolQuery]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getlatestOracleBlock(connection, schema, tokenSymbol:str):
    tokenSymbolQuery = tokenSymbol + '-USD'
    query = sql.SQL("SELECT MAX(d.block_number) AS max_block_number FROM {0}.dfi_oracle d \
        WHERE 1=1 AND key = %s ").format(sql.Identifier(schema))
    params = [tokenSymbolQuery]
   
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getTokenRisk(connection, schema, hours:int, upside:bool=True, firstWeeks:int=12, percentRnk:float=0.04):
    if upside:
        direction = 'DESC'
    else:
        direction = 'ASC'
    if hours > 0 and hours <= 7*24:
        query = sql.SQL("WITH basis AS (SELECT d.*,row_number() OVER (PARTITION BY d.key ORDER BY block_timestamp desc) AS rownum,count(*) OVER (PARTITION BY d.key) AS data_hours \
                FROM {0}.dfi_oracle d WHERE d.key not in ('BCH-USD','BTC-USD','DFI-USD','ETH-USD','LTC-USD','USDC-USD','USDT-USD','DOGE-USD')), tab AS ( \
                    SELECT b1.*,b1.active_price/b2.active_price -1 AS change,(b1.rownum/7/24)::int AS weeks FROM basis b1 \
                    left join basis b2 ON b1.key = b2.key and b1.rownum = b2.rownum - (%s)::int WHERE b2.id is not null) \
                SELECT first_weeks.key,(4*first_weeks.border+last_weeks.border)/5 AS border FROM ( \
                    SELECT d.key,MIN(d.change) AS border FROM ( \
                        SELECT t.*,percent_rank() OVER (PARTITION BY t.key ORDER BY t.change {1}) AS percent_rnk,count(*) OVER (PARTITION BY t.key) AS data_points FROM tab t \
                        WHERE t.weeks < %s) d \
                    WHERE d.percent_rnk <= %s \
                    GROUP BY d.key) first_weeks \
                LEFT JOIN (SELECT d.key,MIN(d.change) AS border FROM ( \
                    SELECT t.*,percent_rank() OVER (PARTITION BY t.key ORDER BY t.change {1}) AS percent_rnk,count(*) OVER (PARTITION BY t.key) AS data_points FROM tab t \
                    WHERE t.weeks >= %s) d WHERE d.percent_rnk <= %s GROUP BY d.key) last_weeks ON first_weeks.key = last_weeks.key ORDER BY 2").format(sql.Identifier(schema),sql.SQL(direction))
        params = [hours,firstWeeks,percentRnk,firstWeeks,percentRnk]
    
        result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
        return result
    else:
        return None


def postDFIBotEvent(connection, schema, data):
    if 'risk' not in data:
        data['risk'] = None
    
    query = sql.SQL("INSERT INTO {}.dfi_bot (id,address,block_number,future_settlement_block,loan,loan_token,loan_oracle_price,loan_dex_price,invest_type,sentiment,risk,is_active,waiting_for_loan_payback) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);").format(sql.Identifier(schema))
    params = (
        data['id'],
        data['address'],
        data['block_number'],
        data['future_settlement_block'],
        data['loan'],
        data['loan_token'],
        data['loan_oracle_price'],
        data['loan_dex_price'],
        data['invest_type'],
        data['sentiment'],
        data['risk'],
        'Y',
        'N'
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def putDFIBotEventInvest(connection, schema, data):
    query = sql.SQL("UPDATE {}.dfi_bot SET invest = %s, invest_token = %s, invest_oracle_price =%s, invest_dex_price = %s WHERE id = %s AND address = %s").format(sql.Identifier(schema))
    params = (
        data['invest'],
        data['invest_token'],
        data['invest_oracle_price'],
        data['invest_dex_price'],
        data['id'],
        data['address'],
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def putDFIBotEventAddLiquidity(connection, schema, data):
    query = sql.SQL("UPDATE {}.dfi_bot SET lp_pool_tokens = %s WHERE id = %s AND address = %s").format(sql.Identifier(schema))
    params = (
        data['lp_pool_tokens'],
        data['id'],
        data['address'],
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def putDFIBotEventROI(connection, schema, data):
    query = sql.SQL("UPDATE {}.dfi_bot SET expected_roi = %s WHERE id = %s AND address = %s").format(sql.Identifier(schema))
    params = (
        data['expected_roi'],
        data['id'],
        data['address'],
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def changeDFIBotEventStatus(connection, schema, data):
    status = None
    params = []
    if 'is_active' in data:
        status = ' is_active = %s'
        params.append(data['is_active'])
    if 'waiting_for_loan_payback' in data:
        if status is None:
            status = ' waiting_for_loan_payback = %s'
        else:
            status = status + ', waiting_for_loan_payback = %s'
        params.append(data['waiting_for_loan_payback'])

    if status is not None:
        query = sql.SQL("UPDATE {}.dfi_bot SET %s WHERE id = %%s AND address = %%s" % status).format(sql.Identifier(schema))
        params.append(data['id'])
        params.append(data['address'])
        params = tuple(params)

        result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
        return result
    else:
        return None

def getDFIBotEvents(connection, schema, address:str,is_active:bool=True,waiting_for_loan_payback:bool=None):
    if is_active == True:
        condition = " AND d.is_active = 'Y'"
    elif is_active == False:
        condition = " AND d.is_active = 'N'"
    else:
        condition = ''

    if waiting_for_loan_payback == True:
        condition = condition + " AND d.waiting_for_loan_payback = 'Y'"
    elif waiting_for_loan_payback == False:
        condition = condition + " AND d.waiting_for_loan_payback = 'N'"
    else:
        condition = condition

    query = sql.SQL("SELECT * FROM {0}.dfi_bot d \
        WHERE 1=1 AND d.address = %%s %s" % (condition)).format(sql.Identifier(schema))
    params = [address]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getDFIBotControl(connection, schema, address:str):
    query = sql.SQL("SELECT address,is_active FROM {0}.dfi_bot_control WHERE 1=1 AND address = %s").format(sql.Identifier(schema))
    params = [address]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def putDFIBotControl(connection, schema, address:str,flag:str):
    if len(getDFIBotControl(connection,schema,address)) == 0:
        query = sql.SQL("INSERT INTO {}.dfi_bot_control (address,is_active) VALUES (%s,%s);").format(sql.Identifier(schema))
        params = (
        address,
        flag
    )
    else:
        query = sql.SQL("UPDATE {}.dfi_bot_control SET is_active = %s WHERE address = %s").format(sql.Identifier(schema))
        params = (
            flag,
            address
        )
    print(query)
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

# import os
# from dotenv import load_dotenv
# import herokuDbAccess as db
# load_dotenv()

# def convertToType(data,type):
#     if data is None:
#         return None
#     else:
#         return type(data)
# def assignDBResponse(res:tuple):
#     return {
#         'id':res[0],
#         'address':res[1],
#         'block_number':res[2],
#         'future_settlement_block':res[3],
#         'loan':convertToType(res[4],float),
#         'loan_token':res[5],
#         'loan_oracle_price':convertToType(res[6],float),
#         'loan_dex_price':convertToType(res[7],float),
#         'invest_type':res[8],
#         'sentiment':res[9],
#         'risk':convertToType(res[10],float),
#         'invest':convertToType(res[11],float),
#         'invest_token':res[12],
#         'invest_oracle_price':convertToType(res[13],float),
#         'invest_dex_price':convertToType(res[14],float),
#         'lp_pool_tokens':convertToType(res[15],float),
#     }

# if __name__ == '__main__':
#     connection = db.connect(
#         os.environ.get("HEROKU_DB_USER"),
#         os.environ.get("HEROKU_DB_PW"),
#         os.environ.get("HEROKU_DB_HOST"),
#         os.environ.get("HEROKU_DB_PORT"),
#         os.environ.get("HEROKU_DB_DATABASE")
#     )

#     res = putDFIBotcontrol(connection,'stage','dfi1','N')
#     print(res)
    # data = {
    #     'id':'1003718-tf1q6qj52ykxlf6halmx0g32gaumuuptactwgrqh23-MSFT',
    #     'address':'tf1q6qj52ykxlf6halmx0g32gaumuuptactwgrqh23',
    #     'expected_roi':13,
    #     'is_active':'N',
    #     'waiting_for_loan_payback':'Y'
    # } 
#     putDFIBotEventROI(connection,os.environ.get("ENVIRONMENT"),data)
#     changeDFIBotEventStatus(connection,os.environ.get("ENVIRONMENT"),data)
    #print(getTokenRisk(connection,'prod',4))
    # data = {
    #     'id':'dfi1-123-TSLA',
    #     'address':'dfi1',
    #     'is_active':'Y' 
    # }
    # changeDFIBotEventStatus(connection,'stage',data)

    # trades = getDFIBotEvents(connection,'stage','dfi1',True)
    # for t in trades:
    #     print(assignDBResponse(t))
