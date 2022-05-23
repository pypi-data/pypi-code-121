#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Purpose - script with crm campaigns (multiple), to calling-dashboard write, daily frequency
# Todo evaluate RS/MySQL read-write connections later
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger

from datetime import datetime
from datetime import timedelta
from dateutil.tz import gettz

import pandas as pd

# Import custom functions
from zeno_etl_libs.utils.consumer.crm_campaigns import CrmCampaigns

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.jangir@zeno.health", type=str, required=False)
parser.add_argument('-dw', '--db_write', default="yes", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
db_write = args.db_write

# env = 'stage'
# limit = 10
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

# Instantiate the CRM campaigns class
cc = CrmCampaigns()

'''
# Connections
rs_db = DB()
rs_db.open_connection()
'''

# Global variable
# Run date
# run_date = datetime.today().strftime('%Y-%m-%d')
# Timezone aware
run_date = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d")

# run_date = '2021-09-01'
logger.info("Running for {}".format(run_date))


# Custom campaigns start
# Read data
# Can come from SQL query or from .csv read from an s3 folder

def campaign_mandatory_steps(data_pass, run_date, last_n_days_bill_param=15,
                             last_n_days_call_param=30):
    # Mandatory steps
    # Remove Last 15 days billed already
    data_pass = cc.no_bill_in_last_n_days(data_pass, run_date, last_n_days_param=last_n_days_bill_param)

    # Should not have been called in last 30-days thru calling dashboard
    data_pass = cc.no_call_in_last_n_days(data_pass, run_date, last_n_days_param=last_n_days_call_param)

    # Read DND list
    data_pass = cc.remove_dnd(data_pass)

    return data_pass


def data_prep_pune_custom_campaign():
    # Pune custom campaign
    store_group_id_param = 3  # Pune

    trans_start_d_param = (pd.to_datetime(run_date) - timedelta(days=120)).strftime("%Y-%m-%d")
    trans_end_d_param = (pd.to_datetime(run_date) - timedelta(days=30)).strftime("%Y-%m-%d")

    abv_lower_cutoff_param = 200
    abv_upper_cutoff_param = 2000

    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    data_q = """
        select
                a."store-id",
                a."patient-id",
                date(b."last-bill-date") as "last-bill-date",
                b."average-bill-value"
            from
                (
                select
                    rm."store-id",
                    rm."patient-id"
                from
                    "retention-master" rm
                inner join "stores-master" sm
                    on rm."store-id" = sm."id"
                where
                    rm."is-repeatable" = True
                    and sm."store-group-id" = {0}
                    and date(rm."bill-date") between '{1}' and '{2}'
                group by
                    rm."store-id",
                    rm."patient-id") a
            inner join "patients-metadata-2" b
                on
                a."patient-id" = b."id"
            where
                date(b."last-bill-date") between '{1}' and '{2}'
                and b."average-bill-value" between {3} and {4}
            order by
                a."store-id" asc,
                b."average-bill-value" desc
    """.format(store_group_id_param, trans_start_d_param, trans_end_d_param,
               abv_lower_cutoff_param, abv_upper_cutoff_param)
    logger.info(data_q)

    cc.rs_db.execute(data_q, params=None)
    data: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data is None:
        data = pd.DataFrame(columns=['store_id', 'patient_id', 'last_bill_date', 'average_bill_value'])
    data.columns = [c.replace('-', '_') for c in data.columns]
    logger.info(len(data))

    data_base_c_grp = data.drop_duplicates(subset='patient_id')
    logger.info("Unique data length {}".format(len(data_base_c_grp)))

    return data_base_c_grp


def data_prep_refill_campaign():
    # For refill date filtering
    run_date_plus7 = (pd.to_datetime(run_date) + timedelta(days=7)).strftime("%Y-%m-%d")

    # For active patient filtering
    run_date_minus15 = (pd.to_datetime(run_date) - timedelta(days=15)).strftime("%Y-%m-%d")
    run_date_minus45 = (pd.to_datetime(run_date) - timedelta(days=45)).strftime("%Y-%m-%d")

    # For last calling date filtering
    run_date_minus30 = (pd.to_datetime(run_date) - timedelta(days=30)).strftime("%Y-%m-%d")

    logger.info(f"Run date is {run_date}")

    ##########################################
    # Reill data
    ##########################################
    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    refill_q = """
            SELECT
                a."patient-id",
                a."store-id",
                a."drug-id",
                b."category",
                a."refill-date"
            FROM
                "retention-refill" a
            LEFT JOIN "drugs" b
                on a."drug-id" = b."id"
            WHERE
                a."refill-date" between '{0}' and '{1}'
    """.format(run_date, run_date_plus7)
    logger.info(refill_q)

    cc.rs_db.execute(refill_q, params=None)
    data_base: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data_base is None:
        data_base = pd.DataFrame(columns=['patient_id', 'store_id', 'drug_id', 'refill_date'])
    data_base.columns = [c.replace('-', '_') for c in data_base.columns]
    logger.info(len(data_base))

    logger.info("Length of refill data base is {}".format(len(data_base)))

    # Chronic only - current logic
    data_base_c = data_base[data_base['category'] == 'chronic'].copy()

    logger.info("After Filtering chronic - Length of data base is "
                "{}".format(len(data_base_c)))

    ##########################################
    # Atleast 2 chronic drugs
    ##########################################
    data_base_c_grp = data_base_c.groupby(['store_id',
                                           'patient_id'])['drug_id'].count().reset_index()

    logger.info("After grouping - Length of data base is {}".format(len(data_base_c_grp)))

    data_base_c_grp = data_base_c_grp[data_base_c_grp['drug_id'] >= 2]

    logger.info("After atleast 2drugs criteria filter - "
                "Length of data base is {}".format(len(data_base_c_grp)))

    data_base_c_grp = data_base_c_grp[['store_id', 'patient_id']]
    data_base_c_grp = data_base_c_grp.drop_duplicates(subset='patient_id')

    logger.info("After dropping duplicates - Length of data base is "
                "{}".format(len(data_base_c_grp)))

    ##########################################
    # Active customers window (-45 to -15)
    ##########################################
    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    pm_q = """
            SELECT
                id as "patient-id",
                "average-bill-value"
            FROM
                "patients-metadata-2"
            WHERE
                date("last-bill-date") between '{0}' and '{1}'
    """.format(run_date_minus45, run_date_minus15)
    logger.info(pm_q)

    cc.rs_db.execute(pm_q, params=None)
    data_pm: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data_pm is None:
        data_pm = pd.DataFrame(columns=['patient_id', 'average_bill_value'])
    data_pm.columns = [c.replace('-', '_') for c in data_pm.columns]
    logger.info(len(data_pm))

    logger.info("Length of Active patients (-45 to -15) metadata - "
                "fetched is {}".format(len(data_pm)))

    # Merge with active customers
    data_base_c_grp = data_base_c_grp.merge(data_pm, how='inner', on='patient_id')

    logger.info("After merging with patients metadata - "
                "Length of data base is {}".format(len(data_base_c_grp)))

    ##########################################
    # ABV Filter
    ##########################################
    data_base_c_grp = data_base_c_grp[data_base_c_grp['average_bill_value'].between(250, 1500)]

    logger.info("Length of data base after ABV filtering - "
                "length is {}".format(len(data_base_c_grp)))

    return data_base_c_grp


def data_prep_premium_cum_hd_campaign():
    # Single data for 2 campaigns, separated only by HD vs non-HD
    # For active patient filtering
    run_date_minus15 = (pd.to_datetime(run_date) - timedelta(days=15)).strftime("%Y-%m-%d")
    run_date_minus91 = (pd.to_datetime(run_date) - timedelta(days=91)).strftime("%Y-%m-%d")
    run_date_minus180 = (pd.to_datetime(run_date) - timedelta(days=180)).strftime("%Y-%m-%d")

    # For last calling date filtering
    run_date_minus30 = (pd.to_datetime(run_date) - timedelta(days=30)).strftime("%Y-%m-%d")

    logger.info(f"Run date is {run_date}")

    #######################################
    # SQL Logic
    #######################################
    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    list_q = """
        select
            pm."id" as patient_id
        from
            "patients-metadata-2" pm
        inner join (
            select
                "patient-id"
            from
                "customer-value-segment"
            where
                "value-segment" in ('platinum', 'gold', 'silver')
            group by
                "patient-id"
                ) seg
                on
            pm."id" = seg."patient-id"
        where
            pm."is-repeatable" is True
            and (current_date - date(pm."last-bill-date")) between 91 and 180
            and pm."average-bill-value" >= 250
        group by
            pm."id"
    """
    logger.info(list_q)

    cc.rs_db.execute(list_q, params=None)
    data: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data is None:
        data = pd.DataFrame(columns=['patient_id'])
    data.columns = [c.replace('-', '_') for c in data.columns]
    logger.info(len(data))

    logger.info("Data fetched with length {}".format(len(data)))

    # Final list
    logger.info("Unique patients list length is {}".format(len(data)))

    ##########################################
    # Active customers window (-180 to -91)
    ##########################################
    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    pm_q = """
            SELECT
                id as "patient-id",
                "average-bill-value"
            FROM
                "patients-metadata-2"
            WHERE
                date("last-bill-date") between '{0}' and '{1}'
    """.format(run_date_minus180, run_date_minus91)
    logger.info(pm_q)

    cc.rs_db.execute(pm_q, params=None)
    data_pm: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data_pm is None:
        data_pm = pd.DataFrame(columns=['patient_id', 'average_bill_value'])
    data_pm.columns = [c.replace('-', '_') for c in data_pm.columns]
    logger.info(len(data_pm))

    logger.info("Length of Active patients (-180 to -91) metadata - "
                "fetched is {}".format(len(data_pm)))

    # Merge with active customers
    data_base_c_grp = data.merge(data_pm, how='inner', on='patient_id')

    logger.info("After merging with patients metadata - "
                "Length of data base is {}".format(len(data_base_c_grp)))

    ##########################################
    # Latest store-id
    ##########################################
    data_store = cc.patient_latest_store(data_base_c_grp)

    ########################################
    # Merge
    ########################################
    data_base_c_grp = data_base_c_grp.merge(data_store, how='inner', on='patient_id')
    logger.info("After merging with store-id data - "
                "Length of data base is {}".format(len(data_base_c_grp)))

    ##########################################
    # Non-HD vs HD filtering
    ##########################################
    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    hd_q = """
            SELECT
                "patient-id"
            FROM
                "retention-master" a
            WHERE
                date("bill-date") between '{0}' and '{1}'
                and "hd-flag" is True
            GROUP BY
                "patient-id"
    """.format(run_date_minus180, run_date_minus91)
    logger.info(hd_q)

    cc.rs_db.execute(hd_q, params=None)
    data_hd: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data_hd is None:
        data_hd = pd.DataFrame(columns=['patient_id'])
    data_hd.columns = [c.replace('-', '_') for c in data_hd.columns]
    logger.info(len(data_hd))

    data_hd['hd_flag'] = 1
    logger.info("Length of HD active 180-91 is - {}".format(len(data_hd)))

    # Merge with premium set
    data_base_c_grp = data_base_c_grp.merge(data_hd, how='left', on='patient_id')
    data_base_c_grp['hd_flag'] = data_base_c_grp['hd_flag'].fillna(0)

    logger.info("After merging with hd-data, length is {}".format(len(data_base_c_grp)))
    logger.info("HD filtered data length is {}".format(data_base_c_grp['hd_flag'].sum()))

    return data_base_c_grp


def data_prep_pilot_store_margin():
    # Pilot Project extra discount
    store_ids_mulund = [2, 4, 230, 244, 264]  # Mulund Cluster
    store_ids_thane = [89, 126, 122, 139, 144, 145, 233, 304]  # Thane Cluster
    store_ids = store_ids_mulund + store_ids_thane

    lost_customer_cutoff_1 = 30
    lost_customer_cutoff_2 = 120

    read_schema = 'prod2-generico'
    cc.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

    data_q = f"""
            select
                T1."store-id",
                T1."patient-id",
                T1."last-bill-date",
                T1."average-bill-value"
            from
                (
                select
                    "previous-store-id" as "store-id",
                    id as "patient-id",
                    date("last-bill-date") as "last-bill-date",
                    "average-bill-value",
                    rank() over (partition by "previous-store-id"
                order by
                    "average-bill-value" desc) as "rank"
                from
                    "patients-metadata-2" pm
                where
                    "previous-store-id" in {tuple(store_ids)}
                    and datediff('days',
                    "last-bill-date",
                    current_date) >= {lost_customer_cutoff_1}
                    and datediff('days',
                    "last-bill-date",
                    current_date) <= {lost_customer_cutoff_2}) T1
            where
                T1."rank" <= 100;
            """
    logger.info(data_q)

    cc.rs_db.execute(data_q, params=None)
    data: pd.DataFrame = cc.rs_db.cursor.fetch_dataframe()
    if data is None:
        data = pd.DataFrame(columns=['store_id', 'patient_id', 'last_bill_date', 'average_bill_value'])
    data.columns = [c.replace('-', '_') for c in data.columns]
    logger.info(len(data))

    data_base_c_grp = data.drop_duplicates(subset='patient_id')
    logger.info("Unique data length {}".format(len(data_base_c_grp)))

    return data_base_c_grp


#########################################################################
# Main execution starts:
#########################################################################

################################################
# Pune custom campaign
################################################
logger.info("Pune custom campaign starts")

data = data_prep_pune_custom_campaign()
# Mandatory steps
data = campaign_mandatory_steps(data, run_date, last_n_days_bill_param=15,
                                last_n_days_call_param=30)
# DB Write
if db_write == 'yes':
    cc.db_write(data, run_date, 32, 'Inactive customer', store_daily_limit_param=5,
                default_sort_needed=True)

################################################
# Thane & Mulund cluster margin hit pilot
################################################
logger.info("Thane and Mulund cluster discount pilot")

data = data_prep_pilot_store_margin()
# Mandatory steps
data = campaign_mandatory_steps(data, run_date, last_n_days_bill_param=15,
                                last_n_days_call_param=30)

# Split Thane and Mulund data
data_mulund = data[data['store_id'].isin([2, 4, 230, 244, 264])].copy()
# DB Write
if db_write == 'yes':
    cc.db_write(data_mulund, run_date, 39, '20% discount pilot on Mulund Cluster', store_daily_limit_param=10,
                default_sort_needed=True)

data_thane = data[data['store_id'].isin([89, 126, 122, 139, 144, 145, 233, 304])].copy()
# DB Write
if db_write == 'yes':
    cc.db_write(data_thane, run_date, 39, '18% discount pilot on Thane cluster', store_daily_limit_param=10,
                default_sort_needed=True)

################################################
# Refill campaign
################################################
logger.info("Refill campaign starts")

data = data_prep_refill_campaign()
# Mandatory steps
data = campaign_mandatory_steps(data, run_date, last_n_days_bill_param=15,
                                last_n_days_call_param=30)
# DB Write
if db_write == 'yes':
    cc.db_write(data, run_date, 21, 'Medicine Refill estimated', store_daily_limit_param=5,
                default_sort_needed=True)

################################################
# Premium non-HD and HD campaign
################################################
logger.info("Premium non-hd and hd campaign starts")

data = data_prep_premium_cum_hd_campaign()
# Mandatory steps
data = campaign_mandatory_steps(data, run_date, last_n_days_bill_param=15,
                                last_n_days_call_param=30)

# Split non-hd and hd data
data_nonhd = data[data['hd_flag'] != 1].copy()
# DB Write
if db_write == 'yes':
    cc.db_write(data_nonhd, run_date, 26, 'Lost customer', store_daily_limit_param=10,
                default_sort_needed=True)

data_hd = data[data['hd_flag'] == 1].copy()
# DB Write
if db_write == 'yes':
    cc.db_write(data_hd, run_date, 28, 'Lost customer', store_daily_limit_param=5,
                default_sort_needed=True)

#################################################
# Closing the DB Connections
cc.close_connections()

logger.info("File ends")
