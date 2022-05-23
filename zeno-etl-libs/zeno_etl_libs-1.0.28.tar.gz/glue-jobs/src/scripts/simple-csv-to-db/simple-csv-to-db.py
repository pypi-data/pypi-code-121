#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Simple csv to RS write
# Upload file to Glue temp bucket
# https://s3.console.aws.amazon.com/s3/buckets/aws-glue-temporary-921939243643-ap-south-1
# edit parameters accordingly
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

import pandas as pd

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.jangir@zeno.health", type=str, required=False)
parser.add_argument('-fn', '--read_file_name', default="random.csv", type=str, required=False)
parser.add_argument('-tn', '--write_table_name', default="random", type=str, required=False)
parser.add_argument('-ws', '--write_schema', default="public", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
read_file_name = args.read_file_name
write_table_name = args.write_table_name
write_schema = args.write_schema

# env = 'stage'
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

# Connections
rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()

df = pd.read_csv(s3.download_file_from_s3(file_name=read_file_name))

# Comment this if not needed
final_cols = ['a','b','c']
df = df[final_cols]

logger.info("Length {}".format(len(df)))

s3.write_df_to_db(df=df, table_name=write_table_name,
                      db=rs_db_write, schema=write_schema)

#################################################
# Closing the DB Connections
rs_db_write.close_connection()

logger.info("File ends")