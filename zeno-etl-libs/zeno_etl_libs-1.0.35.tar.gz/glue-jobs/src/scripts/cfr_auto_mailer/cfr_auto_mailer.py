"""
Author:shubham.gupta@zeno.health
Purpose: cfr-visibility auto-mailer
"""
import argparse
import os
import sys
from datetime import datetime as dt
from datetime import timedelta

import numpy as np
import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-dws', '--day_wise_sale', default=1, type=int, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
day_wise_sale = args.day_wise_sale
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

read_schema = 'prod2-generico'

# Fetching data from google sheet
gs = GoogleSheet()

cfr_data = gs.download({
    "spreadsheet_id": "18SUPchsLqNAl0m7xSu09jz51taZO5JgZtQQAliahddg",
    "sheet_name": "CFR",
    "listedFields": []})
generic_activity_data = gs.download({
    "spreadsheet_id": "18SUPchsLqNAl0m7xSu09jz51taZO5JgZtQQAliahddg",
    "sheet_name": "Generic Activity",
    "listedFields": []})

data_cfr = pd.DataFrame(cfr_data)
data_generic = pd.DataFrame(generic_activity_data)
data_cfr['Project'] = 'CFR Search'
data_generic['Project'] = 'Generic Assrt Extention'

data = pd.concat([data_cfr, data_generic])

end = dt.now().date() - timedelta(days=1)
start_m = dt.now().date() - timedelta(days=30)
start_w1 = dt.now().date() - timedelta(days=7)
start_w2 = dt.now().date() - timedelta(days=14)

data = data[['store_id', 'drug_id', 'drug name', 'drug grp', 'cat', 'Project']]
data.columns = [c.replace('_', '-') for c in data.columns]
data = data.drop_duplicates()
data['drug grp'] = data['drug grp'].apply(lambda x: "others" if x not in ('ethical', 'generic') else x)
drugs = tuple(data['drug-id'].drop_duplicates())
limit_str = " "
doi_q = f"""
        SELECT
            "store-id",
            "drug-id",
            "min",
            "safe-stock",
            "max",
            "as-active",
            "ms-active",
            "pr-active"
        FROM
            "{read_schema}"."drug-order-info"
        WHERE
            "drug-id" in {drugs}
        {limit_str}"""

inv_q = f"""
        SELECT
            "store-id",
            "drug-id",
            SUM("locked-quantity" + "quantity" + "locked-for-audit" + "locked-for-transfer" 
            + "locked-for-check" + "locked-for-return") AS "current-inventory",
            SUM(("locked-quantity" + "quantity" + "locked-for-audit" + "locked-for-transfer" 
            + "locked-for-check" + "locked-for-return")* ptr) as "inv-value"
        FROM
            "{read_schema}"."inventory-1"
        WHERE
            "drug-id" in {drugs}
        GROUP BY
            "store-id",
            "drug-id" {limit_str};"""

sales_q = f"""
        select
            "store-id",
            "drug-id",
            DATE("created-at") as "sales-date",
            sum("net-quantity") as "net-sales-quantity",
            sum("revenue-value") as "net-sales-value"
        from
            "{read_schema}".sales s
        where
            DATE("created-at") between '{start_m}' and '{end}'
            and "drug-id" in {drugs}
        group by
            "store-id",
            "drug-id",
            DATE("created-at") {limit_str};
        """

doi = rs_db.get_df(doi_q)
inv = rs_db.get_df(inv_q)
sales = rs_db.get_df(sales_q)

data['store-id'] = data['store-id'].astype(int)
data['drug-id'] = data['drug-id'].astype(int)

data = pd.merge(data, doi, how='left', on=['store-id', 'drug-id'])

inv['current-inventory'] = inv['current-inventory'].apply(lambda x: 0 if x < 1 else x)
inv['inv-value'] = inv['inv-value'].apply(lambda x: 0 if x < 1 else x)

data = pd.merge(data, inv, how='left', on=['store-id', 'drug-id'])

D_30 = sales[sales['sales-date'].between(start_m, end)].groupby(['store-id',
                                                                 'drug-id'],
                                                                as_index=False).agg({'net-sales-quantity': 'sum',
                                                                                     'net-sales-value': 'sum'})

D_14 = sales[sales['sales-date'].between(start_w2,
                                         end)].groupby(['store-id',
                                                        'drug-id'],
                                                       as_index=True).agg(
    sales_quantiy_14=('net-sales-quantity', 'sum'),
    sales_value_14=('net-sales-value', 'sum')).reset_index()

D_07 = sales[sales['sales-date'].between(start_w1,
                                         end)].groupby(['store-id',
                                                        'drug-id'],
                                                       as_index=True).agg(
    sales_quantiy_07=('net-sales-quantity', 'sum'),
    sales_value_07=('net-sales-value', 'sum')).reset_index()

