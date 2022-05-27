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
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="sanjay.bohra@zeno.health,rohan.kamble@zeno.health,"
                                                 "renuka.rawal@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
os.environ['env'] = env
logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()
s3 = S3()

query = f'''
        select
            a."drug-id" ,
            d.composition ,
            d."drug-name"
        from
            "prod2-generico"."prod2-generico"."wh-sku-subs-master" a
        left join "prod2-generico"."prod2-generico".drugs d on
            a."drug-id" = d.id
        left join 
                "prod2-generico"."prod2-generico"."goodaid-incentive-rate-card" b on
            a."drug-id" = b."drug-id" 
        where
            b."drug-id" is null
            and d."company-id" = 6984
            and a."add-wh" = 'Yes'
        group by
            a."drug-id" ,
            d.composition,
            d."drug-name"
            '''
new_drugs =rs_db.get_df(query)
new_drugs.columns = [c.replace('-', '_') for c in new_drugs.columns]
run_date = str(datetime.datetime.now().date())

file_name = 'Goodaid_ATC_SR_and_Incentive_Mapping_{}.csv'.format(str(run_date))

no_of_drugs = len(new_drugs)
logger.info('Total number of miss drugs are {}'.format(no_of_drugs))

drug_names= new_drugs.drug_name.unique()
logger.info('Unique missed drugs are {}'.format(drug_names))


if no_of_drugs > 0:
    # Uploading the file to s3
    new_drugs = s3.save_df_to_s3(df=new_drugs, file_name=file_name)
    # Sending email
    subject = ''' Goodaid ATC SR and Incentive Mapping'''
    mail_body = '''Provide GoodAid Incentive mapping for -{} Drugs
            '''.format(no_of_drugs)
    file_uris = [new_drugs]
    email = Email()
    email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)

    # deleteing the old files
    for uri in file_uris:
        s3.delete_s3_obj(uri=uri)

# Closing the DB Connection
rs_db.close_connection()