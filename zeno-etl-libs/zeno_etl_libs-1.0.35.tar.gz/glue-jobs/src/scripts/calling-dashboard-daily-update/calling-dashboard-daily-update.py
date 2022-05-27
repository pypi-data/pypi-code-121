#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Purpose - script with calling-dashboard and related tables, daily update
# Todo evaluate RS/MySQL read-write connections later
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

from datetime import datetime
from datetime import timedelta
from dateutil.tz import gettz

import time

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

# pip install mutagen
import urllib
from mutagen.mp3 import MP3

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.jangir@zeno.health", type=str, required=False)
parser.add_argument('-l', '--limit', default=None, type=int, required=False)
parser.add_argument('-dw', '--db_write', default="yes", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
limit = args.limit
db_write = args.db_write

# env = 'stage'
# limit = 10
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

# Connections
rs_db = DB()
rs_db.open_connection()
rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

# ALERT: read_only=False, if you want connection which writes
# this is mysql_write
ms_connection = MySQL(read_only=False)
ms_connection.open_connection()

s3 = S3()

# Global variable
# Run date
# run_date = datetime.today().strftime('%Y-%m-%d')
# Timezone aware
run_date = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d")

# run_date = '2021-09-01'
logger.info("Running for {}".format(run_date))


####################################
# DND list update
####################################
def dnd_list_update():
    #########################################
    # Connections start
    #########################################
    read_schema = 'prod2-generico'
    rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    ##########################################
    # DND customers
    ##########################################
    calling_q = """
                SELECT
                    a.`patient-id`,
                    b.`comment-id`,
                    b.`comment`,
                    c.`call-status`
                FROM
                    `calling-dashboard` a
                INNER JOIN
                    `calling-history` b
                on a.`id` = b.`calling-dashboard-id`
                LEFT JOIN
                    `call-statuses` c
                ON b.`comment-id` = c.`id`
                WHERE b.`comment-id` in (79)
                GROUP BY
                    a.`patient-id`, b.`comment-id`, b.`comment`, c.`call-status`
        """
    calling_q = calling_q.replace('`', '"')
    logger.info(calling_q)

    data_c = rs_db.get_df(query=calling_q)
    data_c.columns = [c.replace('-', '_') for c in data_c.columns]

    logger.info("Length of DND list fetched is {}".format(len(data_c)))

    logger.info("Unique".format(data_c.nunique()))

    logger.info("Unique comment-id is {}".format(data_c['comment_id'].unique()))
    logger.info("Unique comment is {}".format(data_c['comment'].unique()))
    logger.info("Unique call-status is {}".format(data_c['call_status'].unique()))

    # Final list
    data = data_c[['patient_id']].drop_duplicates()
    data['call_dnd'] = 1
    data['reason'] = 'Calling dashboard - Do not disturb'

    logger.info("DND list length is {}".format(len(data)))

    logger.info("Export columns are {}".format(data.columns))

    # Remove those that are already part
    read_schema = 'prod2-generico'
    rs_db_write.execute(f"set search_path to '{read_schema}'", params=None)
    dnd_q = """
                SELECT
                    "patient-id"
                FROM
                    "dnd-list"
                WHERE
                    "patient-id" is not null
                GROUP BY
                    "patient-id"
        """
    dnd_q = dnd_q.replace('`', '"')
    logger.info(dnd_q)

    data_dss = rs_db_write.get_df(query=dnd_q)
    data_dss.columns = [c.replace('-', '_') for c in data_dss.columns]

    # Already dnd
    already_dnd = data_dss['patient_id'].dropna().drop_duplicates().to_list()

    data_export = data[~data['patient_id'].isin(already_dnd)]

    logger.info("Data export length - after removing already in list, is {}".format(len(data_export)))

    # Dummy column values
    data_export['phone'] = "-1"
    data_export['sms_dnd'] = 0
    # Timestamp
    data_export['created_at'] = pd.to_datetime(datetime.now())

    # Created-by
    data_export['created_by'] = 'etl-automation'

    ##########################################
    # DANGER ZONE
    ##########################################
    logger.info("Insert started for length {}".format(len(data_export)))

    write_schema = 'prod2-generico'
    write_table_name = 'dnd-list'
    table_info = helper.get_table_info(db=rs_db, table_name=write_table_name, schema=write_schema)

    table_info_clean = table_info[~table_info['column_name'].isin(['id', 'updated-at'])]

    data_export.columns = [c.replace('_', '-') for c in data_export.columns]

    s3.write_df_to_db(df=data_export[table_info_clean['column_name']], table_name=write_table_name,
                      db=rs_db_write, schema=write_schema)

    logger.info("Insert done")


def calling_history_metadata():
    ######################################################
    # Check existing
    ######################################################

    # Check data already in DSS
    read_schema = 'prod2-generico'
    rs_db_write.execute(f"set search_path to '{read_schema}'", params=None)

    call_ds_q = """
        SELECT
            "calling-history-id"
        FROM 
            "calling-history-metadata"
    """
    call_ds_q = call_ds_q.replace('`', '"')
    logger.info(call_ds_q)

    last_dss = rs_db_write.get_df(query=call_ds_q)
    last_dss.columns = [c.replace('-', '_') for c in last_dss.columns]

    already_present = tuple(last_dss['calling_history_id'].to_list())

    logger.info("Interaction id's present in DSS are : "
                "{}".format(len(already_present)))

    ########################################
    # Check recording lengths to be inserted
    ########################################
    read_schema = 'prod2-generico'
    rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    limit_str = f" limit {limit} ; " if limit else ""
    calling_h_q = f"""
        SELECT
            id AS `calling-history-id`,
            `call-recording-url`
        FROM 
            `calling-history`
        WHERE 
            `call-recording-url` != ''
        {limit_str}
    """

    calling_h_q = calling_h_q.replace('`', '"')
    # logger.info(calling_h_q)

    data = rs_db.get_df(query=calling_h_q)
    data.columns = [c.replace('-', '_') for c in data.columns]

    logger.info("Interaction history present in mySQL : {}".format(len(data)))

    # Removing already present in dss
    data = data[~data['calling_history_id'].isin(already_present)]

    logger.info("New interaction history present in mySQL : {}".format(len(data)))

    # If testing
    # data = data.sample(n=10)

    ########################
    # Calculation
    ########################

    def get_length(url):
        try:
            download_data = urllib.request.urlopen(url)
            local_file_path = s3.download_file_from_s3(file_name='sample.mp3')
            f = open(local_file_path, 'wb')
            f.write(download_data.read())
            f.close()
            audio = MP3(local_file_path)
            return audio.info.length
        except:
            return 0

    data['call_duration'] = data.apply(lambda row: get_length(row['call_recording_url']),
                                       axis=1)

    data_insert_dss = data[['calling_history_id', 'call_duration']]

    #########################################################
    # INSERT
    ########################################################

    # Insert using to_sql
    data_insert_dss.columns = [c.replace('_', '-') for c in data_insert_dss.columns]
    logger.info("DSS - insert length is {}".format(len(data_insert_dss)))

    expected_data_length_insert = len(last_dss) + len(data_insert_dss)
    logger.info("DSS - Resulted data length after insert should be is "
                "{}".format(expected_data_length_insert))

    # DSS insert
    logger.info("DSS - Insert starting")

    write_schema = 'prod2-generico'
    write_table_name = 'calling-history-metadata'
    table_info = helper.get_table_info(db=rs_db_write, table_name=write_table_name, schema=write_schema)

    # table_info_clean = table_info[~table_info['column_name'].isin(['id', 'updated-at'])]

    data_export = data_insert_dss.copy()
    data_export.columns = [c.replace('_', '-') for c in data_export.columns]

    s3.write_df_to_db(df=data_export[table_info['column_name']], table_name=write_table_name,
                      db=rs_db_write, schema=write_schema)

    logger.info("DSS - Insert ended")


def calling_dashboard_info_update(run_date_param=None):
    ######################################################
    # Check Tickets
    ######################################################

    s = """
        SELECT
            a.*,
            b.`campaign-name`
        FROM
            `calling-dashboard` a
        LEFT JOIN `calling-dashboard-campaigns` b
            on a.`campaign-id` = b.id
    """
    tickets_data = pd.read_sql_query(s, ms_connection.connection)
    tickets_data.columns = [c.replace('-', '_') for c in tickets_data.columns]

    # Convert date values to date type
    tickets_data['list_date'] = pd.to_datetime(tickets_data['list_date'], errors='coerce')
    tickets_data['call_date'] = pd.to_datetime(tickets_data['call_date'], errors='coerce')

    logger.info("Tickets present in existing sheet : {}".format(len(tickets_data)))

    #########################################################
    # Check which tickets have call date earlier than today, but still in open or reopen status
    ########################################################
    # fetch run_date from parameters
    # if not, take current date as run date
    if run_date_param is not None:
        run_date = run_date_param
    else:
        run_date = datetime.today().strftime('%Y-%m-%d')

    logger.info("Running for {}".format(run_date))

    # Check open tickets
    open_tickets = tickets_data[tickets_data['status'].isin(['open', 'reopen'])]

    logger.info("Total open tickets are {}".format(len(open_tickets)))

    # Check backlog tickets
    backlog_tickets = open_tickets[open_tickets['list_date'] < run_date]

    logger.info("Total backlog open tickets are {}".format(len(backlog_tickets)))

    # Update call date and backlog count for backlog tickets
    backlog_update = backlog_tickets[['id', 'list_date', 'call_date', 'backlog_days_count']]

    backlog_update['call_date'] = run_date
    backlog_update['backlog_days_count'] = (
            pd.to_datetime(backlog_update['call_date']) - backlog_update['list_date']).dt.days

    backlog_update_mysql = backlog_update[['id', 'call_date', 'backlog_days_count']]

    # Out of this, how many do we actually need to update?

    s = """
        SELECT
            `id`,
            `call-date`,
            `backlog-days-count`
        FROM
            `calling-dashboard`
     """
    last_data_mysql = pd.read_sql_query(s, ms_connection.connection)
    last_data_mysql.columns = [c.replace('-', '_') for c in last_data_mysql.columns]

    # Join and check exactly which to update
    # Data match with mySQL
    common_cols = ['id', 'call_date', 'backlog_days_count']

    # To merge, keep both dtypes same
    backlog_update_mysql['call_date'] = pd.to_datetime(backlog_update_mysql['call_date']).dt.strftime("%Y-%m-%d")
    last_data_mysql['call_date'] = pd.to_datetime(last_data_mysql['call_date']).dt.strftime("%Y-%m-%d")

    data_update_mysql = backlog_update_mysql[common_cols].merge(
        last_data_mysql[common_cols], how='outer', on=common_cols, indicator=True)

    # To update
    data_update_mysql = data_update_mysql[data_update_mysql['_merge'] == 'left_only']

    data_update_mysql = data_update_mysql[['id', 'call_date', 'backlog_days_count']]
    data_update_mysql.columns = [c.replace('_', '-') for c in data_update_mysql.columns]

    logger.info("Update to be done for backlog tickets count is {}".format(len(data_update_mysql)))

    data_to_be_updated_list_mysql = list(data_update_mysql.apply(dict, axis=1))

    #################################
    # DANGER ZONE start
    #################################
    # mySQL write engine
    update_counter = 0
    for i in data_to_be_updated_list_mysql:
        update_q = """
            UPDATE
                `calling-dashboard`
            SET
                `call-date` = '{1}', 
                `backlog-days-count` = {2}
            WHERE
                `id` = {0}
        """.format(i['id'], i['call-date'], i['backlog-days-count'])

        # logger.info("Running update for ticket {}".format(i['id']))
        # logger.info("id:", i['id'], "call-date:", i['call-date'],
        # "backlog-days-count:", i['backlog-days-count'])
        if db_write == 'yes':
            ms_connection.engine.execute(update_q)
        # logger.info("Update for ticket {} is successful".format(i['id']))

        # Print success periodically
        update_counter = update_counter + 1
        if update_counter % 1000 == 0:
            logger.info("mySQL - Update done till row {}".format(update_counter))

    #################################
    # DANGER ZONE END
    #################################

    logger.info("mySQL - Update for calling-dashboard successful")

    # Verify updates
    s = """
        SELECT
            `id`,
            `call-date`,
            `backlog-days-count`
        FROM
            `calling-dashboard`
    """
    update_mysql_verify = pd.read_sql_query(s, ms_connection.connection)

    # To merge, keep both dtypes same
    update_mysql_verify['call-date'] = pd.to_datetime(update_mysql_verify['call-date']).dt.strftime("%Y-%m-%d")

    # Inner join with existing data
    update_mysql_check = update_mysql_verify.merge(data_update_mysql, how='inner',
                                                   on=['id', 'call-date', 'backlog-days-count'])

    logger.info("mySQL - Update done for data entries length is {}".format(len(update_mysql_check)))

    if len(update_mysql_check) != len(data_update_mysql):
        logger.info("Warning: Error, update didn't happen for all entries")

    ############################################
    # Create follow-up tickets
    #############################################

    # Check which tickets have requested follow-up

    s = """
        SELECT
            a.`calling-dashboard-id`,
            a.`follow-up-required`,
            a.`follow-up-at`,

            b.`original-reference-id`,
            b.`store-id`,
            b.`campaign-id`,
            b.`callback-reason`,
            b.`patient-id`,
            b.`follow-up-count`
        FROM
            `calling-history` a
        LEFT JOIN `calling-dashboard` b on 
            a.`calling-dashboard-id` = b.`id`
    """
    history_data = pd.read_sql_query(s, ms_connection.connection)
    history_data.columns = [c.replace('-', '_') for c in history_data.columns]

    # Convert follow up time to timestamp
    # Right now format is dd-mm-yy so putting dayfirst = True filter
    history_data['follow_up_at'] = pd.to_datetime(history_data['follow_up_at'], dayfirst=True, errors='coerce')

    # Keep date as string only
    history_data['follow_up_date'] = history_data['follow_up_at'].dt.strftime("%Y-%m-%d")
    logger.info("Follow up date converted to string")

    # Take only those who have requested follow-up
    # Check if flag is integer os string
    if is_numeric_dtype(history_data['follow_up_required']):
        follow_up_data = history_data[history_data['follow_up_required'] == 1]
        logger.info(
            "Follow up required (integer flag) is present in interactions - "
            "length is {}".format(len(follow_up_data)))
    else:
        follow_up_data = history_data[history_data['follow_up_required'] == '1']
        logger.info(
            "Follow up required (string flag) is present in interactions - "
            "length is {}".format(len(follow_up_data)))

    # Sort on follow up dates, max is first
    follow_up_data = follow_up_data.sort_values(by=['calling_dashboard_id', 'follow_up_at'], ascending=[True, False])

    # Choose only maximum follow-up time
    follow_up_data['rank'] = follow_up_data.groupby(['calling_dashboard_id']).cumcount() + 1
    follow_up_data_latest = follow_up_data[follow_up_data['rank'] == 1]

    logger.info("Follow up data (max date per ticket) length is {}".format(len(follow_up_data_latest)))

    # Keep only future follow-ups
    follow_up_data_latest_valid = follow_up_data_latest[
        follow_up_data_latest['follow_up_at'] >= pd.to_datetime(run_date)]

    logger.info("Valid (future) follow up date length is {}".format(len(follow_up_data_latest_valid)))

    # New ticket information
    new_ticket_data = follow_up_data_latest_valid.copy()
    # If reference id already exists, then copy it, else take ticket id
    new_ticket_data['new_ticket_reference_id'] = np.where(new_ticket_data['original_reference_id'] > 0,
                                                          new_ticket_data['original_reference_id'],
                                                          new_ticket_data['calling_dashboard_id'])

    # Drop other ticket id columns
    new_ticket_data.drop(['calling_dashboard_id', 'original_reference_id'], axis=1, inplace=True)

    # New original reference id
    new_ticket_data = new_ticket_data.rename(columns={
        'new_ticket_reference_id': 'original_reference_id'})

    # Keep only one new follow-up on unique original_reference_id
    new_ticket_data2 = new_ticket_data.copy()
    new_ticket_data2['follow_up_date'] = pd.to_datetime(new_ticket_data2['follow_up_date'])

    # Sort on follow up dates, max is first
    new_ticket_data2 = new_ticket_data2.sort_values(by=['original_reference_id', 'follow_up_date'],
                                                    ascending=[True, False])

    # Choose only maximum follow-up time
    new_ticket_data2['rank'] = new_ticket_data2.groupby(['original_reference_id']).cumcount() + 1

    # Only one for one ticket
    new_ticket_data3 = new_ticket_data2[new_ticket_data2['rank'] == 1]

    # Keep date as string only
    new_ticket_data3['follow_up_date'] = new_ticket_data3['follow_up_date'].dt.strftime("%Y-%m-%d")
    logger.info("Follow up date converted to string")

    # Since new ticket is generated, so add 1 to follow-up count
    new_ticket_data3['follow_up_count'] = new_ticket_data3['follow_up_count'] + 1

    # Ticket list date taken as follow up date
    new_ticket_data3['list_date'] = new_ticket_data3['follow_up_date']
    # Call date same as list date for now
    new_ticket_data3['call_date'] = new_ticket_data3['list_date']

    # Update data-type to follow up
    new_ticket_data3['data_type'] = 'follow up'

    logger.info("One follow up for one root ticket - upload to be done - length is {}".format(len(new_ticket_data3)))

    # INSERT DATA
    # Final columns
    upload_cols = ['store_id', 'original_reference_id', 'list_date', 'call_date', 'patient_id', 'campaign_id',
                   'data_type', 'callback_reason', 'follow_up_count']

    data_upload_mysql = new_ticket_data3[upload_cols]

    unique_check_cols = ['store_id', 'list_date', 'campaign_id', 'callback_reason', 'patient_id']

    # Assert uniqueness, for DB update
    unique_data = data_upload_mysql[unique_check_cols].drop_duplicates()

    if len(data_upload_mysql) != len(unique_data):
        logger.info("Warning, duplicate entries for date {}".format(run_date))

    # Check last data first
    # Check on store, list date, campaign id, subtype id, patient id
    # Don't check on data-type yet
    s = """
        SELECT
            `store-id`,
            `list-date`,
            `campaign-id`,
            `callback-reason`,
            `patient-id`
        FROM 
            `calling-dashboard`
    """
    last_data_mysql = pd.read_sql_query(s, ms_connection.connection)
    last_data_mysql.columns = [c.replace('-', '_') for c in last_data_mysql.columns]

    logger.info("Last data in mySQL length {}".format(len(last_data_mysql)))

    # Join and check which to insert and which to update

    # To merge, keep both dtypes same
    last_data_mysql['list_date'] = pd.to_datetime(last_data_mysql['list_date']).dt.strftime("%Y-%m-%d")

    # Data match with mySQL
    data_export_mysql = data_upload_mysql.merge(
        last_data_mysql, how='outer', on=unique_check_cols, indicator=True)

    # To upload
    data_upload_mysql2 = data_export_mysql[data_export_mysql['_merge'] == 'left_only']

    data_insert_mysql = data_upload_mysql2[upload_cols]

    # Priority can be default, can be updated later on

    # Don't do any update in DSS for now

    # Check last data
    s = """
        SELECT
            `id`
        FROM 
            `calling-dashboard`
    """
    last_data_mysql = pd.read_sql_query(s, ms_connection.connection)

    # Insert using to_sql
    data_insert_mysql.columns = [c.replace('_', '-') for c in data_insert_mysql.columns]
    logger.info("mySQL - insert to be done - length is {}".format(len(data_insert_mysql)))

    expected_data_length_insert = len(last_data_mysql) + len(data_insert_mysql)
    logger.info("mySQL - Resulted data length after insert should be is {}".format(expected_data_length_insert))

    # Upload to mySQL DB
    logger.info("mySQL - Insert starting")
    if db_write == 'yes':
        data_insert_mysql.to_sql(name='calling-dashboard', con=ms_connection.engine, if_exists='append', index=False,
                                 method='multi', chunksize=500)

    logger.info("mySQL - Insert ended")

    logger.info("Follow up data uploaded to mySQL for run date {} with length : "
                "{}".format(run_date, len(data_insert_mysql)))

    logger.info("Sleeping for 10 seconds")
    time.sleep(10)
    logger.info("Slept for 10 seconds")

    # Verify the inserted data
    s = """
        SELECT
            `id`
        FROM
            `calling-dashboard`
    """
    insert_mysql_verify = pd.read_sql_query(s, ms_connection.connection)

    logger.info("mySQL - After insert - calling dashboard length is : {}".format(len(insert_mysql_verify)))

    if len(insert_mysql_verify) != expected_data_length_insert:
        logger.info("Warning: Error, update didn't happen for all entries")


def calling_dashboard_feedback_loop(run_date_param=None, follow_up_limit_param=None,
                                    transaction_goal_campaigns_list_param=[]):
    ######################################################
    # Check Tickets
    ######################################################
    s = """
        SELECT
            a.*,
            b.`campaign-name`
        FROM
            `calling-dashboard` a
        LEFT JOIN `calling-dashboard-campaigns` b
            on a.`campaign-id` = b.id
    """
    tickets_data = pd.read_sql_query(s, ms_connection.connection)
    tickets_data.columns = [c.replace('-', '_') for c in tickets_data.columns]

    # Convert date values to date type
    tickets_data['list_date'] = pd.to_datetime(tickets_data['list_date'], errors='coerce')
    tickets_data['call_date'] = pd.to_datetime(tickets_data['call_date'], errors='coerce')

    logger.info("Tickets present in existing sheet : {}".format(len(tickets_data)))

    #########################################################
    # Check which tickets have list date earlier than today, and in closed state
    ########################################################
    # fetch run_date from parameters
    # if not, take current date as run date

    if run_date_param is not None:
        run_date = run_date_param
    else:
        run_date = datetime.today().strftime('%Y-%m-%d')

    logger.info("Running for {}".format(run_date))

    # Check closed tickets
    close_tickets = tickets_data[tickets_data['status'].isin(['closed'])]

    logger.info("Total closed tickets are {}".format(len(close_tickets)))

    # Check only maximum timestamp of non-null comments
    # First fetch calling-history

    # Tickets prior to run date, and of run date, if exist
    # Tickets till T-2 only, in order to avoid scheduling in advance

    run_date_minus2 = (pd.to_datetime(run_date) - timedelta(days=2)).strftime("%Y-%m-%d")

    close_tickets2 = close_tickets[close_tickets['list_date'] <= run_date_minus2]

    logger.info("Total closed tickets prior to run date minus2 is {}".format(len(close_tickets2)))

    tickets = tuple(close_tickets2['id'].to_list())
    logger.info("Tickets to find in calling-history are : {}".format(len(tickets)))

    ############################################
    # Create follow-up tickets - for Non-responders
    #############################################

    # Check which tickets actually require follow-up
    s = """
        SELECT
            a.`calling-dashboard-id`,
            a.`follow-up-required`,
            a.`comment`,
            a.`created-at`,
            b.`original-reference-id`,
            b.`store-id`,
            b.`campaign-id`,
            b.`callback-reason`,
            b.`patient-id`,
            b.`follow-up-count`
        FROM
            `calling-history` a
        LEFT JOIN `calling-dashboard` b
            on a.`calling-dashboard-id` = b.`id`
        WHERE
            b.`id` in {}
    """.format(tickets)
    history_data = pd.read_sql_query(s, ms_connection.connection)
    history_data.columns = [c.replace('-', '_') for c in history_data.columns]

    logger.info("History data - length is {0} and unique tickets length is "
                "{1}".format(len(history_data), history_data['calling_dashboard_id'].nunique()))

    # Change to datetime
    history_data['created_at'] = pd.to_datetime(history_data['created_at'])

    # ORIGINAL REFERENCE ID, if exists, then take it as reference
    # If reference id already exists, then copy it, else take ticket id
    history_data['org_calling_dashboard_id'] = np.where(history_data['original_reference_id'] > 0,
                                                        history_data['original_reference_id'],
                                                        history_data['calling_dashboard_id'])

    logger.info("Original reference id, if exists, has been taken up as original calling dashboard id,"
                "so now unique tickets are {0}".format(history_data['org_calling_dashboard_id'].nunique()))

    # Remove the tickets which already have at least a one follow-up required flag,
    # because they will already be counted

    already_follow_up_data = history_data[history_data['follow_up_required'] == 1][
        ['org_calling_dashboard_id']].drop_duplicates()
    logger.info("Already Follow up required tickets - length is {}".format(len(already_follow_up_data)))

    already_follow_up_data_t = already_follow_up_data['org_calling_dashboard_id'].to_list()

    history_data2 = history_data.query("org_calling_dashboard_id not in @already_follow_up_data_t")

    logger.info(
        "After removing redundant entries - History data - length is "
        "{0} and unique tickets length is {1}".format(
            len(history_data2),
            history_data2['org_calling_dashboard_id'].nunique()))

    non_response_cols = ['Ringing/Not answering',
                         'Call rejected/Busy',
                         'Not reachable/Switched off']

    # First see how many of them are also tagged in call-statuses master
    s = """
        SELECT
            id AS call_status_id,
            `call-status`
        FROM
            `call-statuses`
    """
    dropdown_master = pd.read_sql_query(s, ms_connection.connection)
    dropdown_master.columns = [c.replace('-', '_') for c in dropdown_master.columns]

    logger.info("Dropdown master currently has dropdowns - length {}".format(len(dropdown_master)))

    dropdown_match = dropdown_master.query("call_status in @non_response_cols")

    logger.info("Dropdown master match with non-response cols defined - "
                "length {}".format(len(dropdown_match)))

    # Latest non-null comment should be one-amongst the non-response columns

    follow_up_data_dropna = history_data2[~history_data2['comment'].isnull()]
    logger.info("Follow up data - non-null comment - length is "
                "{}".format(len(follow_up_data_dropna)))

    follow_up_data = follow_up_data_dropna[follow_up_data_dropna['comment'] != '']
    logger.info("Follow up data - non-empty string comment - length is "
                "{}".format(len(follow_up_data)))

    # Sort on interaction timestamp, max is first
    follow_up_data = follow_up_data.sort_values(by=['org_calling_dashboard_id', 'created_at'],
                                                ascending=[True, False])

    # Choose only maximum follow-up time
    follow_up_data['rank'] = follow_up_data.groupby(['org_calling_dashboard_id']).cumcount() + 1
    follow_up_data_latest = follow_up_data[follow_up_data['rank'] == 1]

    logger.info("Follow up data (latest interaction per ticket) length is "
                "{}".format(len(follow_up_data_latest)))

    # Latest interaction was non-response
    follow_up_data_latest_nr = follow_up_data_latest.query("comment in @non_response_cols")

    logger.info("Follow up data (latest interaction per ticket) Non-response length is {}".format(
        len(follow_up_data_latest_nr)))

    follow_up_data_latest_nr['interaction_date'] = follow_up_data_latest_nr['created_at'].dt.strftime("%Y-%m-%d")

    follow_up_data_latest_nr['day_diff_rundate'] = (pd.to_datetime(run_date) -
                                                    pd.to_datetime(
                                                        follow_up_data_latest_nr['interaction_date'])).dt.days

    # Add 2 days to latest interaction date, parametrize it later
    follow_up_data_latest_nr['latest_date_plus2'] = (pd.to_datetime(follow_up_data_latest_nr['interaction_date']) +
                                                     timedelta(days=2)).dt.strftime("%Y-%m-%d")

    # If follow-up is after >=2 days, keep rundate
    # If follow-up is for yesterdays' tickets, then add 2days
    follow_up_data_latest_nr['follow_up_date'] = np.where(follow_up_data_latest_nr['day_diff_rundate'] >= 2,
                                                          run_date,
                                                          follow_up_data_latest_nr['latest_date_plus2'])

    # Remove those who are already-followed-up 3times, parametrized
    if follow_up_limit_param is not None:
        follow_up_limit = follow_up_limit_param
    else:
        follow_up_limit = 1

    logger.info("Follow up limit is {}".format(follow_up_limit))

    follow_up_data_latest_nr_focus1 = follow_up_data_latest_nr[
        follow_up_data_latest_nr['follow_up_count'] < follow_up_limit]

    logger.info(
        "Follow up data after removing those already follow up equal to "
        "limit or more times - length is {}".format(
            len(follow_up_data_latest_nr_focus1)))

    # Remove those with >7 days, vintage, parametrize it later
    follow_up_data_latest_nr_focus2 = follow_up_data_latest_nr_focus1[
        follow_up_data_latest_nr_focus1['day_diff_rundate'] <= 7]

    logger.info("Follow up data after removing those with 7+days passed "
                "since last interaction - length is {}".format(
        len(follow_up_data_latest_nr_focus2)))

    # Transaction goal - campaigns - patamatrized
    if len(transaction_goal_campaigns_list_param) > 0:
        transaction_goal_campaigns_list = transaction_goal_campaigns_list_param
    else:
        transaction_goal_campaigns_list = tickets_data['campaign_id'].drop_duplicates().to_list()

    logger.info("Transaction goal campaigns are {}".format(transaction_goal_campaigns_list))

    # For, transaction goal campaigns, if transaction done in last 15 days, then no call
    # parametrize it later
    bill_days_cutoff = 15
    logger.info("Last bill date cutoff for transaction goal campaigns is "
                "{}".format(bill_days_cutoff))

    # Now join with patients-metadata
    s = """
        SELECT
            `patient-id`,
            max(date(`created-at`)) as `last-bill-date`
        FROM
            `bills-1`
        GROUP BY
            `patient-id`
    """
    patients_lbd = pd.read_sql_query(s, ms_connection.connection)
    patients_lbd.columns = [c.replace('-', '_') for c in patients_lbd.columns]

    # Merge
    follow_up_data_latest_nr_focus2 = follow_up_data_latest_nr_focus2.merge(patients_lbd, how='left', on=['patient_id'])

    # Check recency
    follow_up_data_latest_nr_focus2['day_diff_lbd_rundate'] = (pd.to_datetime(run_date) -
                                                               pd.to_datetime(
                                                                   follow_up_data_latest_nr_focus2['last_bill_date'],
                                                                   errors='coerce')).dt.days

    # If campaign is in transaction goal campaigns then filter, else as it is
    follow_up_data_latest_nr_focus2['exclude_goal_completed'] = np.where(
        ((follow_up_data_latest_nr_focus2['campaign_id'].isin(transaction_goal_campaigns_list)) &
         (follow_up_data_latest_nr_focus2['day_diff_lbd_rundate'] <= bill_days_cutoff)), 1, 0)

    to_be_removed = follow_up_data_latest_nr_focus2[follow_up_data_latest_nr_focus2['exclude_goal_completed'] == 1]

    logger.info("To be removed due to transaction goal completed - in relevant campaigns - "
                "length {}".format(len(to_be_removed)))

    follow_up_data_final = follow_up_data_latest_nr_focus2[
        follow_up_data_latest_nr_focus2['exclude_goal_completed'] == 0]

    logger.info("Final follow up data after removing transaction goal completed tickets - "
                "length {}".format(len(follow_up_data_final)))

    # New ticket information
    new_ticket_data = follow_up_data_final.copy()

    # If reference id already exists, then copy it, else take ticket id
    # org_calling_dashboard_id we have, which is combined

    # Drop other ticket id columns
    new_ticket_data.drop(['calling_dashboard_id', 'original_reference_id'], axis=1, inplace=True)

    # New original reference id
    new_ticket_data = new_ticket_data.rename(columns={
        'org_calling_dashboard_id': 'original_reference_id'})

    # Keep only one new follow-up on unique original_reference_id
    new_ticket_data2 = new_ticket_data.copy()
    new_ticket_data2['follow_up_date'] = pd.to_datetime(new_ticket_data2['follow_up_date'])

    # Sort on follow up dates, max is first
    new_ticket_data2 = new_ticket_data2.sort_values(by=['original_reference_id', 'follow_up_date'],
                                                    ascending=[True, False])

    # Choose only maximum follow-up time
    new_ticket_data2['rank'] = new_ticket_data2.groupby(['original_reference_id']).cumcount() + 1

    # Only one for one ticket
    new_ticket_data3 = new_ticket_data2[new_ticket_data2['rank'] == 1]

    logger.info("Max for one original ticket - length {}".format(len(new_ticket_data3)))

    # Remove those original reference id's which already have another ticket open

    # Check open tickets
    open_tickets = tickets_data[tickets_data['status'].isin(['open', 'reopen'])]

    open_tickets_ref_id = open_tickets['original_reference_id'].drop_duplicates().to_list()

    new_ticket_data3 = new_ticket_data3.query("original_reference_id not in @open_tickets_ref_id")

    logger.info("After removing those with already open tickets in root, - "
                "length {}".format(len(new_ticket_data3)))

    # Keep date as string only
    new_ticket_data3['follow_up_date'] = new_ticket_data3['follow_up_date'].dt.strftime("%Y-%m-%d")
    logger.info("Follow up date converted to string")

    # Since new ticket is generated, so add 1 to follow-up count
    new_ticket_data3['follow_up_count'] = new_ticket_data3['follow_up_count'] + 1

    # Ticket list date taken as follow up date
    new_ticket_data3['list_date'] = new_ticket_data3['follow_up_date']

    # If ticket date in negative then keep run-date
    new_ticket_data3['list_date'] = np.where(pd.to_datetime(new_ticket_data3['list_date']) < run_date, run_date,
                                             new_ticket_data3['list_date'])

    # Call date same as list date for now
    new_ticket_data3['call_date'] = new_ticket_data3['list_date']

    # Update data-type to follow up
    new_ticket_data3['data_type'] = 'follow up'

    logger.info("One follow up for one root ticket - upload to be done - "
                "length is {}".format(len(new_ticket_data3)))

    #################################################
    # Sanity check, if original reference id already has 2 follow ups in list
    #################################################
    reference_tickets = tuple(new_ticket_data3['original_reference_id'].dropna().drop_duplicates().to_list())

    logger.info("Reference ticket length is {}".format(len(reference_tickets)))

    s = """
            SELECT
                `original-reference-id`,
                count(`id`) as already_ticket_count
            FROM
                `calling-dashboard`
            WHERE
                `original-reference-id` in {}
            GROUP BY
                `original-reference-id`
    """.format(reference_tickets)

    followup_already = pd.read_sql_query(s, ms_connection.connection)
    followup_already.columns = [c.replace('-', '_') for c in followup_already.columns]

    # Already follow ups done, as per limit
    followup_already_limit = followup_already[followup_already['already_ticket_count'] >= follow_up_limit].copy()
    logger.info('Already follow up done as per limit, or more times length is {}'.format(len(followup_already_limit)))

    # Remove these from the list
    followup_already_two_list = followup_already_limit['original_reference_id'].to_list()

    new_ticket_data4 = new_ticket_data3.query("original_reference_id not in @followup_already_two_list")

    logger.info('After removing those with already follow up done 2 or more times length is '
                '{}'.format(len(new_ticket_data4)))

    # INSERT DATA
    # Final columns

    upload_cols = ['store_id', 'original_reference_id',
                   'list_date', 'call_date',
                   'patient_id', 'campaign_id',
                   'data_type', 'callback_reason',
                   'follow_up_count']

    data_upload_mysql = new_ticket_data4[upload_cols]

    unique_check_cols = ['store_id', 'list_date', 'campaign_id',
                         'callback_reason', 'patient_id']

    # Assert uniqueness, for DB update
    unique_data = data_upload_mysql[unique_check_cols].drop_duplicates()

    logger.info("Unique data should be - length is {}".format(len(unique_data)))

    if len(data_upload_mysql) != len(unique_data):
        logger.info("Warning, duplicate entries for date {}".format(run_date))
        data_upload_mysql = data_upload_mysql.drop_duplicates(subset=unique_check_cols)
        logger.info("Unique data after dropping duplicates - length is "
                    "{}".format(len(data_upload_mysql)))

    # Check last data first
    # Check on store, list date, campaign id, subtype id, patient id
    # Don't check on data-type yet

    s = """
        SELECT
            `store-id`,
            `list-date`,
            `campaign-id`,
            `callback-reason`,
            `patient-id`
        FROM
            `calling-dashboard`
        GROUP BY
            `store-id`,
            `list-date`,
            `campaign-id`,
            `callback-reason`,
            `patient-id`
    """
    last_data_mysql = pd.read_sql_query(s, ms_connection.connection)
    last_data_mysql.columns = [c.replace('-', '_') for c in last_data_mysql.columns]

    logger.info("Last data in mySQL length {}".format(len(last_data_mysql)))

    # Join and check which to insert and which to update

    # To merge, keep both dtypes same
    last_data_mysql['list_date'] = pd.to_datetime(last_data_mysql['list_date']
                                                  ).dt.strftime("%Y-%m-%d")

    # Data match with mySQL
    data_export_mysql = data_upload_mysql.merge(
        last_data_mysql, how='outer', on=unique_check_cols, indicator=True)

    # To upload
    data_upload_mysql2 = data_export_mysql[data_export_mysql['_merge'] == 'left_only'].copy()

    logger.info("After removing same day duplicate tickets - length is {}".format(len(data_upload_mysql2)))

    data_insert_mysql = data_upload_mysql2[upload_cols].copy()

    # Priority can be default, can be updated later on

    # Don't do any update in DSS for now

    # Check last data
    s = """
        SELECT
            `id`
        FROM
            `calling-dashboard`
    """
    last_data_mysql = pd.read_sql_query(s, ms_connection.connection)

    # Insert using to_sql
    data_insert_mysql.columns = [c.replace('_', '-') for c in data_insert_mysql.columns]
    logger.info("mySQL - insert to be done - length is {}".format(len(data_insert_mysql)))

    expected_data_length_insert = len(last_data_mysql) + len(data_insert_mysql)
    logger.info("mySQL - Resulted data length after insert should be is "
                "{}".format(expected_data_length_insert))

    # Upload to mySQL DB
    logger.info("mySQL - Insert starting")
    if db_write == 'yes':
        data_insert_mysql.to_sql(name='calling-dashboard', con=ms_connection.engine,
                                 if_exists='append', index=False,
                                 method='multi', chunksize=500)

    logger.info("mySQL - Insert ended")

    logger.info(
        "Follow up data uploaded to mySQL for run date {} with length : "
        "{}".format(run_date, len(data_insert_mysql)))

    logger.info("Sleeping for 10 seconds")
    time.sleep(10)
    logger.info("Slept for 10 seconds")

    # Verify the inserted data
    s = """
        SELECT
            `id`
        FROM
            `calling-dashboard`
     """
    insert_mysql_verify = pd.read_sql_query(s, ms_connection.connection)

    logger.info("mySQL - After insert - calling dashboard length is : "
                "{}".format(len(insert_mysql_verify)))

    if len(insert_mysql_verify) != expected_data_length_insert:
        logger.info("Warning: Error, update didn't happen for all entries")


def calling_dashboard_profile_status():
    ######################################################
    # Check existing tickets
    ######################################################
    s = """
        SELECT
            id AS calling_dashboard_id,
            `patient-id`,
            `campaign-id` AS mysql_campaign_id,
            `callback-reason`
        FROM
            `calling-dashboard`
        LIMIT 1000
    """
    tickets_info = pd.read_sql_query(s, ms_connection.connection)
    tickets_info.columns = [c.replace('-', '_') for c in tickets_info.columns]

    logger.info("Tickets present in existing sheet : {}".format(len(tickets_info)))

    # Check campaign in mySQL
    s = """
        SELECT
            id AS mysql_campaign_id,
            `is-active`,
            `patient-billing-status-display`
        FROM
            `calling-dashboard-campaigns`
    """
    mysql_campaigns = pd.read_sql_query(s, ms_connection.connection)
    mysql_campaigns.columns = [c.replace('-', '_') for c in mysql_campaigns.columns]

    logger.info("Campaigns present in mySQL are : {}".format(len(mysql_campaigns)))

    campaign_metadata = mysql_campaigns.copy()
    # To-do. Hard-coded. Evaluate later
    campaign_metadata['patient_bill_status_cutoff_d'] = 30
    # Now join with tickets data
    # Only keep relevant ones, by doing inner join with status enabled campaigns

    tickets_info2 = tickets_info.merge(campaign_metadata[['mysql_campaign_id',
                                                          'patient_billing_status_display',
                                                          'patient_bill_status_cutoff_d']],
                                       how='inner',
                                       on=['mysql_campaign_id'])

    # bill status missing value input if any
    bill_days_cutoff_default = 30
    tickets_info2['patient_bill_status_cutoff_d'] = tickets_info2['patient_bill_status_cutoff_d'].fillna(
        bill_days_cutoff_default)

    # Now join with patients-metadata
    # To-do change with RS ETL table patients-metadata-2
    s = """
        SELECT
            `patient-id`,
            max(date(`created-at`)) as `last-bill-date`
        FROM
            `bills-1`
        GROUP BY
            `patient-id`
    """
    patients_lbd = pd.read_sql_query(s, ms_connection.connection)
    patients_lbd.columns = [c.replace('-', '_') for c in patients_lbd.columns]

    # Merge
    tickets_info2 = tickets_info2.merge(patients_lbd, how='left', on=['patient_id'])

    # Check recency
    tickets_info2['day_diff'] = (pd.to_datetime(run_date)
                                 - pd.to_datetime(tickets_info2['last_bill_date'], errors='coerce')).dt.days

    # Check if days fall within the range
    # Only bill status enabled campaigns
    logger.info("DSS campaign metadata for status enabled - fetched")
    tickets_info2['profile_status'] = np.where(tickets_info2['patient_billing_status_display'] == 1,
                                               np.where(tickets_info2['day_diff'] <= tickets_info2[
                                                   'patient_bill_status_cutoff_d'],
                                                        'Active', 'Inactive'), 'NA')

    #########################################################
    # Profile status to update
    ########################################################

    upload_profile_data = tickets_info2[['calling_dashboard_id', 'profile_status']]

    logger.info("Upload profile data for these many tickets : "
                "{}".format(len(upload_profile_data)))

    # Check last data
    s = """
        SELECT
            `calling-dashboard-id`,
            `profile-status`
        FROM `patient-profile-status`
    """
    last_data_mysql = pd.read_sql_query(s, ms_connection.connection)
    last_data_mysql.columns = [c.replace('-', '_') for c in last_data_mysql.columns]

    # Join and check which to insert and which to update

    # Data match with mySQL
    data_export_mysql = upload_profile_data.merge(
        last_data_mysql, how='outer', on=['calling_dashboard_id', 'profile_status'], indicator=True)

    # To upload
    data_upload_mysql = data_export_mysql[data_export_mysql['_merge'] == 'left_only']

    data_upload_mysql = data_upload_mysql[['calling_dashboard_id', 'profile_status']]

    #########################################################
    # INSERT OR UPDATE
    ########################################################

    # Out of this, how many need insert and how many update?
    mysql_tickets = last_data_mysql['calling_dashboard_id'].to_list()

    # Insert
    data_insert_mysql = data_upload_mysql.query("calling_dashboard_id not in @mysql_tickets")

    # How many do we need to update
    data_update_mysql = data_upload_mysql.query("calling_dashboard_id in @mysql_tickets")

    # Insert using to_sql
    data_insert_mysql.columns = [c.replace('_', '-') for c in data_insert_mysql.columns]
    logger.info("mySQL - insert length is {}".format(len(data_insert_mysql)))

    expected_data_length_insert = len(last_data_mysql) + len(data_insert_mysql)
    logger.info("mySQL - Resulted data length after insert should be is "
                "{}".format(expected_data_length_insert))

    # MySQL insert
    logger.info("mySQL - Insert starting")
    if db_write == 'yes':
        data_insert_mysql.to_sql(name='patient-profile-status', con=ms_connection.engine,
                                 if_exists='append', index=False,
                                 method='multi', chunksize=500)

    logger.info("mySQL - Insert ended")

    logger.info("Sleeping for 10 seconds")
    time.sleep(10)
    logger.info("Slept for 10 seconds")

    # Verify the inserted data
    s = """
        SELECT
             `calling-dashboard-id`,
             `profile-status`
        FROM `patient-profile-status`
    """
    insert_mysql_verify = pd.read_sql_query(s, ms_connection.connection)

    logger.info("mySQL - After insert - patients profile status length is : "
                "{}".format(len(insert_mysql_verify)))

    if len(insert_mysql_verify) != expected_data_length_insert:
        logger.info("Warning: Error, update didn't happen for all entries")

    # Update existing entries
    # Have to do one by one

    data_update_mysql.columns = [c.replace('_', '-') for c in data_update_mysql.columns]

    logger.info("mySQL - Update to be done for data entries length is "
                "{}".format(len(data_update_mysql)))

    # Try SQL engine
    data_to_be_updated_list_mysql = list(data_update_mysql.apply(dict, axis=1))

    logger.info("mySQL - Update to be done for data entries - converted into list - "
                "length is {}".format(
        len(data_to_be_updated_list_mysql)))

    #################################
    # DANGER ZONE start
    #################################
    # mySQL write engine

    logger.info("mySQL - update for patients profile status started")

    update_counter = 0
    for i in data_to_be_updated_list_mysql:
        update_q = """
             UPDATE
                `patient-profile-status`
             SET
                `profile-status` = '{1}'
             WHERE
                `calling-dashboard-id` = {0}
        """.format(i['calling-dashboard-id'], i['profile-status'])
        if db_write == 'yes':
            ms_connection.engine.execute(update_q)

        # Print success periodically
        update_counter = update_counter + 1
        if update_counter % 1000 == 0:
            logger.info("mySQL - Update done till row {}".format(update_counter))

    #################################
    # DANGER ZONE END
    #################################

    logger.info("mySQL - update for patients profile status successful")

    # Verify
    s = """
         SELECT
             `calling-dashboard-id`,
             `profile-status`
        FROM
            `patient-profile-status`
    """
    update_mysql_verify = pd.read_sql_query(s, ms_connection.connection)

    # Inner join with existing data
    update_mysql_check = update_mysql_verify.merge(data_update_mysql,
                                                   how='inner',
                                                   on=["calling-dashboard-id", "profile-status"])

    logger.info("mySQL - Update done for data entries length is {}".format(len(update_mysql_check)))

    if len(update_mysql_check) != len(data_update_mysql):
        logger.info("Warning: Error, update didn't happen for all entries")


####################################################
# Main block
###################################################
# Run DND List update()
logger.info("Running DND list update")
dnd_list_update()

# Run Calling history metadata
logger.info("Running Calling history metadata update")
try:
    calling_history_metadata()
except:
    logger.info("Error in calling_history_metadata")

# Run calling dashboard info update
logger.info("Running Calling dashboard info update")
calling_dashboard_info_update()

# Run calling dashboard feedback loop
logger.info("Running Calling feedback loop update")
calling_dashboard_feedback_loop()

# Run calling dashboard profile status
logger.info("Running Calling profile status update")
calling_dashboard_profile_status()

#################################################
# Closing the DB Connections
rs_db.close_connection()
rs_db_write.close_connection()
ms_connection.close()

logger.info("File ends")
