"""main wrapper for new-stores safety stock reset"""

import os
import sys
import argparse

import pandas as pd
import numpy as np
import datetime as dt
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

from zeno_etl_libs.utils.new_stores.new_stores_ipc import new_stores_ss_calc
from zeno_etl_libs.utils.new_stores.helper_functions import get_drug_info, order_value_report
from zeno_etl_libs.utils.warehouse.wh_intervention.store_portfolio_consolidation import stores_ss_consolidation
from zeno_etl_libs.utils.ipc.goodaid_substitution import update_ga_ss
from zeno_etl_libs.utils.ipc.doid_update_ss import doid_update


def main(debug_mode, reset_stores, goodaid_ss_flag,
         ga_inv_weight, rest_inv_weight, top_inv_weight, wh_gen_consolidation,
         type_list, rs_db_read, rs_db_write, read_schema, write_schema, s3, logger):

    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'
    reset_date = dt.date.today().strftime("%Y-%m-%d")

    # define empty DF if required in case of fail
    order_value_all = pd.DataFrame()
    new_drug_entries = pd.DataFrame()
    missed_entries = pd.DataFrame()

    try:
        for store_id in reset_stores:
            logger.info("New store SS calculation started for store id: " +
                        str(store_id))

            # NEW STORES SS CALCULATION
            ss_stores = new_stores_ss_calc(store_id, reset_date, rs_db_read,
                                           read_schema, logger)

            # EXTRA INFO FETCH
            data_inv, data_ptr, data_drug_info, data_drug_grade,\
                data_stores = get_drug_info(store_id, rs_db_read, read_schema)

            # MERGE DATA
            ss_stores_merge = ss_stores.merge(
                data_inv[['drug_id', 'current_inventory']],
                how='left', on='drug_id')
            ss_stores_merge = ss_stores_merge.merge(data_ptr, how='left',
                                                    on='drug_id')
            ss_stores_merge = ss_stores_merge.merge(data_drug_info, how='left',
                                                    on='drug_id')
            ss_stores_merge = ss_stores_merge.merge(data_drug_grade, how='left',
                                                    on='drug_id')
            ss_stores_merge = ss_stores_merge.merge(data_stores, how='left',
                                                    on='store_id')

            logger.info("Null values in dataframes, count is {}".format(
                ss_stores_merge.isnull().sum()))

            # fill Null values
            ss_stores_merge['current_inventory'].fillna(0, inplace=True)
            ss_stores_merge['ptr'].fillna(67, inplace=True)
            ss_stores_merge['type'].fillna('', inplace=True)
            ss_stores_merge['category'].fillna('', inplace=True)
            ss_stores_merge['drug_grade'].fillna('NA', inplace=True)

            # final data-frame name for update
            new_stores_ss = ss_stores_merge.copy()

            logger.info("SS list base algo+triggers length is {}".format(
                len(new_stores_ss)))
            logger.info(
                "Types in list are - {}".format(new_stores_ss['type'].unique()))

            # remove banned and discontinued drugs
            new_stores_ss = new_stores_ss[~new_stores_ss['type'].isin(
                ['banned', 'discontinued-products'])]
            logger.info(
                "Types in list are - {}".format(new_stores_ss['type'].unique()))

            logger.info(
                "SS list after removing banned and discontinued -  length is {}".format(
                    len(new_stores_ss)))

            # order value report
            order_value = order_value_report(new_stores_ss)

            # WAREHOUSE GENERIC SKU CONSOLIDATION
            if wh_gen_consolidation == 'Y':
                new_stores_ss, consolidation_log = stores_ss_consolidation(
                    new_stores_ss, rs_db_read, read_schema,
                    min_column='min', ss_column='safety_stock',
                    max_column='max')

            # GOODAID SAFETY STOCK MODIFICATION
            if goodaid_ss_flag == 'Y':
                new_stores_ss, good_aid_ss_log = update_ga_ss(
                    new_stores_ss, store_id, rs_db_read, read_schema,
                    ga_inv_weight, rest_inv_weight,
                    top_inv_weight, substition_type=['generic'],
                    min_column='min', ss_column='safety_stock',
                    max_column='max', logger=logger)


            # few more columns
            new_stores_ss['inventory_quantity'] = new_stores_ss['current_inventory']
            new_stores_ss['fptr'] = new_stores_ss['ptr']
            new_stores_ss['store_id'] = store_id

            new_stores_ss['daily_sales_1'] = -1
            new_stores_ss['daily_sales_2'] = -1
            new_stores_ss['daily_sales_3'] = -1
            new_stores_ss['ads'] = -1
            new_stores_ss['ads_min'] = -1
            new_stores_ss['ads_ss'] = -1
            new_stores_ss['ads_max'] = -1

            new_stores_ss['algo_max_days'] = 30
            # adjustment for ethical
            # same logic as in new_store_ipc_funcs.ss_calc
            new_stores_ss['algo_max_days'] = np.round(
                np.where(new_stores_ss['type'].isin(
                    ['ethical', 'high-value-ethical']),
                    new_stores_ss['algo_max_days'] * (1 / 2),
                    new_stores_ss['algo_max_days'] * (2 / 3)))

            # for min
            new_stores_ss['algo_min_days'] = np.where(new_stores_ss['max'] > 0,
                                                      (new_stores_ss['min'] /
                                                       new_stores_ss['max']
                                                       ) * new_stores_ss[
                                                          'algo_max_days'], 0)
            # for ss
            new_stores_ss['algo_ss_days'] = np.where(new_stores_ss['max'] > 0,
                                                     (new_stores_ss[
                                                          'safety_stock'] /
                                                      new_stores_ss['max']
                                                      ) * new_stores_ss[
                                                         'algo_max_days'], 0)

            new_stores_ss['corr_min'] = new_stores_ss['min']
            new_stores_ss['corr_ss'] = new_stores_ss['safety_stock']
            new_stores_ss['corr_max'] = new_stores_ss['max']
            new_stores_ss['to_order_quantity'] = np.where(
                new_stores_ss['inventory_quantity']
                <= new_stores_ss['corr_ss'],
                new_stores_ss['corr_max'] -
                new_stores_ss['inventory_quantity'],
                0)

            new_stores_ss['to_order_value'] = new_stores_ss['fptr'] * \
                                              new_stores_ss['to_order_quantity']

            # required columns
            new_store_ss = new_stores_ss[[
                'store_id', 'store_name', 'drug_id', 'drug_name', 'type',
                'category', 'drug_grade', 'inventory_quantity',
                'min', 'safety_stock', 'max',
                'daily_sales_1', 'daily_sales_2', 'daily_sales_3',
                'ads', 'ads_min', 'ads_ss', 'ads_max',
                'algo_min_days', 'algo_ss_days', 'algo_max_days',
                'corr_min', 'corr_ss', 'corr_max',
                'to_order_quantity', 'fptr', 'to_order_value', 'algo_type']]

            # overall order value
            order_value_all = order_value_all.append(order_value,
                                                     ignore_index=True)

            # WRITING TO RS-DB
            if debug_mode == 'N':
                logger.info("Writing table to RS-DB")
                # writing table non-ipc-safety-stock
                # new_store_ss['store_id'] = new_store_ss['store_id'].astype(int)
                new_store_ss['reset-date'] = dt.datetime.strptime(reset_date,
                                                                     '%Y-%m-%d').date()
                new_store_ss['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                new_store_ss['created-by'] = 'etl-automation'
                new_store_ss['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                new_store_ss['updated-by'] = 'etl-automation'
                new_store_ss.columns = [c.replace('_', '-') for c in
                                           new_store_ss.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                   table_name='new-store-safety-stock',
                                                   schema=write_schema)
                columns = list(table_info['column_name'])
                new_store_ss = new_store_ss[columns]  # required column order

                logger.info("Writing to table: new-store-safety-stock")
                s3.write_df_to_db(df=new_store_ss,
                                  table_name='new-store-safety-stock',
                                  db=rs_db_write, schema=write_schema)

                # UPLOADING MIN, SS, MAX in DOI-D
                logger.info("Updating new SS to DrugOrderInfo-Data")
                new_store_ss.columns = [c.replace('-', '_') for c in
                                        new_store_ss.columns]
                ss_data_upload = new_store_ss.query('corr_max > 0')[
                    ['store_id', 'drug_id', 'corr_min', 'corr_ss', 'corr_max']]
                new_drug_entries_str, missed_entries_str = doid_update(
                    ss_data_upload, type_list, rs_db_write, write_schema,
                    logger)
                new_drug_entries = new_drug_entries.append(new_drug_entries_str)
                missed_entries = missed_entries.append(missed_entries_str)

            else:
                logger.info("Writing to RS-DB skipped")

            status = 'Success'
            logger.info(f"New-Stores-SS code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"New-Stores-SS code execution status: {status}")

    return status, reset_date, new_drug_entries, missed_entries, order_value_all


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str,
                        required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)

    parser.add_argument('-d', '--debug_mode', default="N", type=str,
                        required=False)
    parser.add_argument('-exsto', '--exclude_stores',
                        default=[52, 60, 92, 243, 281], nargs='+', type=int,
                        required=False)
    parser.add_argument('-gad', '--gaid_flag', default="Y", type=str,
                        required=False)
    parser.add_argument('-giw', '--gaid_inv_wt', default=0.5, type=float,
                        required=False)
    parser.add_argument('-riw', '--rest_inv_wt', default=0.0, type=float,
                        required=False)
    parser.add_argument('-tiw', '--top_inv_wt', default=1, type=float,
                        required=False)
    parser.add_argument('-wgc', '--wh_gen_consld', default="Y", type=str,
                        required=False)
    parser.add_argument('-rs', '--reset_stores',
                        default=[0], nargs='+', type=int, required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to
    debug_mode = args.debug_mode

    # JOB EXCLUSIVE PARAMS
    exclude_stores = args.exclude_stores
    goodaid_ss_flag = args.gaid_flag
    ga_inv_weight = args.gaid_inv_wt
    rest_inv_weight = args.rest_inv_wt
    top_inv_weight = args.rest_inv_wt
    wh_gen_consolidation = args.wh_gen_consld
    reset_stores = args.reset_stores

    logger = get_logger()
    s3 = S3()
    rs_db_read = DB(read_only=True)
    rs_db_write = DB(read_only=False)
    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'

    # open RS connection
    rs_db_read.open_connection()
    rs_db_write.open_connection()

    store_query = """
        select "id", name, "opened-at" as opened_at
        from "{read_schema}".stores
        where name <> 'Zippin Central'
        and "is-active" = 1
        and "opened-at" != '0101-01-01 00:00:00'
        and id not in {0}
        """.format(str(exclude_stores).replace('[', '(').replace(']', ')'),
                   read_schema=read_schema)
    stores = rs_db_read.get_df(store_query)

    # new stores list
    new_stores = stores.loc[
        (dt.datetime.now() - stores['opened_at'] <= dt.timedelta(days=90)) &
        (dt.datetime.now() - stores['opened_at'] >= dt.timedelta(
            days=30)), 'id'].values

    if reset_stores == [0]:  # Fetch all new stores
        reset_stores = new_stores
        logger.info(f"Algo to run for all new stores: {reset_stores}")
    else:
        reset_stores = list(set(reset_stores).intersection(new_stores))
        logger.info(f"Algo to run for specified new stores: {reset_stores}")
        if not reset_stores:
            logger.info(f"ALERT: None of specified stores is a new store")
            reset_stores = new_stores
            logger.info(f"REVERT: Algo to run for all new stores: {reset_stores}")

    type_list = "('ethical', 'ayurvedic', 'generic', 'discontinued-products', " \
                    "'banned', 'general', 'high-value-ethical', 'baby-product'," \
                    " 'surgical', 'otc', 'glucose-test-kit', 'category-2', " \
                    "'category-1', 'category-4', 'baby-food', '', 'category-3')"

    """ calling the main function """
    status, reset_date, new_drug_entries, missed_entries, \
        order_value_all = main(
            debug_mode, reset_stores, goodaid_ss_flag, ga_inv_weight,
            rest_inv_weight, top_inv_weight, wh_gen_consolidation,
            type_list, rs_db_read, rs_db_write, read_schema, write_schema, s3,
            logger)

    # close RS connection
    rs_db_read.close_connection()
    rs_db_write.close_connection()

    # save email attachements to s3
    order_value_all_uri = s3.save_df_to_s3(order_value_all,
                                           file_name=f"order_value_all_{reset_date}.csv")
    new_drug_entries_uri = s3.save_df_to_s3(new_drug_entries,
                                            file_name=f"new_drug_entries_{reset_date}.csv")
    missed_entries_uri = s3.save_df_to_s3(missed_entries,
                                          file_name=f"missed_entries_{reset_date}.csv")

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    email.send_email_file(
        subject=f"New Stores SS Reset (SM-{env}) {reset_date}: {status}",
        mail_body=f"""
                    Debug Mode: {debug_mode}
                    Reset Stores: {reset_stores}
                    Job Params: {args}
                    """,
        to_emails=email_to, file_uris=[order_value_all_uri,
                                       new_drug_entries_uri,
                                       missed_entries_uri])

    logger.info("Script ended")










