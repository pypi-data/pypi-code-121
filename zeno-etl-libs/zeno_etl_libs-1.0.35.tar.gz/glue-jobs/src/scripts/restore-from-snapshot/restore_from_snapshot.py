import argparse
import sys
import os
import boto3
import json
import time

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-ss', '--source_schema_name', default="prod2-generico", type=str, required=False)
parser.add_argument('-ts', '--target_schema_name', default="public", type=str, required=False)
parser.add_argument('-sd', '--snapshot_date', default=None, type=str, required=False)
parser.add_argument('-lt', '--list_of_tables', default=None, type=str, required=False)
parser.add_argument('-et', '--email_to', default="abhinav.srivastava@zeno.health", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
source_schema_name = args.source_schema_name
target_schema_name = args.target_schema_name
snapshot_date = args.snapshot_date
list_of_tables = args.list_of_tables
list_of_tables = json.loads(list_of_tables)
email_to = args.email_to
logger = get_logger()

logger.info(f"env: {env}")

if env == 'prod':
    SourceDatabaseName = 'prod2-generico'
else:
    SourceDatabaseName = 'prod2-generico'

client = boto3.client('redshift')
for i in list_of_tables["tables"]:
    response = client.restore_table_from_cluster_snapshot(
        # ClusterIdentifier=f'{env}-mysql-redshift-cluster-1',
        # SnapshotIdentifier=f'rs:{env}-mysql-redshift-cluster-1-{snapshot_date}-*',
        ClusterIdentifier='prod-mysql-redshift-cluster-1',
        SnapshotIdentifier='rs:prod-mysql-redshift-cluster-1-2022-05-25-00-30-10',
        SourceDatabaseName=SourceDatabaseName,
        SourceSchemaName=source_schema_name,
        SourceTableName=i,
        TargetDatabaseName=SourceDatabaseName,
        TargetSchemaName=target_schema_name,
        NewTableName=i + '-' + str(snapshot_date),
        EnableCaseSensitiveIdentifier=False
    )
    # if response['TableRestoreStatus']['Status'] == 'IN_PROGRESS':
    #     time.sleep(60)
    # elif response['TableRestoreStatus']['Status'] == 'SUCCEEDED':
    #     email = Email()
    #     email.send_email_file(subject="Snapshot restoration for table: {} completed".format(i + '-' + str(snapshot_date)),
    #                           mail_body='Snapshot restoration for table: {} completed'.format(i + '-' + str(snapshot_date)),
    #                           to_emails=email_to, file_uris=[], file_paths=[])

