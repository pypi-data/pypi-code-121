import argparse
import sys
import os

sys.path.append('../../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from dateutil.relativedelta import relativedelta
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
import pandas as pd
import numpy as np
import dateutil
import datetime
from dateutil.tz import gettz
import gc

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()

s3 = S3()

#########################################################
# Drugs data extraction
########################################################

drugs_q = """
    SELECT
	*
    FROM
	"prod2-generico"."drugs" 
   """
data_drugs = rs_db.get_df(drugs_q)

t_date= datetime.datetime.today().strftime('%Y-%m-%d')

f_name1='drug_master_'+t_date

f_name='drug_master_backup/{}.csv'.format(f_name1)

s3.save_df_to_s3(df=data_drugs, file_name=f_name)


# Closing the DB Connection
rs_db.close_connection()