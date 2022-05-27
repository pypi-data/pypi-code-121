"""
Script for updating and keeping standard drug info.
fields included:
['qty_sold_l2y', 'revenue_l2y', 'num_bills_l2y', 'std_qty', 'purchase_interval',
'avg_ptr', 'avg_selling_rate']
author: vivek.revi@zeno.health
"""

import os
import sys

import pandas as pd
import datetime as dt
import numpy as np
import statistics as stats
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

import argparse


def main(debug_mode, rs_db, read_schema, write_schema, table_name, s3, logger):

    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'
    try:
        # get drug-patient data from mos
        logger.info("Getting historical data from sales table, bill_flag='gross'")
        q_mos_drugs = f"""
                select "drug-id" , "bill-id" , "patient-id" , quantity , 
                "revenue-value" as sales, date("created-at") as bill_date
                from "{read_schema}".sales s 
                where "bill-flag" = 'gross'
                and DATEDIFF(day, date("created-at"), current_date) < 730
                and "store-id" not in (243)
                """
        df_mos_drugs = rs_db.get_df(q_mos_drugs)
        df_mos_drugs.columns = [c.replace('-', '_') for c in df_mos_drugs.columns]

        df_mos_drugs["bill_date"] = pd.to_datetime(df_mos_drugs["bill_date"])
        df_drugs = df_mos_drugs.drop(["bill_id", "patient_id", "quantity", "sales",
                                      "bill_date"], axis=1).drop_duplicates()
        dd_qty_sales = df_mos_drugs.groupby("drug_id", as_index=False).agg(
            {"quantity": "sum", "sales": "sum"})

        ################################
        # get purchase interval of drugs
        ################################

        logger.info("Calculating patient-drug-interval")
        df_mos_drugs["bill_date1"] = df_mos_drugs["bill_date"]
        grp_pts_drug = df_mos_drugs.groupby(["patient_id", "drug_id"],
                                            as_index=False).agg(
            {"bill_date": "count", "bill_date1": "max"})
        grp_pts_drug.rename(
            {"bill_date": "bill_counts", "bill_date1": "latest_date"}, axis=1,
            inplace=True)

        # only drugs with atleast 4 bills taken
        grp_pts_drug = grp_pts_drug.loc[grp_pts_drug["bill_counts"] > 3]
        df_mos_drugs = df_mos_drugs.drop("bill_date1", axis=1)

        # only latest 10 patient considered for  purchase interval calculation
        grp_drugs = grp_pts_drug.groupby(["drug_id"], as_index=False).agg(
            {'patient_id': latest_20})
        pts_drugs_to_consider = grp_drugs.explode('patient_id')
        pts_drugs_to_consider = pts_drugs_to_consider.merge(df_mos_drugs,
                                                            on=["patient_id",
                                                                "drug_id"],
                                                            how="left")

        interval_pts_drug = pts_drugs_to_consider.groupby(["patient_id", "drug_id"],
                                                          as_index=False).agg(
            {"bill_date": pts_drug_interval})
        interval_pts_drug.rename({"bill_date": "purchase_interval"}, axis=1,
                                 inplace=True)
        drug_intv = interval_pts_drug.groupby("drug_id", as_index=False).agg(
            {"purchase_interval": median})

        # handling edge cases
        drug_intv["purchase_interval"] = np.where(
            drug_intv["purchase_interval"] == 0, 180,
            drug_intv["purchase_interval"])
        drug_intv["purchase_interval"] = np.where(
            drug_intv["purchase_interval"] > 180, 180,
            drug_intv["purchase_interval"])
        logger.info("patient-drug-interval calculation finished")

        df_drugs = df_drugs.merge(dd_qty_sales, on="drug_id", how="left")
        df_drugs.rename({"quantity": "qty_sold_l2y", "sales": "revenue_l2y"},
                        axis=1, inplace=True)
        df_drugs = df_drugs.merge(drug_intv, on="drug_id", how="left")
        df_drugs["purchase_interval"] = df_drugs["purchase_interval"].fillna(180)

        dd = df_mos_drugs.groupby("drug_id", as_index=False).agg(
            {"bill_id": count_unique})
        df_drugs = df_drugs.merge(dd, on="drug_id", how="left")
        df_drugs.rename({"bill_id": "num_bills_l2y"}, axis=1, inplace=True)

        dd = df_mos_drugs.groupby("drug_id", as_index=False).agg({"quantity": mode})
        df_drugs = df_drugs.merge(dd, on="drug_id", how="left")
        df_drugs.rename({"quantity": "mode"}, axis=1, inplace=True)

        dd = df_mos_drugs.groupby("drug_id", as_index=False).agg(
            {"quantity": median})
        df_drugs = df_drugs.merge(dd, on="drug_id", how="left")
        df_drugs.rename({"quantity": "median"}, axis=1, inplace=True)

        df_drugs["std_qty"] = np.where(df_drugs["mode"] > df_drugs["median"],
                                       df_drugs["median"], df_drugs["mode"])
        df_drugs["std_qty"] = np.where(df_drugs["num_bills_l2y"] <= 10, 1,
                                       df_drugs["std_qty"])
        df_drugs["std_qty"] = np.where(df_drugs["std_qty"] > 30, 1,
                                       df_drugs["std_qty"])
        df_drugs["std_qty"] = df_drugs["std_qty"].astype(int)
        df_drugs["avg_selling_rate"] = df_drugs["revenue_l2y"] / df_drugs[
            "qty_sold_l2y"]

        ################################
        # get std_qty and other info
        ################################

        logger.info("Calculating other fields")
        # get PTR info for all drugs
        q_inv = f"""
                SELECT "drug-id" as drug_id , AVG(ptr) as avg_ptr
                from "{read_schema}"."inventory-1" i 
                where DATEDIFF(day, date("created-at"), current_date) < 730
                group by "drug-id"
                """
        df_inv = rs_db.get_df(q_inv)

        df_drugs = df_drugs.merge(df_inv, on="drug_id", how="left")

        # get necessary drug info from drugs master
        q_drugs = f"""
                SELECT id as drug_id,  type
                from "{read_schema}".drugs d
                """
        df_drug_info = rs_db.get_df(q_drugs)

        df_drugs = df_drugs.merge(df_drug_info, on="drug_id", how="left")

        # default ptr value for generic=35 and rest=100
        df_drugs["avg_ptr"] = np.where(
            (df_drugs["avg_ptr"].isna()) & (df_drugs["type"] == "generic"), 35,
            df_drugs["avg_ptr"])
        df_drugs["avg_ptr"] = np.where(
            (df_drugs["avg_ptr"].isna()) & (df_drugs["type"] != "generic"), 100,
            df_drugs["avg_ptr"])

        # required format for RS wrtie
        df_drugs = df_drugs[['drug_id', 'qty_sold_l2y','revenue_l2y',
                        'num_bills_l2y', 'std_qty', 'purchase_interval',
                        'avg_ptr', 'avg_selling_rate']]

        df_drugs.columns = [c.replace('_', '-') for c in df_drugs.columns]

        df_drugs['created-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        df_drugs['created-by'] = 'etl-automation'
        df_drugs['updated-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        df_drugs['updated-by'] = 'etl-automation'

        logger.info("All calculations complete")

        if debug_mode == 'N':
            logger.info(f"Truncating {table_name} in {write_schema}")
            truncate_query = f"""
                    truncate table "{write_schema}"."{table_name}"
                    """
            rs_db.execute(truncate_query)
            logger.info(f"Truncating {table_name} in {write_schema} successful")

            logger.info("Writing table to RS-DB")
            s3.write_df_to_db(df=df_drugs, table_name=table_name,
                              db=rs_db, schema=write_schema)
            logger.info("Writing table to RS-DB completed")

        else:
            logger.info("Writing to RS-DB skipped")

        status = 'Success'
        logger.info(f"Drug-Std-Info code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"Drug-Std-Info code execution status: {status}")

    return status


def pts_drug_interval(pd_arr):
    """Purchase interval between buying on patient-drug level
    considering median interval"""
    df = pd.DataFrame(pd_arr, columns=["bill_date"])
    df = df.sort_values(by='bill_date', ascending=True)
    df["delta"] = (df['bill_date']-df['bill_date'].shift())
    df = df.dropna()
    median_days = df["delta"].median().days
    return median_days


def latest_20(pd_arr):
    """To consider only latest 20 patients who bought drug in more than 4 qty
    objective: to reduce run time"""
    pts_list = list(pd_arr)[-20:]
    return pts_list


def count_unique(pd_arr):
    return len(pd_arr.unique())


def mode(pd_arr):
    return min(pd_arr.mode())


def median(pd_arr):
    return stats.median(pd_arr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-d', '--debug_mode', default="Y", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)
    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    debug_mode = args.debug_mode
    email_to = args.email_to

    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'
    table_name = 'drug-std-info'

    logger = get_logger()
    rs_db = DB()
    s3 = S3()

    # open RS connection
    rs_db.open_connection()

    """ calling the main function """
    status = main(debug_mode=debug_mode, rs_db=rs_db, read_schema=read_schema,
                  write_schema=write_schema, table_name=table_name, s3=s3,
                  logger=logger)

    # close RS connection
    rs_db.close_connection()

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    reset_date = dt.date.today().strftime("%Y-%m-%d")
    email.send_email_file(
        subject=f"Drug-STD-Info Update (SM-{env}) {reset_date}: {status}",
        mail_body=f"""
                Debug Mode: {debug_mode}
                Job Params: {args}
                """,
        to_emails=email_to)

    logger.info("Script ended")



