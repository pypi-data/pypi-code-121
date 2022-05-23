"""
main wrapper for forecast performance evaluation
author: vivek.revi@zeno.health
"""

import os
import sys
import argparse

import pandas as pd
import datetime as dt
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

from zeno_etl_libs.utils.fcst_performance.helper_functions import get_store_ids, \
    handle_multiple_resets
from zeno_etl_libs.utils.fcst_performance.get_data import GetData
from zeno_etl_libs.utils.fcst_performance.data_operations import cal_fields_store_drug_level


def main(debug_mode, days_to_replenish, days_delta, reset_date, rs_db_read,
         rs_db_write, read_schema, write_schema):
    s3 = S3()
    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'

    # Get store_ids with corresponding store_type-map for above reset date
    store_ids, store_type_map = get_store_ids(reset_date, rs_db_read, read_schema)

    logger.info(f"Store IDs to perform calculations: {store_ids}")

    try:
        # Initialize get_data class object
        get_data = GetData(store_ids, reset_date, days_to_replenish, days_delta,
                           rs_db_read, read_schema, logger)

        logger.info(f"Fetching required data for all stores")
        # Get required raw data for all stores and group by store_id
        df_inv_comb = get_data.curr_inv().groupby("store_id")
        df_sales_comb = get_data.sales_28day().groupby("store_id")
        df_pr_loss_comb = get_data.pr_loss_28day().groupby("store_id")
        df_3m_sales_comb = get_data.sales_3m().groupby("store_id")

        df_sdl_combined = []
        for index, store_id in enumerate(store_ids):
            print(f"Calculations started for store_id: {store_id}")
            logger.info(f"Calculations started for store_id: {store_id}")

            store_type = store_type_map[index]

            # Get uploaded_at cut_off_condition if multiple resets happened
            sql_cut_off_condition = handle_multiple_resets(reset_date, store_id,
                                                           store_type, rs_db_read,
                                                           read_schema, logger)

            if store_type == "ipc":
                df_ss = get_data.ipc_ss(store_id, sql_cut_off_condition)
            else:
                df_ss = get_data.non_ipc_ss(store_id, sql_cut_off_condition)

            # Get store level data from grouped data
            df_inv = df_inv_comb.get_group(store_id)
            df_sales = df_sales_comb.get_group(store_id)
            df_pr_loss = df_pr_loss_comb.get_group(store_id).groupby(
                        "drug_id")["pr_loss"].sum().reset_index()
            df_3m_sales = df_3m_sales_comb.get_group(store_id)

            # Get store-drug level forecast performance table
            logger.info("Creating store-drug level table")
            df_sdl = cal_fields_store_drug_level(df_ss, df_inv, df_sales,
                                                 df_pr_loss, df_3m_sales)

            df_sdl_combined.append(df_sdl)

        df_store_drug_lvl = pd.concat(df_sdl_combined)
        logger.info("All calculations completed")

        # WRITING TO RS-DB
        if debug_mode == 'N':
            logger.info("Writing table to RS-DB")
            df_store_drug_lvl['created-at'] = dt.datetime.now(
                tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
            df_store_drug_lvl['created-by'] = 'etl-automation'
            df_store_drug_lvl['updated-at'] = dt.datetime.now(
                tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
            df_store_drug_lvl['updated-by'] = 'etl-automation'
            df_store_drug_lvl.columns = [c.replace('_', '-') for c in
                                         df_store_drug_lvl.columns]
            table_info = helper.get_table_info(db=rs_db_write,
                                               table_name='forecast-performance-store-drug-level',
                                               schema=write_schema)
            columns = list(table_info['column_name'])
            df_store_drug_lvl = df_store_drug_lvl[columns]  # required column order

            logger.info("Writing to table: forecast-performance-store-drug-level")
            s3.write_df_to_db(df=df_store_drug_lvl,
                              table_name='forecast-performance-store-drug-level',
                              db=rs_db_write, schema=write_schema)

        else:
            logger.info("Writing to RS-DB skipped")

        status = 'Success'
        logger.info(f"Forecast performance code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"Forecast performance code execution status: {status}")


if __name__ == 'main':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str,
                        required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)

    parser.add_argument('-d', '--debug_mode', default="N", type=str,
                        required=False)
    parser.add_argument('-dtr', '--days_to_replenish', default=4, type=int,
                        required=False)
    parser.add_argument('-dd', '--days_delta', default=28, type=int,
                        required=False)
    parser.add_argument('-rd', '--reset_date', default="YYYY-MM-DD",
                        type=str, required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to
    debug_mode = args.debug_mode

    # JOB EXCLUSIVE PARAMS
    days_to_replenish = args.days_to_replenish
    days_delta = args.days_delta
    reset_date = args.reset_date

    logger = get_logger()
    rs_db_read = DB(read_only=True)
    rs_db_write = DB(read_only=False)
    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'

    # Default value: days_to_replenish = 4, days_delta = 28
    if days_delta < 28:
        logger.info(f"INPUT: days_delta = {days_delta} not acceptable, changing to 28")
        days_delta = 28

    # Reset date to look for in ss_table
    if reset_date == 'YYYY-MM-DD':
        reset_date = dt.date.today() - dt.timedelta(days_to_replenish + days_delta)
        logger.info(f"Store reset date selected: {reset_date}")
    else:
        reset_date = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
        logger.info(f"INPUT: Store reset date: {reset_date}")

    # open RS connection
    rs_db_read.open_connection()
    rs_db_write.open_connection()

    """ calling the main function """
    main(debug_mode, days_to_replenish, days_delta, reset_date, rs_db_read,
         rs_db_write, read_schema, write_schema)

    # close RS connection
    rs_db_read.close_connection()
    rs_db_write.close_connection()


