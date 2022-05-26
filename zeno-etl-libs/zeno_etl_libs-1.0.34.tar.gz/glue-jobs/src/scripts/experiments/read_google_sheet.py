import argparse
import os
import sys

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet


def main(logger):
    gs = GoogleSheet()
    ma_stl_data = gs.download(data={
        "spreadsheet_id": "1CD_sae-3w4S9gOqUhxVYxcGTmS8bUR2rPHDK5T_yFTk",
        "sheet_name": "Step Up MA STL",
        "listedFields": []
    })

    df = pd.DataFrame(ma_stl_data)
    logger.info(f"df: {df}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stage, prod)")

    parser.add_argument('-d', '--data', default=None, type=str, required=False, help="batch size")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env

    _logger = get_logger()
    main(_logger)
