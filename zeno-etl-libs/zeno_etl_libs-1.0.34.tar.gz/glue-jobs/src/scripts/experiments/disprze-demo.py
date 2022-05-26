import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.disprz.disprz import Dizprz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()

disprz = Dizprz()

logger.info(f"info message: {1}")
df = disprz.get_disprz_dataframe()
logger.info(f"df: {df}")
