import os
from os.path import exists
import sys
import datetime
from datetime import date, timedelta
import logging

import azure.functions as func


from shared_code.inoc_automator import automate, generate_report
from shared_code.createtable import create_table

logging.basicConfig(
    filename="inoc_automator.log",
    format="%(asctime)s %(message)s",
    filemode="w",
    level=logging.INFO,
)

logger = logging.getLogger()


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    yesterday = date.today() - timedelta(1)

    driver = automate()

    # creates a report based on tickets created on this date
    count = generate_report(driver, yesterday.strftime("%Y-%m-%d"), "created")
    for i in range(1, count):
        if exists("report{i}.csv"):
            os.remove("report{i}.csv")
    create_table()
    # creates a report based on tickets last edited on this date
    count = generate_report(driver, yesterday.strftime("%Y-%m-%d"), "last edited")
    for i in range(1, count):
        if exists("report{i}.csv"):
            os.remove("report{i}.csv")
    create_table()

    print(yesterday.strftime("%Y-%m-%d") + " Completed")
    logger.info(yesterday.strftime("%Y-%m-%d") + " Completed")
