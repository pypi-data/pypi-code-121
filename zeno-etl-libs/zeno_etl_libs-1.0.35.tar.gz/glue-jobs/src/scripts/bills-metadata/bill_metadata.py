#!/usr/bin/env python
# coding: utf-8

import argparse
# this is to include zeno_etl_libs in the python search path on the run time
import sys

sys.path.append('../../../..')
import pandas as pd
import numpy as np
import time
import os

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger

# ## Take the new records from bills and insert them into bills-metadata table
bill_metadata_table = "bills-1-metadata"
patients_metadata_table = "patients-metadata-2"

status = {
    "updated": "updated",
    "pending": "pending",
    "updating": "updating",
}


def insert_new_bills(db, limit, start_date, end_date):
    limit_str = f"limit {limit}" if limit else ""
    if start_date and end_date:
        date_filter = f""" and date(b."created-at") between '{start_date}' and '{end_date}' """
    else:
        date_filter = ""

    query = f'''
         insert into
            "prod2-generico"."{bill_metadata_table}" (
            id,
            "patient-id",
            "zippin-serial",
            "store-id",
            "doctor-id",
            "promo-code-id",
            "promo-flag",
            "promo-discount",
            "payment-method",
            "redeemed-points",
            "created-by",
            "created-at",
            "updated-at",
            "bill-date",
            "bill-year",
            "bill-month",
            "bill-day",
            "etl-status" )
        select
            b.id,
            b."patient-id",
            b."zippin-serial",
            b."store-id",
            b."doctor-id",
            b."promo-code-id",
            case when b."promo-code-id" is null then false else true end ,
            b."promo-discount",
            b."payment-method",
            b."redeemed-points",
            b."created-by",
            b."created-at",
            convert_timezone('Asia/Calcutta', GETDATE()),
            trunc(b."created-at"),
            extract(year from b."created-at"),
            extract(month from b."created-at"),
            extract(day from b."created-at"),
            '{status['pending']}'
        from
            "prod2-generico"."bills-1" b
        left join "prod2-generico"."{bill_metadata_table}" bm on
            bm.id = b.id
        where
            bm.id is null
            {date_filter}
            and (bm."etl-status" != '{status['updated']}'
            or bm."etl-status" is null)
       order by b.id asc
       {limit_str}
    '''
    db.execute(query, params=None)


def mark_old_affected_bills_also_pending(db, start_date, end_date):
    # # Take the effect of below tables
    # - "bills-1"
    # - "patients-store-orders"
    # - "bills-items-1"
    # - "inventory-1"
    # - "drugs"
    if start_date and end_date:
        date_filter = f""" and date(bm."created-at") between '{start_date}' and '{end_date}' """
    else:
        date_filter = ""

    query = f"""
        update
            "prod2-generico"."{bill_metadata_table}" bm2
        set
            "etl-status" = '{status['pending']}',
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE())
        from
            (
            select
                f.id
            from
                "prod2-generico"."{bill_metadata_table}" bm
            inner join
                "prod2-generico"."bills-1" f on
                bm.id = f.id
            inner join "prod2-generico"."bill-items-1" a on
                bm."id" = a."bill-id"
            inner join "prod2-generico"."inventory-1" b on
                a."inventory-id" = b."id"
            inner join "prod2-generico".drugs d on
                b."drug-id" = d.id
            left join "prod2-generico"."patients-store-orders" pso on
                bm.id = NVL(pso."bill-id" , 0)
            where
                ((bm."updated-at" < f."updated-at")
                    or
                (bm."updated-at" < a."updated-at")
                    or
                (bm."updated-at" < b."updated-at")
                    or
                (bm."updated-at" < d."updated-at")
                    or
                (bm."updated-at" < pso."updated-at"))) ab
        where 
            bm2.id = ab.id;
    """
    db.execute(query, params=None)


def mark_pending_bills_updating(db, batch_size):
    query = f"""
        update
            "prod2-generico"."{bill_metadata_table}" bm2
        set
            "etl-status" = '{status['updating']}'
        from
            (
            select
                bm.id
            from
                "prod2-generico"."{bill_metadata_table}" bm
            where
                "etl-status" = '{status['pending']}'
            limit {batch_size} ) ab
        where 
            bm2.id = ab.id;
    """
    db.execute(query, params=None)


