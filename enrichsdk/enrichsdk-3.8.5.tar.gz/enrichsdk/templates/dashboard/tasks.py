import os
import sys
import gzip
import csv
import io
import re
import time
from celery import shared_task
from datetime import datetime, timedelta
from dateutil import relativedelta
from celery.utils.log import get_task_logger

from django.db import connections

logger = get_task_logger(__name__)


@shared_task(name="complex_task")
def complex_task(params):
    """
    Run some complicated and long running transaction
    """

    try:
        records = [{"name": "John", "location": "South Africa"}]

        logger.info(f"Received {len(records) -1} records")
    except:
        logger.exception("Error while executing the query")
        raise

    return {"records": records}
