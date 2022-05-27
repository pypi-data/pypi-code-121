"""
Author:shubham.gupta@zeno.health
Purpose: Membership Program
"""

import argparse
import os
import sys
from datetime import datetime as dt
from datetime import timedelta

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.email.email import Email

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-pst', '--pid_sharing_thresh', default=1000, nargs='+', type=int, required=False)

args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
email_to = args.email_to
pid_thresh = args.pid_sharing_thresh
logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

read_schema = 'prod2-generico'
report_date = dt.now().date()

# Fetching earn and burn data for past one week
members_q = f"""
             SELECT
                 *
             FROM
                 "{read_schema}"."member-details" 
             WHERE DATE("created-at") <= '{str(report_date)}' ;
             """
subscription_q = f"""
             SELECT
                 *
             FROM
                 "{read_schema}"."subscriptions-meta"
             WHERE DATE("created-at") <= '{str(report_date)}';
             """
subs_sku_q = f"""
             SELECT
                 "subscription-meta-id",
                 COUNT(DISTINCT "drug-id") "sku-count",
                 AVG(quantity) as "q-per-sku",
                 MAX(DATE("created-at")) AS "created-at"
             FROM
                 "{read_schema}"."subscriptions"
             WHERE DATE("created-at") <= '{str(report_date)}'
             GROUP BY
                 "subscription-meta-id";
                 """
subs_amount_q = f"""
                 SELECT
                     s."subscription-meta-id",
                     SUM(s.quantity * T2.rate) "sub-amount",
                     MAX(DATE(s."created-at")) AS "created-at"
                 FROM
                     "{read_schema}"."subscriptions" s
                 LEFT JOIN "{read_schema}"."subscriptions-meta" sm ON
                     s."subscription-meta-id" = sm.id
                 LEFT JOIN (
                     SELECT
                         *
                     FROM
                         (
                         SELECT
                             "store-id",
                             "drug-id",
                             "selling-rate" rate,
                             RANK() OVER(
                 PARTITION BY "store-id",
                             "drug-id"
                         ORDER BY
                             i."created-at" DESC) AS RRank
                         FROM
                             "{read_schema}"."inventory-1" i )T
                     WHERE
                         RRank = 1) T2 ON
                     s."drug-id" = T2."drug-id"
                     AND sm."preferred-store-id" = T2."store-id"
                 WHERE DATE(s."created-at") <= '{str(report_date)}'
                 GROUP BY
                     s."subscription-meta-id";
                """

calling_q = f"""
             SELECT
                 cd."call-date",
                 COUNT(cd.id) "call-attempt",
                 SUM(T.connected) "call-connected"
             FROM
                 "{read_schema}"."calling-dashboard" cd
             LEFT JOIN (
                 SELECT
                     "calling-dashboard-id",
                     (CASE
                         WHEN SUM(CASE WHEN (connected = 1) OR (("call-recording-url" is not null)
                     AND ("call-recording-url" != '')) THEN 1 ELSE 0 END) > 0 THEN 1
                         ELSE 0
                     END) connected
                 FROM
                     "{read_schema}"."calling-history" ch
                 GROUP BY
                     "calling-dashboard-id") T ON
                 cd.id = T."calling-dashboard-id"
             WHERE
                 cd."campaign-id" = 34
                 AND cd.status = 'closed'
                 AND cd."call-date" <= '{str(report_date)}'
             GROUP BY
                 cd."call-date" ;"""

members = rs_db.get_df(members_q)
subscription = rs_db.get_df(subscription_q)
subs_sku = rs_db.get_df(subs_sku_q)
subs_amount = rs_db.get_df(subs_amount_q)
calling = rs_db.get_df(calling_q)

# date format conversion
members['created-at'] = pd.to_datetime(members['created-at']).dt.date
subscription['created-at'] = pd.to_datetime(subscription['created-at']).dt.date
subs_sku['created-at'] = pd.to_datetime(subs_sku['created-at']).dt.date
subs_amount['created-at'] = pd.to_datetime(subs_amount['created-at']).dt.date

# Previous Day
p_date = report_date - timedelta(days=1)

