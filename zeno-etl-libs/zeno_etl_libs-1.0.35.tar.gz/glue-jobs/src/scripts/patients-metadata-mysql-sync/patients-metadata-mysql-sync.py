import argparse
import sys
import os
import pandas as pd
import time

from zeno_etl_libs.db.db import MySQL, DB

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")

args, unknown = parser.parse_known_args()
env = args.env

os.environ['env'] = env

logger = get_logger()

logger.info(f"env: {env}")

""" opening the postgres connection """
rs_db = DB()
rs_db.open_connection()

""" opening the MySQL connection """
ms_db = MySQL(read_only=False)
ms_db.open_connection()

""" opening the MySQL write(many) connection """
ms_db_write = MySQL(read_only=False)
ms_db_write.open_connection()

ms_schema = "test-generico" if env in ("dev", "stage") else "prod2-generico"

""" Query to get patients-metadata from RS """
query = f"""
    SELECT
        id as "patient-id",
        date("first-bill-date") as "first-bill-date",
        date("last-bill-date") as "last-bill-date",
        "number-of-bills",
        "total-spend",
        "average-bill-value"
    FROM
        "prod2-generico"."patients-metadata-2"
    order by id desc
"""

patients_meta_rs = rs_db.get_df(query=query)
patients_meta_rs.columns = [c.replace('-', '_') for c in patients_meta_rs.columns]

""" date columns converted to string """
for i in ['first_bill_date', 'last_bill_date']:
    patients_meta_rs[i] = pd.to_datetime(patients_meta_rs[i], errors='coerce').dt.strftime("%Y-%m-%d")

logger.info(f"patients_meta_rs sample data: \n{str(patients_meta_rs[0:2])}")

"""checking the latest last_bill_date """
try:
    bill_date_max_pg = pd.to_datetime(patients_meta_rs['last_bill_date']).max().strftime('%Y-%m-%d')
except ValueError:
    bill_date_max_pg = '0000-00-00'

logger.info("patients_meta_rs, latest last_bill_date: {}".format(bill_date_max_pg))
logger.info("patients_meta_rs, total count {}".format(len(patients_meta_rs)))

""" Query to get patients-metadata from MySQL """
query = f"""
    SELECT
        `patient-id`,
        `first-bill-date`,
        `last-bill-date`,
        `number-of-bills`,
        `total-spend`,
        `average-bill-value`
    FROM
        `{ms_schema}`.`patients-metadata`
"""

patients_meta_ms = pd.read_sql_query(query, ms_db.connection)
patients_meta_ms.columns = [c.replace('-', '_') for c in patients_meta_ms.columns]

""" date columns converted to string """
for i in ['first_bill_date', 'last_bill_date']:
    patients_meta_ms[i] = pd.to_datetime(patients_meta_ms[i], errors='coerce').dt.strftime("%Y-%m-%d")

try:
    bill_date_max_ms = pd.to_datetime(patients_meta_ms['last_bill_date']).max().strftime('%Y-%m-%d')
except ValueError:
    bill_date_max_ms = '0000-00-00'

logger.info("patients_meta_ms, latest last_bill_date: {}".format(bill_date_max_ms))
logger.info("patients_meta_ms, total count: {}".format(len(patients_meta_ms)))

""" merge the Redshift and MySQL data """
patients_meta_union = patients_meta_rs.merge(
    patients_meta_ms[['patient_id', 'first_bill_date', 'last_bill_date', 'number_of_bills']],
    how='outer',
    on=['patient_id', 'first_bill_date', 'last_bill_date', 'number_of_bills'],
    indicator=True
)

metadata_cols = ['patient_id', 'first_bill_date', 'last_bill_date', 'number_of_bills',
                 'total_spend', 'average_bill_value']

""" 
New data in redshift has two parts
1. Insert - Completely new customers
2. Update - Old customers with data change
"""
patients_meta_new = patients_meta_union[patients_meta_union['_merge'] == 'left_only']
patients_meta_new = patients_meta_new[metadata_cols]

logger.info("patients_meta_new (difference), total count: {}".format(len(patients_meta_new)))

ms_patient_ids = patients_meta_ms['patient_id'].to_list()  # mysql patients ids

# To be inserted
patients_meta_new_insert = patients_meta_new.query("patient_id not in @ms_patient_ids")
patients_meta_new_insert.columns = [c.replace('_', '-') for c in patients_meta_new_insert.columns]

""" Don't upload patients ids which are not in patients table, Can be Removed later """
query = f"""
    SELECT
        `id` AS `patient-id`
    FROM 
        `{ms_schema}`.`patients` 
"""
patients = pd.read_sql_query(query, ms_db.connection)

patients_meta_new_insert_clean = patients_meta_new_insert.merge(patients, how='inner', on=['patient-id'])
logger.info("Absent in patients table count: {}".format(
    len(patients_meta_new_insert) - len(patients_meta_new_insert_clean)))
logger.info("patients_meta_new_insert_clean (to be inserted) count: {}".format(len(patients_meta_new_insert_clean)))
logger.info("Ignored if patient is absent in patient table")

