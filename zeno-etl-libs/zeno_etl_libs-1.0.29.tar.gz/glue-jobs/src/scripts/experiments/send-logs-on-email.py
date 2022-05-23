import argparse
import os
import sys

sys.path.append('../../../..')
from zeno_etl_libs.logger import get_logger, send_logs_via_email

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-lem', '--log_email_to', default=None, type=str, required=False)
parser.add_argument('-jn', '--job_name', default=None, type=str, required=False)
args, unknown = parser.parse_known_args()
os.environ['env'] = args.env

logger = get_logger()
logger.debug(f"This is debug log.")
logger.info(f"This is info log.")
logger.warn(f"This is warning log")
logger.error(f"This is error log")

send_logs_via_email(job_name=args.job_name, email_to=args.log_email_to)
