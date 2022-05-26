import sys
import os
import boto3
import argparse

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-tb', '--table_name', default="", type=str, required=False)
parser.add_argument('-sc', '--schema', default="prod2-generico", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()
s3 = S3()


def migrate_data(db, table_name, schema=None):
    if schema:
        table_location = f'''"{schema}"."{table_name}"'''
    else:
        """ temp tables have session specific schema which has no name """
        table_location = table_name
    query = f"""
            UNLOAD ('select * from {table_location}')    
            to 's3://aws-glue-temporary-921939243643-ap-south-1/redshift-migration/{table_name}/file_'
            iam_role 'arn:aws:iam::921939243643:role/etl-iam-redshift-unload-role'
            parallel off;
            """
    db.execute(query=query)
    logger.info("data unloaded successfully")


if __name__ == '__main__':
    table_name = args.table_name
    schema = args.schema
    migrate_data(rs_db, table_name, schema)
