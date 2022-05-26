import argparse
import datetime
import sys
import os
import boto3

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-ss', 'source_schema_name', default='prod2-generico', type=str, required=True)
parser.add_argument('-ts', 'target_schema_name', default='public', type=str, required=True)
parser.add_argument('-sd', 'snapshot_date', default=None, type=str, required=True)
parser.add_argument('-lt', 'list_of_tables', default=None, type=str, required=True)

args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
source_schema_name = args.source_schema_name
target_schema_name = args.target_schema_name
snapshot_date = args.snapshot_date
list_of_tables = args.list_of_tables
logger = get_logger()

logger.info(f"env: {env}")

if env == 'prod':
    SourceDatabaseName = 'prod2-generico'
else:
    SourceDatabaseName = 'dev'

client = boto3.client('redshift')

for i in list_of_tables:
    response = client.restore_table_from_cluster_snapshot(
        ClusterIdentifier=f'{env}-mysql-redshift-cluster-1',
        SnapshotIdentifier=f'rs:{env}-mysql-redshift-cluster-1-{snapshot_date}-*',
        SourceDatabaseName=SourceDatabaseName,
        SourceSchemaName=source_schema_name,
        SourceTableName=i,
        TargetDatabaseName=SourceDatabaseName,
        TargetSchemaName=target_schema_name,
        NewTableName=i + '-' + snapshot_date,
        EnableCaseSensitiveIdentifier=False
    )
    if response['TableRestoreStatus']['Status'] == 'IN_PROGRESS':

