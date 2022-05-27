import argparse
import sys
import os
from zeno_etl_libs.db.db import DB

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()


query = f"""
    select
        id as "store-id",
        store as "store-name",
        "store-manager" ,
        "line-manager" ,
        abo
    from
        "prod2-generico"."stores-master" sm limit 4
"""

logger.info(f"df: {rs_db.get_df(query=query)}")