def get_changed_bills(db):
    # ## Considering only updating bills
    query = f'''
         select
            id,
            "patient-id",
            "zippin-serial",
            "store-id",
            "doctor-id",
            "promo-code-id",
            "promo-discount",
            "payment-method",
            "redeemed-points",
            "created-by",
            "created-at",
            "updated-at",
            "bill-date",
            "bill-year",
            "bill-month",
            "bill-day",
            "promo-flag",
            "digital-payment-flag",
            "etl-status"
        from
            "prod2-generico"."{bill_metadata_table}" bm3
        where
            "etl-status" = '{status['updating']}'
        order by bm3.id asc
        '''
    db.execute(query, params=None)
    _changed_bills: pd.DataFrame = db.cursor.fetch_dataframe()
    return _changed_bills


def get_numbered_bills(db):
    # ## Min bill date logic to get month difference and month rank
    query = f'''    
        select
            bm.id,
            bm."patient-id",
            bm."created-at" ,
            row_number () over (partition by bm."patient-id" order by "created-at" asc) as row_num,
            bm."bill-year", 
            bm."bill-month", 
            bm."bill-date",
            bm."store-id"
        from
            "prod2-generico"."{bill_metadata_table}" bm
        inner join 
         (
            select
                "patient-id"
            from
                "prod2-generico"."{bill_metadata_table}" 
            where
                "etl-status" = '{status['updating']}'
            group by
                "patient-id") p on
            bm."patient-id" = p."patient-id"
    '''
    db.execute(query, params=None)
    _numbered_bills: pd.DataFrame = db.cursor.fetch_dataframe()
    return _numbered_bills


def get_pr_hd_ecom_flags(db):
    # PR, HD, Ecom flags
    query = f"""
        select
            bm.id,
            bool_or(case when pso."patient-request-id" is null then false else true end) as "pr-flag",
            bool_or(case when pso."order-type" = 'delivery' then true else false end) as "hd-flag",
            bool_or(case when pso."order-source" = 'zeno' then true else false end) as "ecom-flag"
        from
            "prod2-generico"."{bill_metadata_table}" bm
        left join "prod2-generico"."patients-store-orders" pso on
            pso."bill-id" = bm.id
        where
            bm."etl-status" = '{status['updating']}'
        group by
            bm.id
    """
    db.execute(query, params=None)
    _pr_hd_ecom_bills: pd.DataFrame = db.cursor.fetch_dataframe()

    return _pr_hd_ecom_bills


def get_doctor_data(db):
    query = f"""
        select
            bm.id ,
            d."name" as "doctor-name"
        from
            "prod2-generico"."{bill_metadata_table}" bm
        left join "prod2-generico".doctors d on
            bm."doctor-id" = d.id
        where
            bm."etl-status" = '{status['updating']}'
    """
    db.execute(query, params=None)
    _doctors: pd.DataFrame = db.cursor.fetch_dataframe()
    return _doctors


def get_item_drug_inv(db):
    # ## bill item, drug, inventory data
    query = f"""
        select
            bm.id ,
            bi."inventory-id",
            bi."quantity",
            bi."rate",
            i."drug-id" ,
            i."purchase-rate" ,
            i.mrp ,
            i.ptr ,
            i.expiry ,
            d."drug-name" ,
            d."type" ,
            d."drug-name",
            d."type" as "drug-type",
            d.category as "drug-category",
            d."repeatability-index" ,
            d.composition ,
            d.schedule ,
            d."company-id" ,
            d.company ,
            d.pack
        from
            "prod2-generico"."{bill_metadata_table}" bm
        inner join "prod2-generico"."bill-items-1" bi on
            bm.id = bi."bill-id"
        inner join "prod2-generico"."inventory-1" i on
            bi."inventory-id" = i.id
        inner join "prod2-generico".drugs d on
            i."drug-id" = d.id
        where
            bm."etl-status" = '{status['updating']}';
    """

    db.execute(query=query)

    _item_drug_inv: pd.DataFrame = db.cursor.fetch_dataframe()

    return _item_drug_inv


