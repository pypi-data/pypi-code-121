import logging
import os
import sys
from dotenv import load_dotenv

if not load_dotenv(override=False):
    print('Could not find any .env file. The module will depend on system env only')

from zsftp.config import Config

logger = logging.getLogger(os.getenv('APP_NAME', __name__))

logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

if not logger.hasHandlers():
    formatter = logging.Formatter('%(asctime)s-%(module)s-%(lineno)s::%(levelname)s:: %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    ch.setFormatter(formatter)
    logger.addHandler(ch)

