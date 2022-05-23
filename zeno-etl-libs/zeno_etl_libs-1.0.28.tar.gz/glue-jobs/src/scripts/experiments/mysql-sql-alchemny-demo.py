# !/usr/bin/env python
# coding: utf-8

import sys
import os
sys.path.append('../../../..')
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import MySQL
from zeno_etl_libs.logger import get_logger

import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()
logger.info(f"env: {env}")

mysql = MySQL()
mysql.open_connection()

# ALERT: read_only=False, if you want connection which writes
mysql_write = MySQL(read_only=False)
mysql_write.open_connection()

# select demo
query = "SELECT  * from `prod2-generico`.`test` limit 1"
df = pd.read_sql(sql=query, con=mysql_write.connection)
logger.info(f"df: {df}")

# Insert demo
df[['col1']].to_sql(name='test', con=mysql_write.engine, if_exists='append', index=False,
                    method='multi', chunksize=500, schema='prod2-generico')

# single line update demo
update_q = """
    UPDATE
        `prod2-generico`.`test`
    SET
        `col2` = '{1}'
    WHERE
        `col1` = '{0}'
    """.format('xyz', '123')
logger.info(update_q)
mysql_write.engine.execute(update_q)

# delete demo
delete_q = """
    delete from
        `prod2-generico`.`test`
    WHERE
        `col1` = '{0}'
    """.format('xyz')
logger.info(delete_q)
mysql_write.engine.execute(delete_q)

# Bulk update /update many at the same tome
values_list = [{"col1": "abc", "col2": "xyz"}]
values_tuple = []
for i in values_list:
    values_tuple.append((i['col2'], i['col1']))
logger.info(values_tuple)

""" Query to bulk update """
query = """
    UPDATE
        `test`
    SET
        `col2` = %s
    WHERE 
        `col1` = %s
"""

try:
    a = mysql_write.cursor.executemany(query, values_tuple)
    logger.info(a)
except mysql_write.cursor.Error as e:
    try:
        logger.info("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
    except IndexError:
        logger.info("MySQL Error: %s" % str(e))

mysql_write.close()
mysql.close()
