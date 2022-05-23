#!/usr/bin/env python
# coding: utf-8
# this is included zeno_etl_libs in the python search path on the run time
import os
import sys

sys.path.append('./../../../..')

import pandas as pd
import argparse
from datetime import datetime as dt

from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger


def main(ms_db, rs_db, s3, year_month_input, test_records_limit):
    logger = get_logger()
    ms_cursor = ms_db.open_connection()
    # year_month_input = "2021-08"  # eg. "2022-01"
    year_month = year_month_input or dt.now().strftime("%Y-%m")
    plain_year_month = year_month.replace("-", "")
    year, month = int(year_month.split("-")[0]), int(year_month.split("-")[1])

    # default_db = "test-generico" if env == EnvNames.development else "prod2-generico"
    default_db = "prod2-generico"
    db_name = f"generico_{plain_year_month}" if year_month_input else default_db

    ms_cursor.execute(query=f"use `{db_name}`;")
    # test_records_limit = 1  # None if running for all records
    limit_str = f"LIMIT {test_records_limit} ;" if test_records_limit else ";"

    # Data 1
    query = """
        select
            '2020-09-01' date,
            '' `return-item-id`,
            f.id `invoice-item-id`,
            d.`id` `invoice-id`,
            c.id `inventory-id`,
            '' `return-id`,
            e.`id` `drug-id`,
            e.`drug-name`,
            f.vat gst,
            c.`purchase-rate`,
            c.`expiry`,
            case
                d.`received-at`
                        when '0000-00-00 00:00:00' then '1971-01-01 00:00:00'
                else d.`received-at`
            end `received-at`,
            d.`dispatch-status`,
            case
                d.`dispatched-at`
                        when '0000-00-00 00:00:00' then '1971-01-01 00:00:00'
                else d.`dispatched-at`
            end `invoice-dispatched-at`,
            d.`franchisee-invoice-number`,
            d.`invoice-number`,
            d.`invoice-date`,
            h.name `distributor`,
            g.id `store-id`,
            g.name `store-name`,
            e.`type`,
            c.`locked-quantity` quantity,
            '' `return-reason`,
            '' serial,
            '' `debit-note-status`,
            '1971-01-01 00:00:00' `debit-note-created-at`,
            '1971-01-01 00:00:00' `debit-note-dispatched-at`,
            '1971-01-01 00:00:00' `discarded-at`,
            '' `discard-reason`,
            '' `return-status`,
            '' `return_created_at`,
            '' `returns_created_by`,
            d.`created-by` 'invoice_created_by',
            c.mrp,
            e.pack
        from
            `inventory` c
        join `invoices` d on
            c.`invoice-id` = d.id
        join `drugs` e on
            c.`drug-id` = e.id
        join `invoice-items` f on
            c.`invoice-item-id` = f.id
        join `stores` g on
            c.`store-id` = g.id
        join `distributors` h on
            d.`distributor-id` = h.id
        where
            c.`locked-quantity` > 0
        %s
    """ % limit_str

    df_1 = pd.read_sql_query(query, ms_db.connection)
    logger.info("Data 1, fetched.")
    # Data: 2
    query = """
        select
            '2020-09-01' date,
            '' `return-item-id`,
            f.`invoice-item-reference` `invoice-item-id`,
            d.`id` `invoice-id`,
            c.id `inventory-id`,
            '' `return-id`,
            e.`id` `drug-id`,
            e.`drug-name`,
            f.vat gst,
            k.`purchase-rate`,
            c.`expiry`,
            case
                d.`received-at` when '0000-00-00 00:00:00' then '1971-01-01 00:00:00'
                else d.`received-at`
            end `received-at`,
            d.`dispatch-status`,
            case
                d.`dispatched-at` when '0000-00-00 00:00:00' then '1971-01-01 00:00:00'
                else d.`dispatched-at`
            end `invoice-dispatched-at`,
            d.`franchisee-invoice-number`,
            d.`invoice-number`,
            d.`invoice-date`,
            h.name `distributor`,
            g.id `store-id`,
            g.name `store-name`,
            e.`type`,
            c.`locked-quantity` quantity,
            '' `return-reason`,
            '' serial,
            '' `debit-note-status`,
            '1971-01-01 00:00:00' `debit-note-created-at`,
            '1971-01-01 00:00:00' `debit-note-dispatched-at`,
            '1971-01-01 00:00:00' `discarded-at`,
            '' `discard-reason`,
            '' `return-status`,
            '' `return_created_at`,
            '' `returns_created_by`,
            d.`created-by` 'invoice_created_by',
            c.mrp,
            e.pack
        from
            `inventory-1` c
        join `invoices` d on
            c.`invoice-id` = d.id
        join `drugs` e on
            c.`drug-id` = e.id
        join `invoice-items-1` f on
            c.`invoice-item-id` = f.id
        join `stores` g on
            c.`store-id` = g.id
        join `distributors` h on
            d.`distributor-id` = h.id
        join `inventory` k on
            c.id = k.id
        where
            c.`locked-quantity` > 0
        %s
    """ % limit_str

    df_2 = pd.read_sql_query(query, ms_db.connection)
    logger.info("Data 2, fetched.")
    # # Data: 3
    query = """
        select
            '2020-09-01 ' date,
            a.id `return-item-id`,
            f.id `invoice-item-id`,
            d.`id` `invoice-id`,
            c.id `inventory-id`,
            b.id `return-id`,
            e.`id` `drug-id`,
            e.`drug-name`,
            f.vat gst,
            c.`purchase-rate`,
            c.`expiry`,
            case
                d.`received-at`
            when ' 0000-00-00 00:00:00 ' then ' 1971-01-01 00:00:00 '
                else d.`received-at`
            end `received-at`,
            d.`dispatch-status`,
            case
                d.`dispatched-at`
            when ' 0000-00-00 00:00:00 ' then ' 1971-01-01 00:00:00 '
                else d.`dispatched-at`
            end `invoice-dispatched-at`,
            d.`franchisee-invoice-number`,
            d.`invoice-number`,
            d.`invoice-date`,
            h.name `distributor`,
            g.id `store-id`,
            g.name `store-name`,
            e.`type`,
            a.`returned-quantity` quantity,
            a.`return-reason`,
            i.serial,
            i.`status` `debit-note-status`,
            case
                i.`created-at`
            when ' 0000-00-00 00:00:00 ' then ' 1971-01-01 00:00:00 '
                else i.`created-at`
            end `debit-note-created-at`,
            case
                i.`dispatched-at`
            when ' 0000-00-00 00:00:00 ' then ' 1971-01-01 00:00:00 '
                else i.`dispatched-at`
            end `debit-note-dispatched-at`,
            case
                a.`discarded-at`
            when ' 0000-00-00 00:00:00 ' then ' 1971-01-01 00:00:00 '
                else a.`discarded-at`
            end `discarded-at`,
            a.`discard-reason`,
            a.status `return-status`,
            b.`created-at` `return_created_at`,
            b.`created-by` `returns_created_by`,
            d.`created-by` ' invoice_created_by',
            c.mrp,
            e.pack
        from
            `return-items` a
        join `returns-to-dc` b on
            a.`return-id` = b.id
        join `inventory` c on
            a.`inventory-id` = c.id
        join `invoices` d on
            c.`invoice-id` = d.id
        join `drugs` e on
            c.`drug-id` = e.id
        join `invoice-items` f on
            c.`invoice-item-id` = f.id
        join `stores` g on
            b.`store-id` = g.id
        join `distributors` h on
            d.`distributor-id` = h.id
        left join `debit-notes` i on
            a.`debit-note-reference` = i.id
        where
            a.`status` in ('saved', 'approved')
        %s
    """ % limit_str

    df_3 = pd.read_sql_query(query, ms_db.connection)
    logger.info("Data 3, fetched.")
    # Updating the columns
    df_1.columns = [c.replace('-', '_') for c in df_1.columns]
    df_2.columns = [c.replace('-', '_') for c in df_2.columns]
    df_3.columns = [c.replace('-', '_') for c in df_3.columns]

    df = df_1.append([df_2, df_3])

    df['year'] = year
    df['month'] = month

    # # Insert the data
    table_name = "wc-inventory"
    schema = "prod2-generico"

    # # Clean the old data for the same month if any
    # query = f"""
    #     delete
    #     from
    #         "%s"."%s"
    #     where
    #         year = %s
    #         and month = %s;
    # """ % (schema, table_name, year, month)
    #
    # rs_db.execute(query=query)

    inventory_table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

    df['date'] = pd.to_datetime(df['date']).dt.date
    file_name = f"{table_name}_{year}{month}.csv"

    s3.save_df_to_s3(df=df[list(dict.fromkeys(inventory_table_info['column_name']))], file_name=file_name)

    file_s3_uri = f's3://aws-glue-temporary-921939243643-ap-south-1/{file_name}'

    s3.write_to_db_from_s3_csv(
        db=rs_db,
        file_s3_uri=file_s3_uri,
        schema=schema,
        table_name=table_name
    )
    logger.info(f"Data uploaded to s3 successfully, at {file_s3_uri}")

    # s3.write_df_to_db(
    #     df=df[list(dict.fromkeys(inventory_table_info['column_name']))],
    #     table_name=table_name, db=rs_db, schema=schema
    # )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-ym', '--year_month', default=None, type=str, required=False, help="Year Month eg. 2022-01")
    parser.add_argument('-l', '--limit', default=None, type=int, required=False, help="test records")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env

    year_month = args.year_month
    limit = args.limit
    print(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    ms_db = MySQL()

    _s3 = S3()

    """ calling the main function """
    main(ms_db=ms_db, rs_db=rs_db, s3=_s3, year_month_input=year_month, test_records_limit=limit)

    # Closing the DB Connection
    rs_db.close_connection()
    ms_db.close()
