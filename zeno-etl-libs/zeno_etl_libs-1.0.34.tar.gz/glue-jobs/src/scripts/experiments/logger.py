import argparse
import os
import sys
import time

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger


def main(logger):
    for i in range(60):
        time.sleep(1)
        logger.info(f"info message: {i}")
        logger.error(f"error message: {i}")


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
