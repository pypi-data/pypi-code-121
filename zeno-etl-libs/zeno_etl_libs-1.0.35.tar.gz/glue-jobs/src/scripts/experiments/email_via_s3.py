#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB

import argparse
import pandas as pd


def main():
    rs_db = DB()
    try:
        rs_db.open_connection()

        # s3 = S3()
        #
        # df = pd.DataFrame([{"a": "b"}, {"a": "d"}])
        #
        # uri = s3.save_df_to_s3(df=df)
        # uri = "s3://aws-glue-temporary-921939243643-ap-south-1/Summary_Report.xlsx"
        uri = "s3://aws-glue-temporary-921939243643-ap-south-1/temp_1648712846664.csv"


        print(f"uri: {uri}")

        email = Email()
        print("Sending...")
        email.send_email_file(subject="test: email with s3 file", mail_body="this is test email.",
                              to_emails=['kuldeep.singh@zeno.health'], file_uris=[], file_paths=['/Users/kuldeep/Downloads/Summary_Report.xlsx'])
        print("Done.")
        # s3.delete_s3_obj(uri=uri)

    except Exception as e:
        raise e
    finally:
        # Closing the DB Connection
        rs_db.close_connection()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env

    print(f"env: {env}")

    """ calling the main function """
    main()
