import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB

import argparse
import pandas as pd
import datetime

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="stage", type=str, required=False)
parser.add_argument('-et', '--email_to', default="kuldeep.singh@zeno.health,vivek.sidagam@zeno.health", type=str, required=False)
parser.add_argument('-si', '--store_id', default=2, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
os.environ['env'] = env
logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()
s3 = S3()

stores_query = f'''
    select
        *
    from
        "prod2-generico"."stores"
    '''
rs_db.execute(query=stores_query, params=None)
stores: pd.DataFrame = rs_db.cursor.fetch_dataframe()
stores.columns = [col.replace('-', '_') for col in stores.columns]

drug_query = f'''
                select
                    id,
                    "drug-name",
                    company,
                    composition,
                    type,
                    pack ,
                    "pack-form",
                    "pack-of",
                    "available-in"
                from
                    "prod2-generico"."drugs"
    '''
rs_db.execute(query=stores_query, params=None)
drugs: pd.DataFrame = rs_db.cursor.fetch_dataframe()
drugs.columns = [col.replace('-', '_') for col in drugs.columns]
run_date = str(datetime.datetime.now().date())

store_file_name = 'stores_state_{}.xlsx'.format(str(run_date))
drugs_file_name = 'drugs_state_{}.xlsx'.format(str(run_date))

# Uploading the file to s3
store_uri = s3.save_df_to_s3(df=stores, file_name=store_file_name)
drugs_uri = s3.save_df_to_s3(df=stores, file_name=drugs_file_name)


# Sending email
subject = ''' Stores and Drugs Master Snapshot '''
mail_body = '''Stores and Drugs Master Snapshot - {}
            '''.format(run_date)
file_uris = [store_uri, drugs_uri]
email = Email()
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)

# deleteing the old files
for uri in file_uris:
    s3.delete_s3_obj(uri=uri)


