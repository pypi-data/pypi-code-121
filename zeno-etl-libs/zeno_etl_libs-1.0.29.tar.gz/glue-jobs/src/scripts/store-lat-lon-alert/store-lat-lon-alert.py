import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

import argparse
import pandas as pd


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-et', '--email_to', default="aashish.mishra@zeno.health , tech-support@generico.in , akshay.thorat@zeno.health, vijay.pratap@zeno.health, shubham.jangir@zeno.health, admin@zippin.org, ankit.goyal@zeno.health, ashok.munde@zeno.health, pravin.hiwase@zeno.health, akhil.dua@zeno.health",
                    type=str, required=False)

args, unknown = parser.parse_known_args()

env = args.env
email_to = args.email_to

os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()

s3 = S3()

q_aa = """  
       select
        *
    from
        "prod2-generico"."stores"
    where
        (lat is null
        or lat = '')
        and date("opened-at") != '0101-01-01'  
"""

df_aa = rs_db.get_df(q_aa)
df_aa.columns = [c.replace('-', '_') for c in df_aa.columns]

logger.info('Shape of data',str(df_aa.shape))

flag_count = df_aa.shape[0]

if flag_count>0:
    subject = ''' Store with Lat Lon missing'''
    mail_body = '''Please add latitude longitude for -{} Stores
                '''.format(flag_count)

    alert_df = s3.save_df_to_s3(df=df_aa, file_name='store_alert.csv')

    file_uris = [alert_df]
    email = Email()
    email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)

rs_db.close_connection()



