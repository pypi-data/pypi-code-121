#!/usr/bin/env python
# coding: utf-8

# this is include zeno_etl_libs in the python search path on the run time
import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from datetime import datetime as dt
from zeno_etl_libs.logger import get_logger


def main(rs_db, s3, year_month):
    logger = get_logger()
    # year_month = "2021-05"  # eg. "2022-01"
    year_month = year_month or dt.now().strftime("%Y-%m")
    # plain_year_month = year_month.replace("-", "")
    year, month = int(year_month.split("-")[0]), int(year_month.split("-")[1])

    # default_db = "prod2-generico"
    # db_name = f"generico_{plain_year_month}" if year_month_input else default_db

    table_name = "wc-inventory"
    schema = "prod2-generico"

    # Clean the old data for the same month if any
    query = f"""
        delete
        from
            "%s"."%s"
        where
            year = %s
            and month = %s;
    """ % (schema, table_name, year, month)

    rs_db.execute(query=query)
    logger.info(f"Old data cleaned from table: {table_name}, year-month: {year_month}")
    file_name = f"{table_name}_{year}{month}.csv"

    file_s3_uri = f's3://aws-glue-temporary-921939243643-ap-south-1/{file_name}'

    s3.write_to_db_from_s3_csv(
        db=rs_db,
        file_s3_uri=file_s3_uri,
        schema=schema,
        table_name=table_name
    )
    logger.info("Data pushed to table successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-ym', '--year_month', default=None, type=str, required=False, help="YYYY-MM eg. 2022-01")
    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env

    year_month = args.year_month
    print(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    _s3 = S3()

    """ calling the main function """
    main(rs_db=rs_db, s3=_s3, year_month=year_month)

    # Closing the DB Connection
    rs_db.close_connection()
