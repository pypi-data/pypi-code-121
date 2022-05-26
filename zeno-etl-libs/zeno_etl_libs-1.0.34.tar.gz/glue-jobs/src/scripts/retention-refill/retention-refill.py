#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Purpose - script with database write for retention-refill
# Todo evaluate RS read-write connections later
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

sys.path.append('../../../..')
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

from datetime import datetime
from datetime import timedelta
from dateutil.tz import gettz

import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.jangir@zeno.health", type=str, required=False)
parser.add_argument('-rd', '--runtime_date_exp', default="0101-01-01", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
runtime_date_exp = args.runtime_date_exp
email_to = args.email_to

# env = 'stage'
# limit = 10
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()


def get_drugs():
    # Drugs
    read_schema = 'prod2-generico'
    rs_db.execute(f"set search_path to '{read_schema}'", params=None)
    drugs_q = """
            SELECT
                `id` AS drug_id,
                `composition`,
                `drug-name`,
                `type` AS drug_type,
                `category` AS drug_category,
                `repeatability-index`,
                `is-repeatable`
            FROM
                `drugs`
        """

    drugs_q = drugs_q.replace('`', '"')
    logger.info(drugs_q)

    drugs = rs_db.get_df(query=drugs_q)

    drugs.columns = [c.replace('-', '_') for c in drugs.columns]
    logger.info(len(drugs))

    logger.info("Data for drugs fetched")
    return drugs


def get_drugs_metadata():
    #########################################
    # Drug interval
    #########################################
    # Read drug interval per strip
    # Currently purchase-interval in drug-std-info is not really a per strip interval
    # (since it's at drug-id level, not drug-unit level)
    # But because it's a median, so taking it divided by std-qty as best substitute for per strip interval
    # But later on it must be replaced with correct column/logic for interval_per_strip
    # Todo - evaluate interval per strip condition later

    read_schema = 'prod2-generico'
    rs_db_write.execute(f"set search_path to '{read_schema}'", params=None)

    drugs_metadata_q = """
                SELECT
                    "drug-id",
                    "purchase-interval"/"std-qty" as interval_per_strip
                FROM
                    "drug-std-info-temp"
        """
    drugs_metadata_q = drugs_metadata_q.replace('`', '"')
    logger.info(drugs_metadata_q)

    drugs_metadata = rs_db.get_df(query=drugs_metadata_q)
    drugs_metadata.columns = [c.replace('-', '_') for c in drugs_metadata.columns]
    logger.info("Interval per drug strip, data fetched with "
                "length {}".format(len(drugs_metadata)))

    drugs_metadata['interval_per_strip'] = drugs_metadata['interval_per_strip'].round(2)

    logger.info("Mean value of interval per strip, before imputation {}".format(
        drugs_metadata['interval_per_strip'].mean()))

    # If for any drug, interval is less than 7 days, then make it 7 days
    drugs_metadata['interval_per_strip'] = np.where(drugs_metadata['interval_per_strip'] < 7, 7,
                                                    drugs_metadata['interval_per_strip'])

    # If for any drug, interval is more than 180 days, then make it 180 days
    drugs_metadata['interval_per_strip'] = np.where(drugs_metadata['interval_per_strip'] > 180, 180,
                                                    drugs_metadata['interval_per_strip'])

    logger.info("Mean value of interval per strip, after boundary imputation {}".format(
        drugs_metadata['interval_per_strip'].mean()))
    return drugs_metadata


def batch(store_id, drugs, drugs_metadata):
    # Run date
    if runtime_date_exp != '0101-01-01':
        runtime_date = runtime_date_exp
    else:
        runtime_date = datetime.today().strftime('%Y-%m-%d')

    # runtime_date = '2021-09-01'
    logger.info("Running for {}".format(runtime_date))

    # Period end date
    # Paramatrize it
    period_end_d = (datetime.strptime(runtime_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    # period_end_d = period_end_d_ts.strftime('%Y-%m-%d')

    # Data to be fetched

    #########################################################
    # Bill data
    ########################################################
    read_schema = 'prod2-generico'
    rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    sales_q = """
            SELECT
                s."patient-id",
                s."store-id",
                s."year-created-at" as year_bill,
                s."month-created-at" as month_bill,
                s."created-date" as bill_date,
                s."bill-id",
                s."drug-id",
                NVL(pdi."mean-interval", 0) as mean_interval_hist,
                SUM(s."quantity") as "quantity"
            FROM
                "sales" s
                left join "patient-drug-interval" pdi on
                    pdi."patient-id" = s."patient-id"
                    and pdi."drug-id" = s."drug-id"
            WHERE "store-id" = {0}
                AND s."created-date" <= '{1}'
                AND s."bill-flag" = 'gross'
            group by
                s."patient-id",
                s."store-id",
                s."year-created-at",
                s."month-created-at",
                s."created-date",
                s."bill-id",
                s."drug-id",
                NVL(pdi."mean-interval", 0)
    
    """.format(store_id, period_end_d)
    # AND "store-id" = 2

    logger.info(sales_q)

    data_s = rs_db.get_df(query=sales_q)

    data_s.columns = [c.replace('-', '_') for c in data_s.columns]

    logger.info("Data length is : {}".format(len(data_s)))

    data_s['bill_date'] = pd.to_datetime(data_s['bill_date'])

    # Merge main data, with drugs metadata
    data_raw = data_s.merge(drugs, how='left', on='drug_id')

    data_raw['is_repeatable'] = data_raw['is_repeatable'].fillna(0)
    data_raw['is_generic'] = np.where(data_raw['drug_type'] == 'generic', 1, 0)
    logger.info("Raw data length - {}".format(len(data_raw)))
    data = data_raw

    #######################################
    # Estimated due date
    #######################################

    # # Grp on unique columns
    # data = data_raw.groupby(['patient_id', 'store_id', 'year_bill', 'month_bill',
    #                          'bill_date', 'bill_id', 'composition',
    #                          'drug_id', 'drug_name', 'drug_type',
    #                          'drug_category', 'repeatability_index',
    #                          'is_repeatable', 'is_generic'])[['quantity']].sum().reset_index()

    logger.info("Data length after grouping at unique level - {}".format(len(data)))

    # Impute mean at composition level
    drugs_metadata_merge = drugs[['drug_id', 'composition']].merge(drugs_metadata,
                                                                   how='inner', on=['drug_id'])

    drugs_metadata_merge['interval_per_strip'] = drugs_metadata_merge['interval_per_strip'].fillna(
        drugs_metadata_merge.groupby('composition')['interval_per_strip'].transform('mean')).astype(int)

    logger.info("After imputation - Interval per drug strip, data fetched with "
                "length {}".format(len(drugs_metadata_merge)))

    logger.info("Mean value of interval per strip, after composotion imputation {}".format(
        drugs_metadata_merge['interval_per_strip'].mean()))

    # Merge with refill data
    data = data.merge(drugs_metadata_merge[['drug_id', 'interval_per_strip']],
                      how='left', on=['drug_id'])

    # Don't impute for now, but if were to impute for those not having interval
    # Useful when customer buys new drug label, which is not popular
    # Should it be imputed by avg of other drugs in same comp?

    # Imputed
    # data['interval_per_strip'] = data['interval_per_strip'].fillna(15)

    data['expected_next_interval_drug'] = data['quantity'] * data['interval_per_strip']

    data['expected_next_interval_drug'] = data['expected_next_interval_drug'].round(2)

    logger.info("Mean value of expected interval, at drug level impute {}".format(
        data['expected_next_interval_drug'].mean()))

    logger.info("Data length after merging refill data - {}".format(len(data)))

    ###################################
    # Patient-drug-interval
    ###################################
    # Impute for patient drug id's where it's already consistent

    # If for any drug, interval is less than 7 days, then make it 7 days
    data['mean_interval_hist'] = np.where(((data['mean_interval_hist'] > 0) & (data['mean_interval_hist'] < 7)), 7,
                                          data['mean_interval_hist'])

    # If for any drug, interval is more than 180 days, then make it 180 days
    data['mean_interval_hist'] = np.where(data['mean_interval_hist'] > 180, 180,
                                          data['mean_interval_hist'])

    data['mean_interval_hist'] = data['mean_interval_hist'].round(2)

    logger.info("Mean value of interval, of patient drug interval after boundary imputation {}".format(
        data['mean_interval_hist'].mean()))

    # Number of cases where it will be imputed
    pd_impute_length = len(data[data['mean_interval_hist'] > 0])
    logger.info("Impute to be done for length {}".format(pd_impute_length))

    # Finally impute
    data['expected_next_interval'] = np.where(data['mean_interval_hist'] > 0,
                                              data['mean_interval_hist'],
                                              data['expected_next_interval_drug'])

    logger.info("Mean value of interval, after patient drug level imputation {}".format(
        data['expected_next_interval'].mean()))

    # Remove any nulls
    # Todo - evaluate null interval exclusion condition later
    data = data[data['expected_next_interval'] > 0]
    data['expected_next_interval'] = data['expected_next_interval'].astype(int)
    data = data[data['expected_next_interval'] > 0]

    logger.info("Data length after removing any nulls - {}".format(len(data)))

    # If for any drug, interval is more than 180 days, then make it 180 days
    data['expected_next_interval'] = np.where(data['expected_next_interval'] > 180, 180,
                                              data['expected_next_interval'])

    data['refill_date'] = data['bill_date'] + pd.to_timedelta(data['expected_next_interval'], unit='D')
    data['refill_date'] = pd.to_datetime(data['refill_date'].dt.date)

    data['year_refill'] = data['refill_date'].dt.year
    data['month_refill'] = data['refill_date'].dt.month

    # Refill relevancy flag - for ops oracle
    # Todo write custom logic for refill relevancy for front-end, check confluence documentation
    data['refill_relevancy_flag'] = 1

    # DB upload columns
    final_cols = ['patient_id', 'store_id', 'year_bill', 'month_bill',
                  'bill_date', 'bill_id', 'composition',
                  'drug_id', 'drug_name', 'drug_type', 'drug_category',
                  'repeatability_index', 'is_repeatable', 'is_generic',
                  'quantity', 'interval_per_strip', 'expected_next_interval_drug',
                  'mean_interval_hist', 'expected_next_interval',
                  'refill_date', 'year_refill', 'month_refill',
                  'refill_relevancy_flag']

    data_export = data[final_cols]

    # For redshift specific
    # Convert int columns to int

    for i in ['bill_id', 'drug_id', 'repeatability_index', 'is_repeatable', 'quantity']:
        data_export[i] = data_export[i].fillna(0).astype(int)

    logger.info(data_export.columns)

    ################################
    # DB WRITE
    ###############################

    write_schema = 'prod2-generico'
    write_table_name = 'retention-refill'

    table_info = helper.get_table_info(db=rs_db_write, table_name=write_table_name, schema=write_schema)

    # table_info_clean = table_info[~table_info['column_name'].isin(['id', 'created-at', 'updated-at'])]

    data_export.columns = [c.replace('_', '-') for c in data_export.columns]

    # Mandatory lines
    data_export['created-at'] = datetime.now(
        tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    data_export['created-by'] = 'etl-automation'
    data_export['updated-at'] = datetime.now(
        tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    data_export['updated-by'] = 'etl-automation'

    # Truncate and append
    rs_db_write.execute(f"set search_path to '{write_schema}'", params=None)
    truncate_q = f"""
     DELETE FROM
        "{write_table_name}"
    WHERE "store-id" = {0}
    """
    rs_db_write.execute(truncate_q.format(store_id))

    # Write to DB
    s3.write_df_to_db(df=data_export[table_info['column_name']], table_name=write_table_name,
                      db=rs_db_write, schema=write_schema)
    logger.info("Uploading successful with length: {}".format(len(data_export)))


def get_store_ids():
    query = """
        select
            "store-id"
        from
            "prod2-generico"."bills-1"
        group by
            "store-id"
    """
    store_list = rs_db.get_df(query=query)['store-id'].drop_duplicates().to_list()
    return store_list


def main():
    store_list = get_store_ids()
    drugs = get_drugs()
    drugs_metadata = get_drugs_metadata()
    for store_id in store_list:
        # if store_id not in (2, 4):
        #     continue
        logger.info("running for store id: {}".format(store_id))
        batch(store_id, drugs, drugs_metadata)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        logger.exception(err)
    finally:
        # Closing the DB Connection
        rs_db.close_connection()
        rs_db_write.close_connection()
