from sqlalchemy import create_engine, Column, MetaData, literal
from clickhouse_sqlalchemy import Table, make_session, get_declarative_base, types, engines
import pymysql
import pandas as pd
from clickhouse_driver import Client
from trell import aws

def ClickHouse():

    def __init__():

        try:
            self.db_connection_str = "clickhouse://"+aws.cred['CLICKHOUSE_USER']+":"+aws.cred['CLICKHOUSE_PASS']+"@"+aws.cred['CLICKHOUSE_HOST']+":"+ aws.cred['CLICKHOUSE_PORT'] +"/"+ aws.cred['CLICKHOUSE_DB']
            self.db_connection = create_engine(self.db_connection_str)
        except Exception as err:
            print(str(err))

    def write_clickhouse_data(self, dataframe, tableName, dbName):
        try:
            dataframe.to_sql(name=dbName+"."+tableName, con=self.db_connection, if_exists='append', index=False)
        finally:
            self.db_connection.close()