def update_target_table(db, bills1_temp):
    # Updating the Destination table using temp table
    target = bill_metadata_table
    source = bills1_temp
    query = f"""
        update "prod2-generico"."{target}" t
            set "month-diff" = s."month-diff",
                "pr-flag" = s."pr-flag",
                "hd-flag" = s."hd-flag",
                "ecom-flag" = s."ecom-flag",
                "doctor-name" = s."doctor-name",
                "total-spend" = s."total-spend", 
                "spend-generic" = s."spend-generic", 
                "spend-goodaid" = s."spend-goodaid", 
                "spend-ethical" = s."spend-ethical", 
                "spend-others-type" = s."spend-others-type", 
                "num-drugs" = s."num-drugs",
                "quantity-generic" = s."quantity-generic", 
                "quantity-goodaid" = s."quantity-goodaid", 
                "quantity-ethical" = s."quantity-ethical", 
                "quantity-chronic" = s."quantity-chronic", 
                "quantity-repeatable" = s."quantity-repeatable", 
                "quantity-others-type" = s."quantity-others-type", 
                "is-generic" = s."is-generic",
                "is-goodaid" = s."is-goodaid", 
                "is-ethical" = s."is-ethical", 
                "is-chronic" = s."is-chronic", 
                "is-repeatable" = s."is-repeatable", 
                "is-others-type" = s."is-others-type",
                "is-rx" = s."is-rx",
                "total-quantity" = s."total-quantity",
                "total-mrp-value" = s."total-mrp-value", 
                "total-purchase-rate-value" = s."total-purchase-rate-value", 
                "total-ptr-value" = s."total-ptr-value", 
                -- "promo-flag" = s."promo-flag",
                "digital-payment-flag" = s."digital-payment-flag",
                "zippin-serial" = s."zippin-serial",
                "month-bill-rank" = s."month-bill-rank",
                "min-bill-date-in-month" = s."min-bill-date-in-month",
                "store-id-month" = s."store-id-month",
                "normalized-date" = s."normalized-date",
                "etl-status" = '{status['updated']}'
        from "{source}" s
        where t.id = s.id;
    """
    db.execute(query=query)


def mark_affected_patients_pending(db, bills1_temp):
    # ## Update the patients-metadata etl-status
    query = f"""
        update
            "prod2-generico"."{patients_metadata_table}" t
        set
            "etl-status" = '{status['pending']}'
        from
            {bills1_temp} s
        where
            t.id = s."patient-id"
            and s."etl-status" = '{status['updating']}';
    """
    db.execute(query=query)


