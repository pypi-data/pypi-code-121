"""
Author:shubham.gupta@zeno.health
Purpose: BOGO Tracking Visibility
"""

import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.email.email import Email

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-skus', '--skus_tracked', type=str, default='0, 0', required=False)

args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()
email_to = args.email_to
skus = tuple(map(int, args.skus_tracked.split(',')))
logger.info(skus)

logger.info(f"env: {env}")
logger.info(f"print the env again: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

read_schema = 'prod2-generico'

# Fetching earn and burn data for past one week
penetration_q = f""" select
                        date("created-at") as date,
                        rm.store as Store_Name,
                        rm."store-city" as City_Name,
                        SUM(case when rm."promo-code" = 'BOGO' then 1 else 0 end) BOGO_Bills,
                        COUNT(distinct rm.id) Total_Bills,
                        SUM(case when rm."promo-code" = 'BOGO' then 1 else 0 end) / COUNT(distinct rm.id) Penetration
                    from
                        "{read_schema}"."retention-master" rm
                    where
                        date(rm."created-at") >= '2022-02-21'
                        and DATE(rm."created-at") < current_date 
                        and extract (day from DATE(rm."created-at")) >= 1
                        and extract (month from DATE(rm."created-at")) = extract (month from current_date )
                    group by
                        date("created-at"),
                        rm.store,
                        rm."store-city";"""

penetration_city_q = f"""
                    select
                        date("created-at") as date,
                        rm."store-city" as City_Name,
                        SUM(case when rm."promo-code" = 'BOGO' then 1 else 0 end) BOGO_Bills,
                        COUNT(distinct rm.id) Total_Bills,
                        SUM(case when rm."promo-code" = 'BOGO' then 1 else 0 end) / COUNT(distinct rm.id) Penetration
                    from
                        "{read_schema}"."retention-master" rm
                    where
                        date(rm."created-at") >= '2022-02-21'
                        and DATE(rm."created-at") < current_date 
                        and extract (day from DATE(rm."created-at")) >= 1
                        and extract (month from DATE(rm."created-at")) = extract (month from current_date )
                    group by
                        date("created-at"),
                        rm."store-city";"""

sku_q = f"""
            select
                date(s."created-at") date_,
                s."store-name",
                s."drug-name",
                s."drug-id", 
                s."bill-flag",
                (case
                    when s."promo-code" = 'BOGO' then 'BOGO'
                    when s."promo-code" is null then 'Organic'
                    when s."code-type" = 'referral' then 'referral'
                    else s."promo-code"
                    end) Promo_Code, 
                sum(s.quantity) quantity_
            from
                "{read_schema}"."sales" s
            where
                s."drug-id" in {skus}
                and date(s."created-at") >= '2022-02-21'
                and date(s."created-at") < current_date
                and extract(day from s."created-at") >= 1
                and extract(month from s."created-at") = extract(month from current_date) 
            group by
                date(s."created-at"),
                s."store-name",
                s."drug-name",
                s."drug-id", 
                s."bill-flag",
                (case
                    when s."promo-code" = 'BOGO' then 'BOGO'
                    when s."promo-code" is null then 'Organic'
                    when s."code-type" = 'referral' then 'referral'
                    else s."promo-code"
                    end);
            """

avg_sku_q = f"""
            select
                T.date_,
                T."store-name",
                AVG(T.number_of_sku)
            from
                (
                select
                    date(s."created-at") date_,
                    s."bill-id",
                    s."store-name",
                    COUNT(distinct s."drug-id") number_of_sku
                from
                    "{read_schema}"."sales" s
                where
                    s."promo-code" = 'BOGO'
                    and date(s."created-at") >= '2022-02-21'
                    and date(s."created-at") < current_date
                    and extract(day
                from
                    date(s."created-at")) >= 1
                    and extract(month
                from
                    date(s."created-at")) = extract(month
                from
                    current_date)
                group by
                    date(s."created-at"),
                    s."bill-id",
                    s."store-name") T
            group by
                T.date_,
                T."store-name";"""

penetration = rs_db.get_df(penetration_q)
penetration_city = rs_db.get_df(penetration_city_q)
sku = rs_db.get_df(sku_q)
avg_sku = rs_db.get_df(avg_sku_q)

# MTD Report
penetration_mtd = penetration.groupby(['store_name',
                                       'city_name'],
                                      as_index=False).agg({'bogo_bills': 'sum',
                                                           'total_bills': 'sum',
                                                           'penetration': 'mean'})

penetration_city_mtd = penetration_city.groupby(['city_name'], as_index=False).agg({'bogo_bills': 'sum',
                                                                                    'total_bills': 'sum',
                                                                                    'penetration': 'mean'})

# file_name

penetration_file_name = 'penetration.csv'
penetration_mtd_file_name = 'penetration_mtd.csv'
penetration_city_file_name = 'penetration_city.csv'
penetration_city_mtd_file_name = 'penetration_city_mtd.csv'
sku_file_name = 'sku_sold.csv'
avg_sku_file_name = 'avg_sku_in_bill.csv'

# Uploading the file to s3
penetration = s3.save_df_to_s3(df=penetration, file_name=penetration_file_name)
penetration_mtd = s3.save_df_to_s3(df=penetration_mtd, file_name=penetration_mtd_file_name)
penetration_city = s3.save_df_to_s3(df=penetration_city, file_name=penetration_city_file_name)
penetration_city_mtd = s3.save_df_to_s3(df=penetration_city_mtd, file_name=penetration_city_mtd_file_name)
sku = s3.save_df_to_s3(df=sku, file_name=sku_file_name)
avg_sku = s3.save_df_to_s3(df=avg_sku, file_name=avg_sku_file_name)

# Sending email
subject = 'Campaign Tracker (BOGO)'
mail_body = "Reports are attached"
file_uris = [penetration, penetration_mtd, penetration_city, penetration_city_mtd, sku, avg_sku]
email = Email()
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)

# closing the connection
rs_db.close_connection()
