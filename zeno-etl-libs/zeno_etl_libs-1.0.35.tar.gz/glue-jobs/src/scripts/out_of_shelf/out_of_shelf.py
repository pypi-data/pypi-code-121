import os
import sys

import pandas as pd
import datetime as dt
import numpy as np
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

import argparse


def main(debug_mode, as_inactive_exclude_types, db, rs_db_write,  read_schema, write_schema, logger):
    s3 = S3()
    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'
    run_date = dt.date.today()

    logger.info("Getting all store IDs")
    stores = get_stores(db, read_schema)
    store_id_list = list(stores['id'])
    logger.info("All stores ID's fetched!")

    out_of_shelf = pd.DataFrame()
    try:
        # getting oos iteratively
        for store_id in store_id_list:
            logger.info(f"Getting required data for store: {store_id}")

            # getting current inventory
            inventory = get_inventory(db, store_id, read_schema)

            # getting past 30d sales values of drugs in store
            df_30d_sales = get_past_30d_sales(db, store_id, run_date,
                                              read_schema)

            # getting ipc buckets
            df_buckets = get_buckets(db, store_id, read_schema)

            # getting doi info for drugs whose max is set
            doi_class_1 = get_drug_list(db, store_id, read_schema, max_set='Y',
                                        drugs=[])
            doi_class_1["max_set"] = 'Y'

            # getting doi info for drugs whose max is not set,
            # but sold in past 3 months
            drug_list = list(df_30d_sales.drug_id.unique())
            doi_class_2 = get_drug_list(db, store_id, read_schema, max_set='N',
                                        drugs=drug_list)
            doi_class_2["max_set"] = 'N'

            # combine both doi_class tables
            doi_class = doi_class_1.append(doi_class_2)

            # getting std_qty of all drugs in system
            drug_std_qty = get_std_qty(db, read_schema)

            # ==========================================
            #       Out of shelf calculation starts
            # ==========================================
            out_of_shelf_store = doi_class.merge(inventory[['store_id',
                                                            'store_name',
                                                            'drug_id',
                                                            'quantity']],
                                                 on=['store_id', 'drug_id'],
                                                 how='left')
            out_of_shelf_store['quantity'].fillna(0, inplace=True)

            # set OUP = 0, for NPI drugs in max_set = 'N'
            out_of_shelf_store["order_upto_point"] = np.where(
                out_of_shelf_store["max_set"] == 'N',
                0, out_of_shelf_store["order_upto_point"])

            # merging buckets of drugs
            out_of_shelf_store = out_of_shelf_store.merge(df_buckets,
                                                          on=["store_id", "drug_id"],
                                                          how="left")
            out_of_shelf_store["bucket"].fillna('NA', inplace=True)

            # merging std_qty of drugs
            out_of_shelf_store = out_of_shelf_store.merge(drug_std_qty,
                                                          on="drug_id",
                                                          how="left")
            out_of_shelf_store["std_qty"].fillna(1, inplace=True)

            # merging past 30d sales value of store-drugs
            out_of_shelf_store = out_of_shelf_store.merge(df_30d_sales,
                                                          on="drug_id",
                                                          how="left")
            out_of_shelf_store["gross_sales_val"].fillna(0, inplace=True)

            out_of_shelf = out_of_shelf.append(out_of_shelf_store)

        out_of_shelf["closing_date"] = run_date
        logger.info("All stores required data fetched!")

        # calculating store wise OOS percent high-value-ethical
        logger.info("Creating OOS report on store-drug level")
        out_of_shelf["type"] = np.where(
            out_of_shelf["type"] == 'high-value-ethical', 'ethical',
            out_of_shelf["type"])
        out_of_shelf["type"] = np.where(
            out_of_shelf["type"].isin(['generic', 'ethical']),
            out_of_shelf["type"], 'others')

        out_of_shelf["oos_flag"] = np.where(out_of_shelf["quantity"] == 0, 1, 0)

        # adding inv<min (SS) flag
        out_of_shelf["oos_min_flag"] = np.where(
            out_of_shelf["quantity"] < out_of_shelf["safety_stock"], 1, 0)

        # adding inv<std_qty flag
        out_of_shelf["oos_std_qty_flag"] = np.where(
            out_of_shelf["quantity"] < out_of_shelf["std_qty"], 1, 0)

        # adding 30d sales value
        out_of_shelf["oos_sales_loss_30d"] = out_of_shelf["gross_sales_val"] * \
                                             out_of_shelf["oos_flag"]

        out_of_shelf["sales_30d"] = out_of_shelf["gross_sales_val"]

        # exclude as-active = 0 based on specified drug types
        out_of_shelf = out_of_shelf.loc[~((out_of_shelf["as_active"] == 0) &
                                          (out_of_shelf["type"].isin(
                                              as_inactive_exclude_types)))]

        # OOS group store drug level
        out_of_shelf_group = pd.DataFrame(out_of_shelf.groupby(
            ['store_id', 'store_name', 'drug_id', 'drug_name', 'type', 'bucket',
             'drug_grade', 'max_set']).agg(
            {'oos_flag': ['sum', 'count'], 'oos_min_flag': ['sum', 'count'],
             'oos_std_qty_flag': ['sum', 'count'],
             'oos_sales_loss_30d': 'sum', 'sales_30d': 'sum'})).reset_index()
        out_of_shelf_group.columns = [
            'store_id', 'store_name', 'drug_id', 'drug_name', 'type', 'bucket',
            'drug_grade', 'max_set', 'oos_count', 'drug_count',
            'oos_min_count', 'oos_min_drug_count', 'oos_std_qty_count',
            'oos_std_qty_drug_count', 'oos_sales_loss_30d', 'sales_30d']

        # add customer segment info
        customer_segment = get_customer_segment(db, read_schema, interval=90)
        out_of_shelf_group = out_of_shelf_group.merge(
            customer_segment, how='left', on=['store_id', 'drug_id'])
        out_of_shelf_group['customer_type'].fillna('Non-premium', inplace=True)
        out_of_shelf_group['closing_date'] = run_date

        # OOS group store type grade level
        out_of_shelf_drug_group = pd.DataFrame(out_of_shelf.groupby(
            ['store_id', 'store_name', 'type', 'bucket', 'max_set']).agg(
            {'oos_flag': ['sum', 'count'], 'oos_min_flag': ['sum', 'count'],
             'oos_std_qty_flag': ['sum', 'count'], 'oos_sales_loss_30d': 'sum',
             'sales_30d': 'sum'})).reset_index()
        out_of_shelf_drug_group.columns = [
            'store_id', 'store_name', 'type', 'bucket', 'max_set', 'oos_count',
            'drug_count', 'oos_min_count', 'oos_min_drug_count',
            'oos_std_qty_count', 'oos_std_qty_drug_count',
            'oos_sales_loss_30d', 'sales_30d']
        out_of_shelf_drug_group['closing_date'] = run_date

        # required format for RS write
        logger.info("Formatting table for RS-DB write")
        out_of_shelf_group = out_of_shelf_group[['store_id', 'store_name',
                'drug_id', 'drug_name', 'type', 'bucket', 'drug_grade',
                'closing_date', 'max_set', 'customer_type',
                'segment_calculation_date', 'oos_count', 'drug_count',
                'oos_min_count', 'oos_min_drug_count', 'oos_std_qty_count',
                'oos_std_qty_drug_count', 'oos_sales_loss_30d', 'sales_30d']]
        out_of_shelf_group.columns = [c.replace('_', '-') for c in
                                      out_of_shelf_group.columns]

        out_of_shelf_drug_group = out_of_shelf_drug_group[[
                'store_id', 'store_name', 'type', 'bucket', 'closing_date',
                'max_set', 'oos_count', 'drug_count', 'oos_min_count',
                'oos_min_drug_count', 'oos_std_qty_count',
                'oos_std_qty_drug_count', 'oos_sales_loss_30d', 'sales_30d']]
        out_of_shelf_drug_group.columns = [c.replace('_', '-') for c in
                                      out_of_shelf_drug_group.columns]

        out_of_shelf_group['created-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        out_of_shelf_group['created-by'] = 'etl-automation'
        out_of_shelf_group['updated-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        out_of_shelf_group['updated-by'] = 'etl-automation'

        out_of_shelf_drug_group['created-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        out_of_shelf_drug_group['created-by'] = 'etl-automation'
        out_of_shelf_drug_group['updated-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        out_of_shelf_drug_group['updated-by'] = 'etl-automation'

        if debug_mode == 'N':
            logger.info("Writing table to RS-DB")
            logger.info("Writing to table: out-of-shelf-drug-level")
            s3.write_df_to_db(df=out_of_shelf_group,
                              table_name='out-of-shelf-drug-level',
                              db=rs_db_write, schema=write_schema)
            logger.info("Writing to table: out-of-shelf-store-level")
            s3.write_df_to_db(df=out_of_shelf_drug_group,
                              table_name='out-of-shelf-store-level',
                              db=rs_db_write, schema=write_schema)
            logger.info("Writing table to RS-DB completed!")

        else:
            logger.info("Writing to RS-DB skipped")

        # get metrics for email notification
        df_max_set = out_of_shelf_drug_group.loc[out_of_shelf_drug_group["max-set"]=='Y']
        df_ethical = df_max_set.loc[df_max_set["type"] == 'ethical']
        df_generic = df_max_set.loc[df_max_set["type"] == 'generic']
        df_others = df_max_set.loc[df_max_set["type"] == 'others']
        store_count = len(df_max_set["store-id"].unique())
        oos_sys = round((df_max_set["oos-count"].sum() / df_max_set["drug-count"].sum()), 4) * 100
        oos_ethical = round((df_ethical["oos-count"].sum() / df_ethical["drug-count"].sum()), 4) * 100
        oos_generic = round((df_generic["oos-count"].sum() / df_generic["drug-count"].sum()), 4) * 100
        oos_others = round((df_others["oos-count"].sum() / df_others["drug-count"].sum()), 4) * 100

        status = 'Success'
        logger.info(f"OOS code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"OOS code execution status: {status}")
        store_count, oos_sys, oos_ethical, oos_generic, oos_others = 0, 0, 0, 0, 0

    return status, run_date, store_count, oos_sys, oos_ethical, oos_generic, oos_others


def get_stores(db, read_schema):
    q_store = """
    select id
    from "{read_schema}".stores
    where name <> 'Zippin Central'
    and name <> 'Marketing'
    and "is-active" = 1
    and "opened-at" != '0101-01-01 00:00:00'
    and id not in (52, 60, 92, 243, 281)
    """.format(read_schema=read_schema)
    stores = db.get_df(q_store)

    return stores


def get_inventory(db, store_id, read_schema):
    q_inventory = """
    select "store-id" , s.name as "store-name", "drug-id" , 
        sum(quantity) as quantity,
        sum("locked-quantity") as "locked-quantity" , 
        sum(quantity+"locked-quantity"+"locked-for-audit"+
        "locked-for-check"+"locked-for-transfer"+"locked-for-return")
        as "total-system-quantity"
    from "{read_schema}"."inventory-1" i 
    left join "{read_schema}".stores s
    on i."store-id" = s.id
    where "store-id" = {0}
    group by "store-id" , s.name, "drug-id" 
    """.format(store_id, read_schema=read_schema)
    inventory = db.get_df(q_inventory)
    inventory.columns = [c.replace('-', '_') for c in inventory.columns]

    return inventory


def get_past_30d_sales(db, store_id, run_date, read_schema):
    start_date = run_date - dt.timedelta(days=30)
    end_date = run_date
    q_sales = """
    select "drug-id", sum("revenue-value") as "gross-sales-val"
    from "{read_schema}".sales s 
    where "store-id" = {0}
    and "bill-flag" = 'gross'
    and date("created-at") between '{1}' and '{2}'
    group by "drug-id" 
    """.format(store_id, start_date.strftime("%Y-%m-%d"),
               end_date.strftime("%Y-%m-%d"), read_schema=read_schema)
    df_30d_sales = db.get_df(q_sales)
    df_30d_sales.columns = [c.replace('-', '_') for c in df_30d_sales.columns]

    return df_30d_sales


def get_std_qty(db, read_schema):
    q_std_qty = f"""
    select "drug-id" , "std-qty" 
    from "{read_schema}"."drug-std-info" dsi 
    """
    drug_std_qty = db.get_df(q_std_qty)
    drug_std_qty.columns = [c.replace('-', '_') for c in drug_std_qty.columns]

    return drug_std_qty


def get_buckets(db, store_id, read_schema):
    q_latest_buckets = f"""
    (
    select iaxc2."store-id" , iaxc2."drug-id" , concat("bucket-abc", "bucket-xyz") as bucket
    from (select "store-id", max("reset-date") as "reset-date"
            from "{read_schema}"."ipc-abc-xyz-class" iaxc
            where "store-id" = {store_id}
            group by "store-id" ) as "latest-reset"
    inner join "{read_schema}"."ipc-abc-xyz-class" iaxc2
    on iaxc2."store-id" = "latest-reset"."store-id"
    and iaxc2."reset-date" = "latest-reset"."reset-date"
    )
    union 
    (
    select niaxc2."store-id" , niaxc2."drug-id" , concat("bucket-abc", "bucket-xyz") as bucket
    from (select "store-id", max("reset-date") as "reset-date"
            from "{read_schema}"."non-ipc-abc-xyz-class" niaxc
            where "store-id" = {store_id}
            and "store-id" not in (select distinct "store-id" from "{read_schema}"."ipc-abc-xyz-class" iaxc3)
            group by "store-id" ) as "latest-reset"
    inner join "{read_schema}"."non-ipc-abc-xyz-class" niaxc2
    on niaxc2."store-id" = "latest-reset"."store-id"
    and niaxc2."reset-date" = "latest-reset"."reset-date"
    )
    """
    df_latest_buckets = db.get_df(q_latest_buckets)
    df_latest_buckets.columns = [c.replace('-', '_') for c in df_latest_buckets.columns]

    return df_latest_buckets


def get_customer_segment(db, read_schema, interval):
    q_customer_seg = """
    select distinct "store-id" , "drug-id" , seg."segment-calculation-date" , 
	    case 
	    when seg."value-segment" in ('platinum', 'gold', 'silver') then 'Premium'
	    else 'Non-premium'
	    end as "customer-type"
    from "{read_schema}".sales s
    left join (
    select "patient-id" , "segment-calculation-date", "value-segment"
    from "{read_schema}"."customer-value-segment"
    where "segment-calculation-date" = (select max("segment-calculation-date") 
            from "{read_schema}"."customer-value-segment")
    ) as seg on s."patient-id" = seg."patient-id" 
    where DATEDIFF(day, date(s."created-at"), current_date) <= {0}
    and "customer-type" = 'Premium' 
    order by "store-id" , "drug-id"
    """.format(interval, read_schema=read_schema)
    df_customer_seg = db.get_df(q_customer_seg)
    df_customer_seg.columns = [c.replace('-', '_') for c in
                               df_customer_seg.columns]

    return df_customer_seg


def get_drug_list(db, store_id, read_schema, max_set='Y', drugs=None):
    if max_set == 'Y':
        max_condition = "max > 0"
        drugs_condition = ""
    elif max_set == 'N' and drugs != []:
        max_condition = "max = 0"
        drugs_condition = """and "drug-id" in {0}""".format(
            str(drugs).replace('[', '(').replace(']', ')'))
    else:
        max_condition = "max = 0"
        drugs_condition = """and "drug-id" in (0)"""

    # getting max from drug-order-info
    doi_query = """
    select "store-id", "drug-id", "drug-name", type, category, "drug-grade",
    min, doi."safe-stock", max, "as-active"
    from "{read_schema}"."drug-order-info" doi
    join "{read_schema}".drugs d on d.id = doi."drug-id"
    where {1} and d.type not in ('discontinued-products', 'banned')
    and "store-id" = {0}
    {2}
    """.format(store_id, max_condition, drugs_condition,
               read_schema=read_schema)
    doi = db.get_df(doi_query)
    doi.columns = [c.replace('-', '_') for c in doi.columns]
    doi.columns = ['store_id', 'drug_id', 'drug_name', 'type', 'category',
                   'drug_grade', 'safety_stock', 'reorder_point',
                   'order_upto_point', 'as_active']

    return doi


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-d', '--debug_mode', default="Y", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)
    parser.add_argument('-exlist', '--as_inact_ex_types',
                        default="generic,others", type=str,
                        required=True)
    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    debug_mode = args.debug_mode
    email_to = args.email_to
    as_inactive_exclude_types = args.as_inact_ex_types.replace(" ", "").split(",")

    #ensure input is correct
    if not all([i in ['generic', 'ethical', 'others'] for i in as_inactive_exclude_types]):
        as_inactive_exclude_types = ['generic', 'others'] #default types

    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'
    logger = get_logger()
    rs_db = DB()
    rs_db_write = DB(read_only=False)

    # open RS connection
    rs_db.open_connection()
    rs_db_write.open_connection()

    """ calling the main function """
    status, run_date, store_count, oos_sys, oos_ethical, \
        oos_generic, oos_others = main(
            debug_mode, as_inactive_exclude_types, rs_db,
            rs_db_write, read_schema, write_schema, logger)

    # close RS connection
    rs_db.close_connection()
    rs_db_write.close_connection()

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    email.send_email_file(
        subject=f"OOS Job (GLUE-{env}) {run_date}: {status}",
        mail_body=f"""
                    Debug Mode: {debug_mode}
                    Job Params: {args}
                    
                    ===SYSTEM LEVEL===
                    TOTAL   : {oos_sys}%
                    GENERIC : {oos_generic}%
                    ETHICAL : {oos_ethical}%
                    OTHERS  : {oos_others}% 
                    STORES  : {store_count}
                    """,
        to_emails=email_to)

    logger.info("Script ended")