def process_batch(changed_bills, db, s3):
    changed_bills['digital-payment-flag'] = np.where(
        changed_bills['payment-method'].isin(['', ' ', 'cash', 'cheque']), False, True)
    # print(changed_bills.head(1).transpose())

    numbered_bills = get_numbered_bills(db)
    first_bill = numbered_bills[numbered_bills['row_num'] == 1].rename(
        columns={"created-at": "min-created-at"})[['patient-id', 'min-created-at']]
    # first_bill.head(2)

    # Month bill rank
    bill_rank_month = numbered_bills.sort_values(by=['patient-id', 'bill-year', 'bill-month', 'bill-date']).copy()
    bill_rank_month['month-bill-rank'] = bill_rank_month.groupby(
        ['patient-id', 'bill-year', 'bill-month']).cumcount() + 1
    # bill_rank_month.head(2)

    bill_rank_month_min = bill_rank_month[bill_rank_month['month-bill-rank'] == 1][
        ['patient-id', 'bill-year', 'bill-month', 'bill-date', 'store-id']].rename(
        columns={'bill-date': 'min-bill-date-in-month', 'store-id': 'store-id-month'})
    # bill_rank_month_min.head(2)

    pr_hd_ecom_bills = get_pr_hd_ecom_flags(db)
    # pr_hd_ecom_bills.head(1)

    doctors = get_doctor_data(db)

    item_drug_inv = get_item_drug_inv(db)

    # Measured fields
    item_drug_inv['total-spend'] = item_drug_inv['rate'].astype('float') * item_drug_inv['quantity'].astype('float')
    item_drug_inv['total-mrp-value'] = item_drug_inv['mrp'].astype('float') * item_drug_inv['quantity'].astype(
        'float')
    item_drug_inv['total-purchase-rate-value'] = item_drug_inv['purchase-rate'].astype('float') * item_drug_inv[
        'quantity'].astype('float')
    item_drug_inv['total-ptr-value'] = item_drug_inv['ptr'].astype('float') * item_drug_inv['quantity'].astype(
        'float')

    # Quantity fields
    item_drug_inv['quantity-generic'] = np.where(item_drug_inv['drug-type'] == 'generic', item_drug_inv['quantity'], 0)
    item_drug_inv['quantity-goodaid'] = np.where(item_drug_inv['company'] == 'GOODAID', item_drug_inv['quantity'], 0)
    item_drug_inv['quantity-ethical'] = np.where(item_drug_inv['drug-type'] == 'ethical', item_drug_inv['quantity'], 0)
    item_drug_inv['quantity-others-type'] = np.where(~item_drug_inv['drug-type'].isin(['generic', 'ethical']),
                                                     item_drug_inv['quantity'], 0)
    item_drug_inv['quantity-chronic'] = np.where(item_drug_inv['drug-category'] == 'chronic',
                                                 item_drug_inv['quantity'], 0)

    item_drug_inv['quantity-repeatable'] = np.where(((item_drug_inv['repeatability-index'] >= 80) | (
            (item_drug_inv['drug-category'] == 'chronic') & (item_drug_inv['repeatability-index'] >= 40))),
                                                    item_drug_inv['quantity'], 0)

    # Spend columns
    item_drug_inv['spend-generic'] = np.where(item_drug_inv['drug-type'] == 'generic', item_drug_inv['total-spend'], 0)

    item_drug_inv['spend-goodaid'] = np.where(item_drug_inv['company'] == 'GOODAID', item_drug_inv['total-spend'], 0)

    item_drug_inv['spend-ethical'] = np.where(item_drug_inv['drug-type'] == 'ethical', item_drug_inv['total-spend'], 0)

    item_drug_inv['spend-others-type'] = np.where(~item_drug_inv['drug-type'].isin(['generic', 'ethical']),
                                                  item_drug_inv['total-spend'], 0)

    # aggregation at bill level
    bills_level_data = item_drug_inv.groupby(['id']).agg(
        {'total-spend': 'sum',
         'total-mrp-value': 'sum',
         'total-purchase-rate-value': 'sum',
         'total-ptr-value': 'sum',
         'spend-generic': 'sum',
         'spend-goodaid': 'sum',
         'spend-ethical': 'sum',
         'spend-others-type': 'sum',
         'drug-id': 'nunique',
         'quantity': 'sum',
         'quantity-generic': 'sum',
         'quantity-goodaid': 'sum',
         'quantity-ethical': 'sum',
         'quantity-others-type': 'sum',
         'quantity-chronic': 'sum',
         'quantity-repeatable': 'sum'}).reset_index()

    bills_level_data = bills_level_data.rename(columns={'drug-id': 'num-drugs', 'quantity': 'total-quantity'})

    # bill is generic or not
    bills_level_data['is-generic'] = np.where(bills_level_data['quantity-generic'] > 0, 1, 0)

    # Patient is GOODAID or not
    bills_level_data['is-goodaid'] = np.where(bills_level_data['quantity-goodaid'] > 0, 1, 0)

    # Patient is ethical or not
    bills_level_data['is-ethical'] = np.where(bills_level_data['quantity-ethical'] > 0, 1, 0)

    # Patient is Others type or not
    bills_level_data['is-others-type'] = np.where(bills_level_data['quantity-others-type'] > 0, 1, 0)

    # Patient is RX or not
    bills_level_data['is-rx'] = np.where(
        (bills_level_data['quantity-generic'] + bills_level_data['quantity-ethical']) > 0, 1, 0)

    # Patient is chronic or not
    bills_level_data['is-chronic'] = np.where(bills_level_data['quantity-chronic'] > 0, 1, 0)

    # Patient is repeatable or not
    bills_level_data['is-repeatable'] = np.where(bills_level_data['quantity-repeatable'] > 0, 1, 0)

    # ## Merging data
    # ### month difference data

    # transformed_bills = pd.DataFrame()
    transformed_bills = changed_bills.merge(first_bill, how='inner', on=['patient-id'])
    # print(transformed_bills.head(1).transpose())

    transformed_bills['month-diff'] = helper.month_diff(
        transformed_bills['created-at'], transformed_bills['min-created-at'])
    transformed_bills = transformed_bills.drop(columns=['min-created-at'])

    # ### PR, HD flags Data
    transformed_bills = transformed_bills.merge(pr_hd_ecom_bills, how="left", left_on='id', right_on='id')
    transformed_bills.head(2)

    # ### Doctor Data
    transformed_bills = transformed_bills.merge(doctors, how="left", left_on='id', right_on='id')
    transformed_bills.head(2)

    # ### Drug and inventory  data
    transformed_bills = transformed_bills.merge(bills_level_data, how="left", left_on='id', right_on='id')
    # transformed_bills.columns

    # ### Month bill rank
    transformed_bills = transformed_bills.merge(bill_rank_month[['id', 'month-bill-rank']], how='left', on=['id'])

    # ### Month bill rank min date
    transformed_bills = transformed_bills.merge(
        bill_rank_month_min[['patient-id', 'bill-year', 'bill-month', 'min-bill-date-in-month', 'store-id-month']],
        how='left', on=['patient-id', 'bill-year', 'bill-month']
    )

    # ### Normalise date
    transformed_bills['normalized-date'] = transformed_bills['created-at'].dt.date.values.astype(
        'datetime64[M]').astype('datetime64[D]')
    transformed_bills['normalized-date'] = transformed_bills['normalized-date'].dt.date

    # ### Final column selection
    table_info = helper.get_table_info(db=db, table_name=bill_metadata_table, schema='prod2-generico')

    """correcting the column order"""
    transformed_bills = transformed_bills[table_info['column_name']]

    # ## Updating the data in the target table using temp table
    helper.drop_table(db=db, table_name=bill_metadata_table.replace('-', '_') + "_temp")

    """ Creating temp table """
    bills1_temp = helper.create_temp_table(db=db, table=bill_metadata_table)

    # fillna(-1)
    transformed_bills['num-drugs'] = transformed_bills['num-drugs'].fillna(-1).astype('int64')
    transformed_bills['promo-code-id'] = transformed_bills['promo-code-id'].fillna(-1).astype('int64')
    transformed_bills['total-quantity'] = transformed_bills['total-quantity'].fillna(-1).astype('int64')
    transformed_bills['quantity-generic'] = transformed_bills['quantity-generic'].fillna(-1).astype('int64')
    transformed_bills['quantity-goodaid'] = transformed_bills['quantity-goodaid'].fillna(-1).astype('int64')
    transformed_bills["quantity-ethical"] = transformed_bills["quantity-ethical"].fillna(-1).astype('int64')
    transformed_bills["quantity-chronic"] = transformed_bills["quantity-chronic"].fillna(-1).astype('int64')
    transformed_bills["quantity-repeatable"] = transformed_bills["quantity-repeatable"].fillna(-1).astype('int64')
    transformed_bills["quantity-others-type"] = transformed_bills["quantity-others-type"].fillna(-1).astype('int64')

    transformed_bills['is-generic'] = transformed_bills['is-generic'].fillna(0).astype('int64')
    transformed_bills['is-goodaid'] = transformed_bills['is-goodaid'].fillna(0).astype('int64')
    transformed_bills['is-ethical'] = transformed_bills['is-ethical'].fillna(0).astype('int64')
    transformed_bills['is-chronic'] = transformed_bills['is-chronic'].fillna(0).astype('int64')
    transformed_bills['is-repeatable'] = transformed_bills['is-repeatable'].fillna(0).astype('int64')
    transformed_bills['is-others-type'] = transformed_bills['is-others-type'].fillna(0).astype('int64')
    transformed_bills['is-rx'] = transformed_bills['is-rx'].fillna(0).astype('int64')

    ts = time.time()
    s3.write_df_to_db(df=transformed_bills, table_name=bills1_temp, db=db)
    print(f"total time: {time.time() - ts}")

    """ updating the bill metadata table """
    update_target_table(db, bills1_temp)

    # """ mark affected patients pending """
    # mark_affected_patients_pending(db, bills1_temp)


