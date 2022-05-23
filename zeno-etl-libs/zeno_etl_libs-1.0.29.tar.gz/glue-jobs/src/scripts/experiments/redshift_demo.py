import argparse
import os
import sys

import zipfile

zip_ref = zipfile.ZipFile('./psycopg2.zip', 'r')
zip_ref.extractall('/tmp/packages')
zip_ref.close()
sys.path.insert(0, '/tmp/packages')

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import RedShift

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env


logger = get_logger()
rs = RedShift()
connection = rs.open_connection()

""" calling the main function """
# main(logger=_logger, rs=_rs)


logger.info(f"info message: {1}")
query = f""" select * from "prod2-generico"."actions" limit 1;"""
df = pd.read_sql(query, con=rs.connection)
logger.info(f"df: {df}")

# rs_pg = RedShiftPG8000(secrets=config.secrets)
# rs_pg.open_connection()
# rs_pg.execute(query)
# data = rs_pg.cursor.fetch_dataframe()
# logger.info(f"df2: {data}")

# rs.execute(query=f""" delete from "prod2-generico".test_2 where id > 2 """)
#
# query = f"""
#     insert into  "prod2-generico".test_2 ("action") values ('Check2');
#     """
# rs.execute(query=query)

rs.close_connection()
