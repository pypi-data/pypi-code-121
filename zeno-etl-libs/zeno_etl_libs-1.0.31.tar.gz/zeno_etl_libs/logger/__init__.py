import json
import logging
import sys

import requests

from zeno_etl_libs.config.common import Config


def get_logger(level='DEBUG'):
    """
    returns: logger
    """
    configobj = Config.get_instance()
    secrets = configobj.get_secrets()
    level = secrets.get('LOGGER_LEVEL') or level
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def send_logs_via_email(job_name: str, email_to: list):
    configobj = Config.get_instance()
    secrets = configobj.get_secrets()
    url = f"{secrets['FLASK_DS_APP_BASE_URL']}/aws/glue/job/logs"
    payload = json.dumps({
        "job_name": job_name,
        "email_to": email_to
    })
    headers = {
        'x-api-key': secrets['FLASK_DS_APP_X_API_KEY'],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response