def get_pending_count(db):
    query = f"""
    select
        count(id)
    from
        "prod2-generico"."{bill_metadata_table}"
    where 
        "etl-status" = '{status['pending']}'
    """
    db.execute(query, params=None)
    _pending: pd.DataFrame = db.cursor.fetch_dataframe()
    return _pending


def main(db, s3, limit, batch_size, start_date, end_date):
    still_pending = True
    insert_new_bills(db, limit, start_date, end_date)
    print("insert_new_bills, done.")
    get_pending_count(db)

    mark_old_affected_bills_also_pending(db, start_date, end_date)
    print("mark_old_affected_bills_also_pending done.")
    get_pending_count(db)

    count = 1
    while still_pending:
        mark_pending_bills_updating(db, batch_size)
        print("mark_pending_bills_updating done.")
        changed_bills = get_changed_bills(db)
        print("get_changed_bills done.")
        if isinstance(changed_bills, type(None)) or changed_bills.empty:
            still_pending = False
            print("Completed all batches.")
        else:
            process_batch(changed_bills=changed_bills, db=db, s3=s3)
            print(f"process_batch done: {count}.")
            count += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-b', '--batch_size', default=500000, type=int, required=False, help="batch size")
    parser.add_argument('-l', '--limit', default=None, type=int, required=False, help="Total bills to process")
    parser.add_argument('-sd', '--start_date', default=None, type=str, required=False)
    parser.add_argument('-ed', '--end_date', default=None, type=str, required=False)
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    logger = get_logger()

    batch_size = args.batch_size
    limit = args.limit

    # This is for new bills
    start_date = args.start_date
    end_date = args.end_date

    logger.info(f"env: {env}, limit: {limit}, batch_size: {batch_size}")

    rs_db = DB()
    rs_db.open_connection()
    _s3 = S3()

    """ calling the main function """
    main(db=rs_db, s3=_s3, limit=limit, batch_size=batch_size, start_date=start_date, end_date=end_date)

    # Closing the DB Connection
    rs_db.close_connection()
