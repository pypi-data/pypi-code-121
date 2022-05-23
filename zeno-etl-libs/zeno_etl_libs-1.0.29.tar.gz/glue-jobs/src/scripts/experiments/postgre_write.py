import argparse
import sys
import os
import pandas as pd
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import PostGreWrite, PostGre

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()

pg = PostGreWrite()
connection = pg.open_connection()

# logger.info(f"info message: {1}")
# query = f""" select * from temp tt limit 10; """
# df = pd.read_sql_query(sql=query, con=connection)
# logger.info(f"df: {df}")
#
# cursor = connection.cursor()
# cursor.execute('select * from temp tt limit 10;')
# for row in cursor.fetchall():
#     print(row)
#
# truncate_query = ''' truncate table temp; '''
# pg.engine.execute(truncate_query)
new_df = pd.DataFrame([{"col": "abc"}])
new_df.to_sql(
    name='temp', con=pg.engine, if_exists='append',
    chunksize=500, method='multi', index=False)

pg.close_connection()