if len(patients_meta_new_insert_clean):
    logger.info("Start of insert, patients_meta_new_insert...")
    patients_meta_new_insert_clean.to_sql(
        name='patients-metadata', con=ms_db_write.engine,
        if_exists='append', index=False,
        method='multi', chunksize=500)
    logger.info("End of insert, patients_meta_new_insert...")

""" Delay to allow the replication in RDS DB replica (for Inserts)"""
time.sleep(5)

"""Verifying the inserted data"""
query = f"""
    SELECT
        `patient-id`
    FROM
        `{ms_schema}`.`patients-metadata`
    WHERE 
        `patient-id` in ('%s')
""" % ("','".join([str(i) for i in patients_meta_new_insert_clean['patient-id'].to_list()]))

inserted_in_mysql = pd.read_sql_query(query, ms_db_write.connection)
logger.info("Total successfully inserted patients metadata count: {}".format(len(inserted_in_mysql)))

expected_insert_count = len(patients_meta_new_insert_clean)
actual_insert_count = len(inserted_in_mysql)
is_insert_successful = False
if expected_insert_count == actual_insert_count:
    logger.info(f"[INFO] Insert was successful.")
    is_insert_successful = True
else:
    logger.info(f"[ERROR] Insert was incomplete, count expected: {expected_insert_count}, "
                f"actual: {actual_insert_count}")

""" To be updated """
patients_meta_new_update = patients_meta_new.query("patient_id in @ms_patient_ids")
patients_meta_new_update.columns = [c.replace('_', '-') for c in patients_meta_new_update.columns]
logger.info("patients_meta_new_update count: {}".format(len(patients_meta_new_update)))

patients_meta_new_update_dicts = list(patients_meta_new_update.apply(dict, axis=1))

""" Query to bulk update """
query = f"""
    UPDATE
        `{ms_schema}`.`patients-metadata`
    SET
        `first-bill-date` = %s,
        `last-bill-date` = %s,
        `number-of-bills` = %s,
        `total-spend` = %s,
        `average-bill-value` = %s
    WHERE 
        `patient-id` = %s
"""
logger.info("Start of update, patients_meta_new_update...")

batch_size = 1000
cur = ms_db_write.connection.cursor()
for start_index in range(0, len(patients_meta_new_update_dicts), batch_size):
    logger.info(
        f"Updating from start index: {start_index}, to: "
        f"{min((start_index + batch_size), len(patients_meta_new_update_dicts))}")

    values = patients_meta_new_update_dicts[start_index: start_index + batch_size]
    values_list = []
    for i in values:
        values_list.append(
            (i['first-bill-date'],
             i['last-bill-date'],
             i['number-of-bills'],
             i['total-spend'],
             i['average-bill-value'],
             i['patient-id'])
        )

    """ Updating multiple patients at time """
    try:
        cur.executemany(query, values_list)
    except ms_db_write.connection.Error as e:
        try:
            logger.info("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
        except IndexError:
            logger.info("MySQL Error: %s" % str(e))
        ms_db_write.connection.rollback()

    ms_db_write.connection.commit()
cur.close()

logger.info("End of update, patients_meta_new_update...")

""" Delay to allow the replication in RDS DB replica """
time.sleep(5)

"""Verifying the updated data"""
query = f"""
    SELECT
        `patient-id`,
        `first-bill-date`,
        `last-bill-date`,
        `number-of-bills`,
        `total-spend`,
        `average-bill-value`
    FROM 
        `{ms_schema}`.`patients-metadata`
    where 
        date(`updated-at`) >= CURRENT_DATE()
"""
""" Alert: We are intentionally reading it from write database because we want real time numbers for validation """
updated_in_mysql = pd.read_sql_query(query, ms_db_write.connection)

for i in ['first-bill-date', 'last-bill-date']:
    updated_in_mysql[i] = pd.to_datetime(updated_in_mysql[i], errors='coerce').dt.strftime("%Y-%m-%d")

# Inner join with existing data
updated_in_mysql_matched = updated_in_mysql.merge(
    patients_meta_new_update[["patient-id", "first-bill-date", "last-bill-date", "number-of-bills"]],
    how='inner',
    on=["patient-id", "first-bill-date", "last-bill-date", "number-of-bills"])

logger.info("Total successfully updated patients metadata count: {}".format(len(updated_in_mysql_matched)))

expected_update_count = len(patients_meta_new_update)
actual_update_count = len(updated_in_mysql_matched)

is_update_successful = False
if expected_update_count == actual_update_count:
    logger.info(f"[INFO] Update was successful.")
    is_update_successful = True
else:
    logger.info(f"[ERROR] Update was incomplete, count expected: {expected_update_count}, "
                f"actual: {actual_update_count}")

if not is_update_successful:
    raise Exception("Update in the metadata table failed.")

if not is_insert_successful:
    raise Exception("Insert in the metadata table failed.")

""" closing the database connections """
rs_db.close_connection()
ms_db.close()
ms_db_write.close()
logger.info("Closed all DB connections successfully.")

"""Closing the logger"""
logger.close()
