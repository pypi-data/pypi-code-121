#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz
from zeno_etl_libs.logger import get_logger

import argparse
import pandas as pd
import datetime as dt
import numpy as np


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-cb', '--created_by', default="etl-automation", type=str, required=False)
parser.add_argument('-et', '--email_to', default="sanjay.bohra@zeno.health, shubham.jangir@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
created_by = args.created_by
os.environ['env'] = env


logger = get_logger()
logger.info(f"env: {env}")
logger.info(f"user:{created_by}")

# prod creds below
rs_db = DB()
rs_db.open_connection()

s3 = S3()


# def main(rs_db, s3):
schema = 'prod2-generico'
table_name = 'goodaid-incentive-rate-card'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# getting new drugs incentive data from s3
df = pd.read_csv(s3.download_file_from_s3(file_name="goodaid-incentive-rate/incentive-rate-card.csv"))
logger.info("number of drugs whose incentive has to be updated is: " +str(len(df)))

# data of drugs in the incentive rate card table
query = f'''
        select
            *
        from
            "prod2-generico"."goodaid-incentive-rate-card" girc
        where
            status = 'live'
            '''
data = rs_db.get_df(query)
data.columns = [c.replace('-','_') for c in data.columns]
logger.info("number of live drugs with incentive are: " +str(len(data)))

# setting up start and end date if it has to be updated currently
now = dt.date.today()
then = now + dt.timedelta(days=365)

###########################################################################################
# for durgs which are currently present in the table and their incentive has to be updated
# checking for the existing drugs
data_drug_id= data.drug_id.unique()
bool_series = df.drug_id.isin(data_drug_id)
fill_df = df[bool_series]
logger.info("number of drugs whose incentive has to be updated are: " +str(len(fill_df)))

number_of_drugs = len(fill_df)
if number_of_drugs>0:
    fill_df['incentive_start_date'] = now
    fill_df['incentive_end_date']= then
    fill_df['status']= 'live'
    drug_id_list = fill_df.drug_id.unique()
    if len(list(drug_id_list))<=1:
        logger.info(drug_id_list)
        drug_id_list = str(list(drug_id_list)).replace('[', '(').replace(']', ')')
        logger.info(drug_id_list)
    else:
        drug_id_list = tuple(drug_id_list)
    if isinstance(table_info, type(None)):
        raise Exception(f"table: {table_name} does not exist, create the table first")
    else:
        print(f"Table:{table_name} exists")

    update_query = f''' 
    update "{schema}"."{table_name}" set
        "incentive-end-date" = CURRENT_DATE-1
        ,status = 'not live',
        "updated-at" = current_date 
    where
        "drug-id" in {drug_id_list} and status = 'live' '''
    rs_db.execute(update_query)
    logger.info(f"Table:{table_name} table updated")
    fill_df['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    fill_df['created-by'] = 'etl-automation'
    fill_df['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    fill_df['updated-by'] = 'etl-automation'
    fill_df.columns = [c.replace('_','-') for c in fill_df.columns]
    # =========================================================================
    # append table in Redshift
    # =========================================================================
    if isinstance(table_info, type(None)):
        raise Exception(f"table: {table_name} do not exist, create the table first")
    else:
        print(f"Table:{table_name} exists")

    s3.write_df_to_db(df=fill_df[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)
    logger.info(f"Table:{table_name} table uploaded")

# Providing incentive for newly added drugs
bool_series = ~df.drug_id.isin(data_drug_id)
fill_df = df[bool_series]
logger.info("number of new drugs whose incentive has to be added are: " +str(len(fill_df)))

number_of_drugs = len(fill_df)
if number_of_drugs>0:
    drug_id_list = fill_df.drug_id.unique()
    if len(list(drug_id_list))<=1:
        logger.info(drug_id_list)
        drug_id_list = str(list(drug_id_list)).replace('[', '(').replace(']', ')')
        logger.info(drug_id_list)
    else:
        drug_id_list = tuple(drug_id_list)
    query = f'''
            select
                i."drug-id" as "drug_id",
                MIN(bi."created-at") as "incentive_start_date"
            from
                "prod2-generico"."bill-items-1" bi
            left join "prod2-generico"."inventory-1" i on
                bi."inventory-id" = i.id
            where
                i."drug-id" in {drug_id_list}
            group by
                i."drug-id" '''
    new_data = rs_db.get_df(query)
    new_data.incentive_start_date = pd.to_datetime(new_data.incentive_start_date)
    new_data['incentive_start_date'] = new_data['incentive_start_date'].dt.date
    new_data['incentive_end_date'] = new_data.incentive_start_date + dt.timedelta(days= 365)
    merged_df = pd.merge(fill_df, new_data, how= 'left', on = 'drug_id')
    merged_df['incentive_start_date'].fillna(value=pd.to_datetime(now), inplace=True)
    merged_df['incentive_end_date'].fillna(value=pd.to_datetime(then), inplace=True)
    merged_df['status'] = 'live'
    merged_df.columns = [c.replace('_','-') for c in merged_df.columns]
    merged_df['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    merged_df['created-by'] = 'etl-automation'
    merged_df['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    merged_df['updated-by'] = 'etl-automation'
    # =========================================================================
    # append table in Redshift
    # =========================================================================
    if isinstance(table_info, type(None)):
        raise Exception(f"table: {table_name} do not exist, create the table first")
    else:
        print(f"Table:{table_name} exists")

    s3.write_df_to_db(df=merged_df[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)
    logger.info(f"Table:{table_name} table uploaded")

# getting data from the table which was uploaded by the user
query= '''
        select
            *
        from
            "prod2-generico"."goodaid-incentive-rate-card" girc
        where
            date("created-at")= current_date
        order by
            "drug-id" asc '''

updated_incentives = rs_db.get_df(query)

number_of_incentives_updated = len(updated_incentives)

file_name= 'updated_goodaid_incentives_{}.csv'.format(dt.datetime.today().strftime('%Y-%m-%d'))

if number_of_incentives_updated > 0:
    # Uploading the file to s3
    updated_incentives = s3.save_df_to_s3(df=updated_incentives, file_name=file_name)
    # Sending email
    subject = ''' Goodaid Incentives Updated'''
    mail_body = '''The {} drug_ids for which the incentive was added or updated are in the file attached please review it. 
            '''.format(number_of_incentives_updated)
    file_uris = [updated_incentives]
    email = Email()
    email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)

    # deleteing the old files
    for uri in file_uris:
        s3.delete_s3_obj(uri=uri)

# saving the file to archive which was uploaded by the user on retool
f_name = 'goodaid-incentive-rate/archive/incentive-rate-card_{}.csv'.format(dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S'))
s3.save_df_to_s3(df=df, file_name=f_name)

# deleting the file which was uploaded by the user on retool
uri = 's3://aws-glue-temporary-921939243643-ap-south-1/goodaid-incentive-rate/incentive-rate-card.csv'
s3.delete_s3_obj(uri=uri)

# Closing the DB Connection
rs_db.close_connection()

