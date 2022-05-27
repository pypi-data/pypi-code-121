import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
import datetime

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env

rs_db = DB()
rs_db.open_connection()

s3 = S3()

#########################################################
# Drugs data extraction
########################################################

drugs_q = """ SELECT * FROM "prod2-generico"."drugs" """
data_drugs = rs_db.get_df(drugs_q)

f_name = 'drug_master_backup/drug_master_{}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d'))

s3.save_df_to_s3(df=data_drugs, file_name=f_name)

# Closing the DB Connection
rs_db.close_connection()