D_30['net-sales-quantity'] = D_30['net-sales-quantity'].apply(lambda x: 0 if x < 1 else x)
D_30['net-sales-value'] = D_30['net-sales-value'].apply(lambda x: 0 if x < 1 else x)

if day_wise_sale:
    sales_day_wise = pd.pivot_table(data=sales,
                                    index=['store-id', 'drug-id'],
                                    columns='sales-date', values='net-sales-quantity',
                                    aggfunc='sum').reset_index().fillna(0)
    data = pd.merge(data, sales_day_wise, how='left', on=['store-id', 'drug-id'])

data = pd.merge(data, D_30, how='left', on=['store-id', 'drug-id'])
data = pd.merge(data, D_14, how='left', on=['store-id', 'drug-id'])
data = pd.merge(data, D_07, how='left', on=['store-id', 'drug-id'])

data['Max>0 Count'] = data['max'].apply(lambda x: 1 if x > 0 else 0)
data['Total Str-Drg Combinations'] = 1
data['Inv > 0 Count'] = data['current-inventory'].apply(lambda x: 1 if x > 0 else 0)
data = data.fillna(0)

availability_summary = data.groupby(['Project', 'drug grp'],
                                    as_index=False).agg({'Total Str-Drg Combinations': 'sum',
                                                         'max': 'sum',
                                                         'Max>0 Count': 'sum',
                                                         'as-active': 'sum',
                                                         'current-inventory': 'sum',
                                                         'Inv > 0 Count': 'sum'})

availability_summary['Availability %'] = availability_summary['Inv > 0 Count'] / availability_summary[
    'Total Str-Drg Combinations']

availability_summary.columns = ['Project',
                                'Type',
                                'Total Str-Drg Combinations',
                                'Max',
                                'Max>0 Count',
                                'AS Active Count',
                                'Inv QTY',
                                'Inv > 0 Count',
                                'Availability %']

inventory_doh_summary = data.groupby(['Project', 'drug grp'],
                                     as_index=False).agg({'Total Str-Drg Combinations': 'sum',
                                                          'current-inventory': 'sum',
                                                          'inv-value': 'sum',
                                                          'net-sales-quantity': 'sum',
                                                          'net-sales-value': 'sum'
                                                          })

inventory_doh_summary['Avg DOH'] = inventory_doh_summary['inv-value'] * 30 / inventory_doh_summary[
    'net-sales-value']

inventory_doh_summary.columns = ['Project',
                                 'Type',
                                 'Total Str-Drg Combinations',
                                 'Inv QTY',
                                 'Inv Value',
                                 'Last 30 days sales qty',
                                 'Last 30 days sales Value',
                                 'Avg DOH']

data['inv-value'] = data['inv-value'].astype(float)
data['net-sales-value'] = data['net-sales-value'].astype(float)
data['DOH'] = data['inv-value'] * 30 / data['net-sales-value']

data['DOH'] = data['DOH'].fillna(0)

data['DOH Buckets'] = pd.cut(data['DOH'], bins=[-1, 7, 15, 30, 90, 10000, np.inf], labels=['less than 7',
                                                                                           '7 - 15 days',
                                                                                           '15-30 days',
                                                                                           '30-90 days',
                                                                                           'greater than 90 days',
                                                                                           'No sales'])
data['DOH Buckets'] = np.where(data['current-inventory'] < 1, 'No Stock', data['DOH Buckets'])

doh_buckets = data.groupby(['Project', 'DOH Buckets'],
                           as_index=True).agg({'Total Str-Drg Combinations': 'sum',
                                               'inv-value': 'sum',
                                               'net-sales-value': 'sum',
                                               'DOH': 'mean'}).reset_index()

doh_buckets.columns = ['Project',
                       'DOH Buckets',
                       'Count Of Str-Drug',
                       'Inv Val',
                       'Sales Val ( Last 30 days )',
                       'Avg DOH']

str_drg = data[['store-id', 'drug-id', 'Project']].drop_duplicates()
str_drg = str_drg.rename(columns={'Project': 'project'})

file_name = 'Summary_Report.xlsx'
file_path = s3.write_df_to_excel(data={'Presence & Availability': availability_summary,
                                       'Inventory DOH': inventory_doh_summary,
                                       'DOH Buckets': doh_buckets,
                                       'base file': data}, file_name=file_name)

email = Email()
email.send_email_file(subject="Weekly CFR Visibility Report",
                      mail_body=f'Weekly CFR Visibility Report from', # {start_m} to {end}',
                      to_emails=email_to, file_uris=[], file_paths=[file_path])