call_attempt = calling[calling['call-date'] == p_date]['call-attempt'].sum()
call_connect = calling[calling['call-date'] == p_date]['call-connected'].sum()
total_members = members[members['created-at'] == p_date]['patient-id'].nunique()
patients_subscribed = subscription[subscription['created-at'] == p_date]['patient-id'].nunique()
total_subscription = subscription[subscription['created-at'] == p_date]['id'].nunique()
sku_per_sub = round(subs_sku[subs_sku['created-at'] == p_date]['sku-count'].mean())
q_per_sku = round(subs_sku[subs_sku['created-at'] == p_date]['q-per-sku'].mean())
sub_value = round(subs_amount[subs_amount['created-at'] == p_date]['sub-amount'].mean(), 2)

previous_day = """
 Previous Day Stats  

 Membership calls done (attempted) : {attempt}
 Membership calls connected (Phone picked up by the customer) : {call_connect}     

 Membership count : {mc}
 Patient subscription : {ps}
 Average number of SKU per subscription : {a_sku_ps}   
 Quantity per SKU per subscription : {q_sku_ps}
 Average subscription value : {sv}
 Total subscriptions : {ts}
 """.format(mc=total_members, ps=patients_subscribed, a_sku_ps=sku_per_sub, q_sku_ps=q_per_sku,
            sv=sub_value, ts=total_subscription, attempt=call_attempt, call_connect=call_connect)

# Today
call_attempt = calling[calling['call-date'] == report_date]['call-attempt'].sum()
call_connect = calling[calling['call-date'] == report_date]['call-connected'].sum()
total_members = members[members['created-at'] == report_date]['patient-id'].nunique()
patients_subscribed = subscription[subscription['created-at'] == report_date]['patient-id'].nunique()
total_subscription = subscription[subscription['created-at'] == report_date]['id'].nunique()
sku_per_sub = subs_sku[subs_sku['created-at'] == report_date]['sku-count'].mean().round()
q_per_sku = subs_sku[subs_sku['created-at'] == report_date]['q-per-sku'].mean().round()
sub_value = subs_amount[subs_amount['created-at'] == report_date]['sub-amount'].mean().round(2)

current_day = """
 Today Stats

 Membership calls done (attempted) : {attempt}
 Membership calls connected (Phone picked up by the customer) : {call_connect}        

 Membership count : {mc}
 Patient subscription : {ps}
 Average number of SKU per subscription : {a_sku_ps}   
 Quantity per SKU per subscription : {q_sku_ps}
 Average subscription value : {sv}
 Total subscriptions : {ts}
 """.format(mc=total_members, ps=patients_subscribed, a_sku_ps=sku_per_sub, q_sku_ps=q_per_sku,
            sv=sub_value, ts=total_subscription, attempt=call_attempt, call_connect=call_connect)

# Till Today
call_attempt = calling[calling['call-date'] <= report_date]['call-attempt'].sum()
call_connect = calling[calling['call-date'] <= report_date]['call-connected'].sum()
total_members = members[members['created-at'] <= report_date]['patient-id'].nunique()
patients_subscribed = subscription[subscription['created-at'] <= report_date]['patient-id'].nunique()
total_subscription = subscription[subscription['created-at'] <= report_date]['id'].nunique()
sku_per_sub = subs_sku[subs_sku['created-at'] <= report_date]['sku-count'].mean().round()
q_per_sku = subs_sku[subs_sku['created-at'] <= report_date]['q-per-sku'].mean().round()
sub_value = subs_amount[subs_amount['created-at'] <= report_date]['sub-amount'].mean().round(2)

till_today = """
 Report till now   

 Membership calls done (attempted) : {attempt}
 Membership calls connected (Phone picked up by the customer) : {call_connect}       

 Membership count : {mc}
 Patient subscription : {ps}
 Average number of SKU per subscription : {a_sku_ps}   
 Quantity per SKU per subscription : {q_sku_ps}
 Average subscription value : {sv}
 Total subscriptions : {ts}
 """.format(mc=total_members, ps=patients_subscribed, a_sku_ps=sku_per_sub, q_sku_ps=q_per_sku,
            sv=sub_value, ts=total_subscription, attempt=call_attempt, call_connect=call_connect)

mail_body = f"""
 Hey Everyone
 {previous_day} \n
 {current_day} \n
 {till_today} \n

 Thanks & Regards
 """

# Sending email
subject = 'Membership Program Summary'
mail_body = mail_body
# if members.shape[0] <= pid_thresh:
#     file_uris = [blank_file]  # [file_p, file_r, file_t, membership]
# else:
#     file_uris = [blank_file]  # [file_p, file_r, file_t, file_m]
email = Email()
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=[])

# closing the connection
rs_db.close_connection()
