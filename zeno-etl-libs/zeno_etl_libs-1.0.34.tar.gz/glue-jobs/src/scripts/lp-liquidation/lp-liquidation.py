import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger, send_logs_via_email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta


def seek(rs_db, limit=None):
    cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_mtd = (datetime.date.today() + relativedelta(months=-6)).replace(day=1).strftime('%Y-%m-%d')
    end_mtd = (datetime.date.today() + relativedelta(days=-1)).strftime('%Y-%m-%d')

    # =============================================================================
    # Store master
    # =============================================================================
    query = f"""
        select
            id as "store-id",
            store as "store-name",
            "store-manager" ,
            "line-manager" ,
            abo
        from
            "prod2-generico"."stores-master" sm
    """
    rs_db.execute(query, params=None)
    stores_master_df: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    logger.info("Data: stores-master fetched successfully")

    # =============================================================================
    # local purchase instances base data
    # =============================================================================

    limit_str = f" limit {limit} ; " if limit else ""
    query = f"""
        select
            ii.id as "invoice-item-id",
            date(i."received-at") as "received-date",
            ii."drug-id" ,
            i."store-id" ,
            ii."invoice-item-reference" ,
            ii."net-value" as "lp-value",
            ii."actual-quantity" as "lp-qty"
        from
            "prod2-generico"."invoice-items-1" ii
        inner join "prod2-generico"."invoices-1" i on
            ii."franchisee-invoice-id" = i.id
        where 
            date(i."received-at") >= '%s'
            and date(i."received-at") <= '%s'
            and i."invoice-reference" is null
        {limit_str}
    """ % (start_mtd, end_mtd)

    rs_db.execute(query=query, params=None)
    lp_df: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    logger.info("Data: lp invoice fetched successfully")

    lp_2_df = lp_df.groupby(['received-date', 'invoice-item-id', 'store-id', 'drug-id'],
                            as_index=False).agg({'lp-value': ['sum'], 'lp-qty': ['sum']}).reset_index(drop=True)
    lp_2_df.columns = ["-".join(x).rstrip('-') for x in lp_2_df.columns.ravel()]

    # =============================================================================
    # local purchase liquidation
    # =============================================================================

    query = f"""
                
   SELECT 
            c."invoice-item-id",
            b."store-id",
            c."drug-id",
            SUM(c."ptr" * a."quantity") AS "lp-sales",
            SUM(a."quantity") AS "lp-qty-sales"
        FROM
            "prod2-generico"."bill-items-1" a
                LEFT JOIN
            "prod2-generico"."bills-1" b ON b."id" = a."bill-id"
                LEFT JOIN
            "prod2-generico"."inventory-1" c ON c."id" = a."inventory-id"
                LEFT JOIN
            "prod2-generico"."invoice-items-1" ii ON ii."id" = c."invoice-item-id"
                JOIN
            "prod2-generico"."invoices-1" i1 ON i1."id" = ii."franchisee-invoice-id"
        WHERE
				DATE(a."created-at") >= '{start_mtd}'
				AND DATE(a."created-at") <= '{end_mtd}'
				AND
                i1."invoice-reference" IS NULL
        GROUP BY c."invoice-item-id" , b."store-id" , c."drug-id" 
        UNION ALL SELECT 
            c."invoice-item-id",
            b."store-id",
            c."drug-id",
            (SUM(c."ptr" * a."returned-quantity") * - 1) AS "lp-sales",
            (SUM(a."returned-quantity") * - 1) AS "lp-qty-sales"
        FROM
            "prod2-generico"."customer-return-items-1" a
                LEFT JOIN
            "prod2-generico"."customer-returns-1" b ON b."id" = a."return-id"
                LEFT JOIN
            "prod2-generico"."inventory-1" c ON c."id" = a."inventory-id"
                LEFT JOIN
            "prod2-generico"."invoice-items-1" ii ON ii."id" = c."invoice-item-id"
                JOIN
            "prod2-generico"."invoices-1" i1 ON i1."id" = ii."franchisee-invoice-id"
        WHERE
				DATE(a."returned-at") >= '{start_mtd}'
				AND DATE(a."returned-at") <= '{end_mtd}'
				AND
                i1."invoice-reference" IS NULL
        GROUP BY c."invoice-item-id" , b."store-id" , c."drug-id"
        {limit_str}
    """
    rs_db.execute(query=query, params=None)
    sales_df: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    logger.info("Data: sales fetched successfully")

    sales_2_df = sales_df.groupby(['invoice-item-id', 'drug-id'], as_index=False).agg(
        {'lp-sales': ['sum'], 'lp-qty-sales': ['sum']}).reset_index(drop=True)
    sales_2_df.columns = ["-".join(x).rstrip('-') for x in sales_2_df.columns.ravel()]

    # =============================================================================
    # Drug details extraction
    # =============================================================================
    query = """
        select
            id as "drug-id",
            "drug-name",
            "type",
            "category",
            "company",
            "composition"
        from
            "prod2-generico".drugs d
    """
    rs_db.execute(query=query, params=None)
    drug_df: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    logger.info("Data: drug fetched successfully")

    # =============================================================================
    # Drug disease extraction
    # =============================================================================
    query = """
        select
            "drug-id",
            "drug-primary-disease" as "drug-disease"
        from
            "prod2-generico"."drug-primary-disease"
    """
    rs_db.execute(query=query, params=None)
    drug_disease_df: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    logger.info("Data: drug-disease fetched successfully")

    # Merge all data points
    local_purchase_df = pd.merge(left=stores_master_df, right=lp_2_df, on=['store-id'], how='right')
    local_purchase_df = pd.merge(left=local_purchase_df, right=sales_2_df, on=['invoice-item-id', 'drug-id'],
                                 how='left')
    local_purchase_df = pd.merge(left=local_purchase_df, right=drug_df, on=['drug-id'], how='left')
    lp_liquidation_df = pd.merge(left=local_purchase_df, right=drug_disease_df, how='left', on=['drug-id'])
    logger.info("Merging of all data points successful.")

    lp_liquidation_df['refreshed-at'] = datetime.datetime.now()

    return lp_liquidation_df


def main(rs_db, s3, limit):
    schema = 'prod2-generico'
    table_name = 'lp-liquidation'
    table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)
    if isinstance(table_info, type(None)):
        raise Exception(f"table: {table_name} do not exist, create the table first")
    else:
        logger.info(f"Table:{table_name} exists")
        """ seek the data """
        lp_liquidation_df = seek(rs_db=rs_db, limit=limit)

        truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
        rs_db.execute(truncate_query)

        s3.write_df_to_db(df=lp_liquidation_df[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-l', '--limit', default=None, type=int, required=False)
    parser.add_argument('-jn', '--job_name', default=None, type=str, required=False)
    parser.add_argument('-lem', '--log_email_to', default=None, type=str, required=False)
    args, unknown = parser.parse_known_args()
    env = args.env
    job_name = args.job_name
    log_email_to = args.log_email_to.split(",")
    limit = args.limit

    os.environ['env'] = env

    logger = get_logger()

    logger.info(f"env: {env}")
    logger.info(f"logger.info the env again: {env}")

    rs_db = DB()
    rs_db.open_connection()

    s3 = S3()

    """ calling the main function """
    main(rs_db=rs_db, s3=s3, limit=limit)

    # Closing the DB Connection
    rs_db.close_connection()

    """ 
    Sending the job  logs,
    1. But if jobs fails before this step, you will not get the log email, so handle the exception  
    """
    send_logs_via_email(job_name=job_name, email_to=log_email_to)
