import logging
import os
import sys

log_format = logging.Formatter(
    '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

app_name = os.getenv('APP_NAME', 'MISSING_APP_NAME_ENV_VAR')
logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(log_format)
logger.addHandler(consoleHandler)
