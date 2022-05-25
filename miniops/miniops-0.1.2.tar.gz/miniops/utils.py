import logging
import os

import psutil


def log_memory_usage():
    process = psutil.Process(os.getpid())
    logging.debug(f"Memory load {process.memory_info().rss/1000000} MB")


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=os.environ.get(key="LOG_LEVEL", default="WARNING").upper(),
    )
