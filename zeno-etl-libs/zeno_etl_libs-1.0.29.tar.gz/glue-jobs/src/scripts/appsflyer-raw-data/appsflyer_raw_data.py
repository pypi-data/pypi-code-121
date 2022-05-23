import os
import sys

sys.path.append('../../../..')

import argparse
import datetime as dt
import io
import pandas as pd
import requests

from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.aws.s3 import S3

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger


class AppFlyerReportDataSync:
    def __init__(self, report_type, rs_db, s3, created_date=None):
        self.appsflyer_uri = "https://hq.appsflyer.com/export"
        self.api_token = '70b710e8-59d1-4121-9aae-f520e4d0cebf'
        self.report_data_df = pd.DataFrame()  # starting with empty frame
        self.report_type = report_type
        self.ignore_columns = ["google-play-referrer"]

        self.rs_db = rs_db
        self.table_name = "appsflyer-" + report_type.replace("_", "-")
        self.s3 = s3
        self.schema = 'prod2-generico'
        yesterday = dt.datetime.now() + dt.timedelta(days=-1)

        """ default date filter is yesterday """
        created_date = created_date if created_date else yesterday
        created_date = created_date.strftime("%Y-%m-%d")
        self.created_date = created_date
        self.from_date = self.created_date
        self.to_date = self.created_date
        self.logger = get_logger()

    def get_app_data(self, report_type, app_id, maximum_rows=10000):
        params = {
            'api_token': self.api_token,
            'from': self.from_date,
            'to': self.to_date,
            'timezone': 'Asia/Kolkata',
            'maximum_rows': maximum_rows,
            'additional_fields': 'device_model,keyword_id,store_reinstall,deeplink_url,oaid,install_app_store,'
                                 'contributor1_match_type,contributor2_match_type,contributor3_match_type,match_type,'
                                 'device_category,gp_referrer,gp_click_time,gp_install_begin,amazon_aid,keyword_match_type,'
                                 'att,conversion_type,campaign_type,is_lat'
        }
        url = '{}/{}/{}/v5'.format(self.appsflyer_uri, app_id, report_type)
        payload = {}
        res = requests.request("GET", url, data=payload, params=params)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text))
            return df
        else:
            if res.status_code == 404:
                self.logger.info('There is a problem with the request URL. Make sure that it is correct')
            else:
                self.logger.info('There was a problem retrieving data: ', res.text)

    def get_report_data(self):
        app_ids = ['com.zenohealth.android', 'id1550245162']

        for app_id in app_ids:
            if isinstance(self.report_data_df, type(None)) or self.report_data_df.empty:
                self.report_data_df = self.get_app_data(report_type=self.report_type, app_id=app_id)
            else:
                self.report_data_df = self.report_data_df.append(
                    [self.get_app_data(report_type=self.report_type, app_id=app_id)])
            self.logger.info(f"Downloaded app data, report_type: {self.report_type}, app_id: {app_id}")

        self.report_data_df.columns = [i.lower().replace(" ", "-") for i in self.report_data_df.columns]

        """ dropping the unwanted columns """
        i_cols = []
        for i_col in self.ignore_columns:
            if i_col in self.report_data_df.columns:
                i_cols.append(i_col)

        if i_cols:
            self.report_data_df = self.report_data_df.drop(i_cols, axis=1)

        self.logger.info(f"Dropped unwanted columns: {i_cols}")
        self.report_data_df['created-date'] = self.created_date
        return self.report_data_df

    def check_table_exists(self):
        cursor = self.rs_db.cursor
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(self.table_name.replace('\'', '\'\'')))
        if cursor.fetchone()[0] == 1:
            # cursor.close()
            self.logger.info(f"Table, {self.table_name}, already exists: {True}")
            return True

        # cursor.close()
        self.logger.info(f"Table, {self.table_name}, already exists: {False}")
        return False

    def upload_data(self):
        """ get the report data """
        self.get_report_data()

        if self.report_data_df.empty:
            self.logger.info(f"No data found, report_type, {self.report_type}, created_date:{self.created_date}")
        else:
            """ create the report table if not exists """
            if self.check_table_exists() is False:
                # rs_db_engine.create_report_table_using_df(df=self.report_data_df, table_name=self.table_name,
                #                                           schema=self.schema)
                raise Exception(f""" create the table first: {self.table_name} """)
            else:
                query = f"""
                delete from "{self.schema}"."{self.table_name}" where "created-date" = '{self.created_date}';
                """
                self.rs_db.execute(query)

            table_info = helper.get_table_info(db=self.rs_db, table_name=self.table_name, schema=self.schema)

            """correcting the column order"""
            self.report_data_df = self.report_data_df[table_info['column_name']]

            self.s3.write_df_to_db(df=self.report_data_df, table_name=self.table_name, db=self.rs_db,
                                   schema=self.schema)

            self.logger.info(f"Data upload successful, report_type: {self.report_type}")


def main(rs_db, s3, from_date=None, to_date=None, reports=None):
    """
    function syns app flyer data to Redshift database for one day at a time
    """
    logger = get_logger()
    yesterday = dt.datetime.now() + dt.timedelta(days=-1)

    from_date = dt.datetime.strptime(from_date, '%Y-%m-%d') if from_date else yesterday
    to_date = dt.datetime.strptime(to_date, '%Y-%m-%d') if to_date else yesterday

    logger.info(f"from_date: {from_date}, to_date: {to_date}")

    if to_date < from_date:
        raise Exception(f"Wrong, from_date: {from_date} and to_date: {to_date} provided")

    created_date = from_date

    while from_date <= created_date <= to_date:
        report_types = reports.split(",") if reports else ['installs_report']
        for report_type in report_types:
            logger.info(f"starting report_type: {report_type}, for created_date: {created_date}")
            af = AppFlyerReportDataSync(report_type=report_type, rs_db=rs_db, s3=s3, created_date=created_date)
            af.upload_data()

        """ next day """
        created_date = created_date + dt.timedelta(days=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-fd', '--from_date', default=None, type=str, required=False)
    parser.add_argument('-td', '--to_date', default=None, type=str, required=False)
    parser.add_argument('-r', '--reports', default=None, type=str, required=False)

    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    logger = get_logger()

    from_date = args.from_date
    to_date = args.to_date
    reports = args.reports
    logger.info(f"env: {env} reports: {reports}")

    rs_db = DB()
    rs_db.open_connection()

    s3 = S3()

    """ calling the main function """
    main(rs_db, s3, from_date, to_date, reports)

    # Closing the DB Connection
    rs_db.close_connection()
