import argparse
import os
import sys
import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.db.db import RedShift

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()
query = f"""select * from "prod2-generico"."sales-agg" limit 1;"""
rs_db.execute(query, params=None)
test_df: pd.DataFrame = rs_db.cursor.fetch_dataframe()
logger.info(test_df)
rs_db.close_connection()

db2 = RedShift()
db2.open_connection()
db2.close_connection()