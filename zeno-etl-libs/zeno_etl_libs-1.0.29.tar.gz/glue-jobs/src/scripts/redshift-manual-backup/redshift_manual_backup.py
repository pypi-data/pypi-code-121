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
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()

logger.info(f"env: {env}")

client = boto3.client('redshift')

time_now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

if env in ("dev", "stage"):
    cluster_identifier = "stag-mysql-redshift-cluster-1"
    snapshot_identifier = f"stag-{time_now}"
    manual_snapshot_retention_period = 1
elif env == "prod":
    cluster_identifier = "prod-mysql-redshift-cluster-1"
    snapshot_identifier = f"prod-{time_now}"
    manual_snapshot_retention_period = 365
else:
    raise Exception(f"Please provide the ENV, first.")

logger.info(f"started: cluster_identifier: {cluster_identifier}, snapshot_identifier: {snapshot_identifier}")
"""
resource to read:
1. https://n2ws.com/blog/aws-automation/3-reasons-to-automate-your-manual-redshift-snapshots
2. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Client.create_cluster_snapshot
3. https://aws.amazon.com/redshift/pricing/
"""
response = client.create_cluster_snapshot(
    SnapshotIdentifier=snapshot_identifier,
    ClusterIdentifier=cluster_identifier,
    ManualSnapshotRetentionPeriod=manual_snapshot_retention_period,
    Tags=[
        {
            'Key': 'backup_type',
            'Value': 'monthly'
        },
    ]
)
logger.info(f"ended: cluster_identifier: {cluster_identifier}, snapshot_identifier: {snapshot_identifier}")
