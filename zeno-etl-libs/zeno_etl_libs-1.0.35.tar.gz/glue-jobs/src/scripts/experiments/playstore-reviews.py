import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.google.playstore.playstore import Reviews

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()
logger.info(f"info message")

reviews = Reviews()
reviews_list = reviews.get()
for r in reviews_list:
    for c in r['comments']:
        print(f"User: {r['authorName']}, commented: {c['userComment']['text'].encode('utf-8')}")
