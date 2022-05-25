from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql

def postTaxTransaction(connection, schema, data):

    query = sql.SQL("INSERT INTO {}.tax_transaction (chain_id,chain,public_address,timestamp,block_number,transaction_hash,category,token,amount,usd_value,eur_value) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        data['chain_id'],
        data['chain'],
        data['public_address'],
        data['timestamp'],
        data['block_number'],
        data['transaction_hash'],
        data['category'],
        data['token'],
        data['amount'],
        data['usd_value'],
        data['eur_value'])
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getTaxTransaction(connection, schema, token:str=None, timestamp:int=0, posNegAll:str='all'):
    '''
    Parameters:
        - token: String of Token, e.g. URHT, DUSD-URTH, etc. Default is None
        - timestamp: all data with timestamp gte. Default is 0
        - posNegAll: "positive", "negative" or "all". is Amount gte 0, lt 0 or everything. Default is 'all'
    '''
    conditions = ""
    params = []
    if token != None:
        conditions = conditions + " AND t.token = %s"
        params.append(token)
    
    if posNegAll == 'positive':
        conditions = conditions + " AND t.amount >= 0"
    elif posNegAll == 'negative':
        conditions = conditions + " AND t.amount < 0"

    order = " ORDER BY t.timestamp ASC, c.sort_no ASC"
 
    query = sql.SQL("SELECT t.*,CASE WHEN c.sort_no IS NULL THEN '999' ELSE c.sort_no END AS sort_no FROM {0}.tax_transaction t LEFT JOIN {0}.tax_category c \
        ON t.category = c.category \
        WHERE 1=1 AND t.timestamp >= %s" + conditions + order).format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [timestamp,*params], connection)    
       
    return result


def postTaxReward(connection, schema, data):
    query = sql.SQL("INSERT INTO {}.tax_reward (chain_id,chain,public_address,timestamp,category,token,amount,usd_value,eur_value) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))   
    params = (
        data['chain_id'],
        data['chain'],
        data['public_address'],
        data['timestamp'],
        data['category'],
        data['token'],
        data['amount'],
        data['usd_value'],
        data['eur_value']
    )

    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def postTaxWarehouse(connection, schema, data):
    query = sql.SQL("INSERT INTO {}.tax_warehouse (chain_id,chain,account,day,token,amount,amount_usd,amount_eur,amount_in,amount_in_usd,amount_in_eur,amount_out,amount_out_usd,amount_out_eur,tax_amount_usd,tax_amount_eur) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))   
    params = (
        data['chain_id'],
        data['chain'],
        data['account'],
        data['day'],
        data['token'],
        data['amount'],
        data['amount_usd'],
        data['amount_eur'],
        data['amount_in'],
        data['amount_in_usd'],
        data['amount_in_eur'],
        data['amount_out'],
        data['amount_out_usd'],
        data['amount_out_eur'],
        data['tax_amount_usd'],
        data['tax_amount_eur']
    )

    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def postTaxTrade(connection, schema, data):
    query = sql.SQL("INSERT INTO {}.tax_trades (chain_id,chain,account,address,token,buy_timestamp,buy_price,buy_transaction_hashes,sell_timestamp,sell_price,sell_transaction_hashes,amount) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))   
    params = (
        data['chain_id'],
        data['chain'],
        data['account'],
        data['address'],
        data['token'],
        data['buy_timestamp'],
        data['buy_price'],
        data['buy_transaction_hashes'],
        data['sell_timestamp'],
        data['sell_price'],
        data['sell_transaction_hashes'],
        data['amount']
    )

    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result



# import os
# from dotenv import load_dotenv
# import herokuDbAccess as db
# from datetime import datetime
# load_dotenv()

# if __name__ == '__main__':
#     connection = db.connect(
#         os.environ.get("HEROKU_DB_USER"),
#         os.environ.get("HEROKU_DB_PW"),
#         os.environ.get("HEROKU_DB_HOST"),
#         os.environ.get("HEROKU_DB_PORT"),
#         os.environ.get("HEROKU_DB_DATABASE")
#     )
    # data = {
    #     'chain_id':1,
    #     'chain':'ETH',
    #     'account':'MYACC',
    #     'day':datetime.strptime('2022-12-01','%Y-%m-%d'),
    #     'token':'BLUE1',
    #     'amount':12.2,
    #     'amount_usd':120.1,
    #     'amount_eur':110.23,
    #     'amount_in':1.3,
    #     'amount_in_usd':1.4,
    #     'amount_in_eur':1.5,
    #     'amount_out':1.6,
    #     'amount_out_usd':1.7,
    #     'amount_out_eur':1.8,
    #     'tax_amount_usd':1.9,
    #     'tax_amount_eur':2.0
    # }
    # data = {
    #     'chain_id':1,
    #     'chain':'ETH',
    #     'account':'MYACC',
    #     'address':'dfi1',
    #     'token':'BLUE1',
    #     'buy_timestamp':127897934,
    #     'buy_price':12.4,
    #     'buy_transaction_hashes':'sjdlfjskljdfklsj,jhghjhghj',
    #     'sell_timestamp':893434,
    #     'sell_price':34.35,
    #     'sell_transaction_hashes':'shdsdfjkhsdjkf2,sdjfklj',
    #     'amount':12.2
    # }
    # res = postTaxTrade(connection,'stage',data)
    # print(res)