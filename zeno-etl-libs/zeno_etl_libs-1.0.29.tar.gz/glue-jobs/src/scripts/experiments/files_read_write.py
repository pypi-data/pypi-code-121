import argparse
import os
import sys

import pandas as pd

sys.path.append('../../../..')
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()
logger.info(f"ENV: {env}")
s3 = S3()

logger.info(f"Demo 1: write df to excel at local")

df1 = pd.DataFrame({"a": ["b"]})
df2 = pd.DataFrame({"x": ["y"]})
file_name = "test.xlsx"
file_path = s3.write_df_to_excel(data={"sheet1": df1, "sheet2": df2}, file_name=file_name)

logger.info(f"Demo 2: upload excel to S3 bucket")
uri = s3.upload_file_to_s3(file_name=file_name)
logger.info(f"uri: {uri}")

logger.info(f"Demo 3: download excel from S3 bucket")
file_path = s3.download_file_from_s3(file_name=file_name)
logger.info(f"local_file_full_path: {file_path}")

logger.info(f"Demo 4: download excel from S3 bucket")
file_path = s3.download_file_from_s3(file_name=file_name)
logger.info(f"local_file_full_path: {file_path}")

logger.info(f"Demo 5: write text to file")
text_file_name = "text_file.txt"
file_path = s3.write_text_to_file(text="Hello World!", file_name=text_file_name)
logger.info(f"local_file_full_path: {file_path}")

logger.info(f"Demo 6: Download text file from S3")
file_path = s3.download_file_from_s3(file_name=text_file_name)
logger.info(f"local_file_full_path: {file_path}")
