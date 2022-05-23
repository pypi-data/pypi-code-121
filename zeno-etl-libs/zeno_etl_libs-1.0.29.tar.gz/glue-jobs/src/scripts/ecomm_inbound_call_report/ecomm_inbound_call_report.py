# inbound missed and complete calls
# author: neha k
import argparse
import json
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB, MongoDB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
import pandas as pd
import datetime
from datetime import datetime as dt
from datetime import timedelta
from dateutil.tz import gettz
import dateutil


def main(rs_db, mg_client, s3, data):
    schema = 'prod2-generico'
    table_name = 'ecomm-inbound-call-report'
    date_field = 'created-at'
    table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)
    # job_data_params = {"end": "2021-12-31", "start": "2021-12-01", "full_run": 1, "alternate_range": 0}
    # params
    job_data_params = data
    if job_data_params['full_run']:
        start = '2017-05-13'
    elif job_data_params['alternate_range']:
        start = job_data_params['start']
    else:
        start = str(dt.today().date() - timedelta(days=1))
    # convert date to pymongo format
    start = dateutil.parser.parse(start)

    # Read Generico crm table
    db = mg_client['generico-crm']
    collection = db["exotelReportLogs"].find({
        "exotelNumber": {"$regex": '2071171644'},
        "direction": "inbound",
        "$or": [{"toName": {"$regex": '2071171644'}}, {"toName": 'ZenoCRM1 Incoming'}],
        "status": {
            "$in": [
                "missed-call",
                "completed"
            ]
        }
    })
    callog_inbound = pd.DataFrame(list(collection))
    callog_inbound = callog_inbound[
        ['_id', 'exotelId', 'exotelNumber', 'from', 'FromName', 'to', 'toName', 'status', 'createdAt']]
    dict = {'_id': 'id',
            'exotelId': 'exotel-id',
            'exotelNumber': 'exotel-number',
            'FromName': 'from-name',
            'toName': 'to-name',
            'startTime': 'start-time',
            'endTime': 'end-time',
            'createdAt': 'created-at'}
    callog_inbound.rename(columns=dict, inplace=True)
    callog_inbound['etl-created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    callog_inbound['etl-updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    callog_inbound['created-by'] = 'etl-automation'
    callog_inbound['updated-by'] = 'etl-automation'
    if isinstance(table_info, type(None)):
        logger.info(f"table: {table_name} do not exist")
    else:
        truncate_query = f''' DELETE FROM "{schema}"."{table_name}" where "{date_field}">'{start}' '''
        logger.info(truncate_query)
        rs_db.execute(truncate_query)
        """ seek the data """
    logger.info(callog_inbound.head(1))
    logger.info(table_info)
    file_s3_uri_save = s3.save_df_to_s3(df=callog_inbound[table_info['column_name']], file_name="callog_inbound.csv")
    s3.write_to_db_from_s3_csv(table_name=table_name,
                               file_s3_uri=file_s3_uri_save,
                               db=rs_db, schema=schema)
    s3.write_df_to_db(df=callog_inbound[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-d', '--data', default=None, type=str, required=False)
    args, unknown = parser.parse_known_args()
    env = args.env
    data = args.data
    os.environ['env'] = env
    logger = get_logger()
    logger.info(f"data: {data}")
    data = json.loads(data) if data else {}
    logger.info(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()
    mg_db = MongoDB()
    mg_client = mg_db.open_connection("generico-crm")

    s3 = S3()

    """ calling the main function """
    main(rs_db=rs_db, mg_client=mg_client, s3=s3, data=data)

    # Closing the DB Connection
    rs_db.close_connection()
