import os

from os.path import exists
import logging
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv

from .connectDB import connect


logging.basicConfig(
    filename="inoc_automator.log",
    format="%(asctime)s %(message)s",
    filemode="w",
    level=logging.INFO,
)

logger = logging.getLogger()

load_dotenv()


conn = connect()
mycursor = conn.cursor()


def create_table():
    if exists("mainreport.csv"):
        try:
            if conn.is_connected():
                cursor = conn.cursor()
                sql = (
                    "CREATE TABLE IF NOT EXISTS `inoc`.`ticket_details` "
                    + "(`ticket_number` INT NOT NULL,`ticket_type` VARCHAR(255) NULL, "
                    + "`priority` VARCHAR(255) NULL,`status` VARCHAR(255) NULL, "
                    + "`title` VARCHAR(255) NULL,`submitted_by` VARCHAR(255) NULL,"
                    + "`assignees` VARCHAR(255) NULL,`last_edit_date` DATETIME NULL,"
                    + "`date_submitted` DATETIME NULL,`date_closed` DATETIME NULL,"
                    + "`description` BLOB NULL,`history` BLOB NULL,"
                    + "`ticket_category` VARCHAR(255) NULL,`date_of_alarm` DATETIME NULL,"
                    + "`time_of_alarm` TIME NULL,`product` VARCHAR(255) NULL,"
                    + "`device_id` VARCHAR(255) NULL,`device_name` VARCHAR(255) NULL,"
                    + "`device_type` VARCHAR(255) NULL,`client_internal` VARCHAR(255) NULL, "
                    + "`client_priority` VARCHAR(255) NULL,"
                    + "`client_ticket_number` VARCHAR(255) NOT NULL,`comments` BLOB NULL, "
                    + "`company` VARCHAR(255) NULL,PRIMARY KEY (`ticket_number`))ENGINE = InnoDB;"
                )
                cursor.execute(sql)
                logger.info("importing...")
                print("importing...")

                df = pd.read_csv("mainreport.csv", encoding="unicode_escape")
                df = df.replace("(no data)", "")

                df["Last Edit Date"] = pd.to_datetime(df["Last Edit Date"])
                df["Last Edit Date"] = df["Last Edit Date"].dt.strftime("%y-%m-%d")

                df["Date Submitted"] = pd.to_datetime(df["Date Submitted"])
                df["Date Submitted"] = df["Date Submitted"].dt.strftime("%y-%m-%d")

                df["Date Closed"] = pd.to_datetime(df["Date Closed"])
                df["Date Closed"] = df["Date Closed"].dt.strftime("%y-%m-%d")

                df["Date of Alarm"] = pd.to_datetime(df["Date of Alarm"])
                df["Date of Alarm"] = df["Date of Alarm"].dt.strftime("%y-%m-%d")

                df.fillna("", inplace=True)
                for i, row in df.iterrows():
                    if row["Date of Alarm"] == "":
                        row["Date of Alarm"] = None
                    if row["Time of Alarm"] == "":
                        row["Time of Alarm"] = None
                    if row["Date Closed"] == "(no data)":
                        row["Date Closed"] = None
                    sql = (
                        "INSERT IGNORE INTO `inoc`.`ticket_details` "
                        + "(ticket_number, ticket_type, priority, status,"
                        + "title, submitted_by, assignees, last_edit_date,"
                        + "date_submitted, date_closed, description, history, "
                        + "ticket_category, date_of_alarm, time_of_alarm, "
                        + "product, device_id, device_name, device_type, "
                        + "client_internal, client_priority, "
                        + "client_ticket_number, comments, company) VALUES"
                        + " (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    )
                    cursor.execute(sql, tuple(row))
                    logger.info("Record inserted")
                    print("Record inserted")

                    conn.commit()

        except Error as e:
            logger.error(f"Error while connecting to MySQL {e}")
            print("Error while connecting to MySQL", e)
