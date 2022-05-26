#!/usr/bin/env python
# coding: utf-8


# !/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
import argparse
import pandas as pd
import re
from datetime import date
from datetime import datetime
import dateutil.relativedelta
import numpy as np
from dateutil.tz import gettz



start_dt = (datetime.now() + dateutil.relativedelta.relativedelta(months=-1)
            ).replace(day=1).date().strftime("%Y-%m-%d")
end_dt = date.today().strftime("%Y-%m-%d")



parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="akshay.bhutada@zeno.health", type=str, required=False)
parser.add_argument('-sd', '--start_date', default='NA', type=str, required=False)
parser.add_argument('-ed', '--end_date', default='NA', type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to
start_date = args.start_date
end_date = args.end_date

if start_date == 'NA' and end_date == 'NA':
    start_date = start_dt
    end_date = end_dt



logger = get_logger()
logger.info(f"env: {env}")



logger.info('Script Manager Initialized')


rs_db = DB()



rs_db.open_connection()



start_date_n = datetime.strptime('{0}'.format(start_date), "%Y-%m-%d").replace(day=1).date()




end_date_n = datetime.strptime('{0}'.format(end_date), "%Y-%m-%d").replace(day=1).date()



drug_q = '''
select
	d.id as "drug_id",
	d."drug-name" as "drug_name",
	d."type" as "drug_type",
	d.category as "drug_category",
	d."repeatability-index" as "drug_repeatability_index",
	d.schedule as "drug_schedule",
	d.company as "drug_company",
	d.composition as "drug_composition",
	d.pack as "drug_pack",
	d."pack-form" as "drug_pack_form"
from
	"prod2-generico".drugs d'''



drugs = rs_db.get_df(query=drug_q)



# Extract drug composition from drug name using regex
# added 'r' prefix





drugs['drug_dosage'] = drugs['drug_composition'].apply(lambda x:
                                                       re.findall(r"\((.*?)\)", x))



# Remove brackets from drug dosage column
# drugs = drugs.copy(deep=True)
drugs['drug_dosage'] = drugs['drug_dosage'].astype(str)
drugs['drug_dosage'] = drugs['drug_dosage'].str.strip('[]')



# Remove brackets from drug dosage column
# drugs = drugs.copy(deep=True)
# drugs['drug_dosage'] = drugs['drug_dosage'].astype(str)
# drugs['drug_dosage'] = drugs['drug_dosage'].str.strip('[]')

# Remove inverted commas from drug dosage column
drugs['drug_dosage'] = drugs['drug_dosage'].apply(lambda x: x.replace("'", ''))



# Remove dosage from composition
drugs['drug_composition'] = drugs['drug_composition'].apply(lambda x:
                                                            re.sub(r" ?\([^)]+\)", "", x))

# Apply repeatability condition to check whether drug is repeatable or not
drugs['drug_is_repeatable'] = np.where(((drugs['drug_repeatability_index'] >= 80) |
                                        ((drugs['drug_category'] == 'chronic') &
                                         (drugs['drug_repeatability_index'] >= 40))),
                                       'yes', 'no')

bi_data_grp = '''
select
	s."month-created-at" as "bill_month",
	s."year-created-at" as "bill_year" ,
	"store-id" as "store_id",
	"drug-id" as "drug_id",
	COUNT(distinct "patient-id") as "no_of_customers",
	COUNT(distinct "bill-id") as "no_of_bills",
	SUM(quantity) as "gross_quantity",
	SUM(s.quantity * s.rate) as "gross_sales",
	SUM(s.quantity * s."purchase-rate") as "gross_cogs",
	SUM(s.quantity *  s.mrp ) as "gross_mrp_sales"
from
	"prod2-generico".sales s
	where s."bill-flag" ='gross' and date(s."created-at")>='{}' and date(s."created-at")<='{}'
group by 
s."month-created-at",
s."year-created-at",
"store-id",
"drug-id" 
'''.format(start_date, end_date)



bi_data_grp = rs_db.get_df(query=bi_data_grp)

logger.info(bi_data_grp)



bi_data_grp['avg_selling_rate'] = bi_data_grp['gross_sales'] / bi_data_grp['gross_quantity']
bi_data_grp['avg_drug_cogs'] = bi_data_grp['gross_cogs'] / bi_data_grp['gross_quantity']
bi_data_grp['avg_drug_mrp'] = bi_data_grp['gross_mrp_sales'] / bi_data_grp['gross_quantity']
bi_data_grp['abv'] = bi_data_grp['gross_sales'] / bi_data_grp['no_of_bills']


data_return_grp = '''
select
	s."month-created-at" as "return_month",
	s."year-created-at" as "return_year" ,
	"store-id" as "store_id",
	"drug-id" as "drug_id",
	SUM(quantity) as "return_quantity",
	SUM(s.quantity * s.rate) as "return_value",
	SUM(s.quantity * s."purchase-rate") as "return_cogs",
	SUM(s.quantity *  s.mrp ) as "return_mrp_value"
from
	"prod2-generico".sales s
	where s."bill-flag" ='return' and date(s."created-at")>='{start_date}' and date(s."created-at")<='{end_date}'
group by 
s."month-created-at" ,
s."year-created-at" ,
"store-id",
"drug-id" 
'''.format(start_date=start_date, end_date=end_date)


data_return_grp = rs_db.get_df(query=data_return_grp)



data_return_grp['avg_return_rate'] = data_return_grp['return_value'] / data_return_grp['return_quantity']
data_return_grp['avg_drug_cogs'] = data_return_grp['return_cogs'] / data_return_grp['return_quantity']
data_return_grp['avg_drug_mrp'] = data_return_grp['return_mrp_value'] / data_return_grp['return_quantity']



data_return_grp.drop(['return_cogs', 'return_mrp_value'], axis=1, inplace=True)



# Merge patient bill item data and customer returns data by outer
# on 'bill_month'/'return_month',
# 'bill_year'/'return_year', 'store_id','drug_id' to get aggregated data
# on store,drug,month level
# Outer merge has been done so that going forward, net measures
# can be calculated on
# exact month/year of returns only




merge_data = pd.merge(bi_data_grp, data_return_grp, how='outer',
                      left_on=['bill_month', 'bill_year', 'store_id', 'drug_id'],
                      right_on=['return_month', 'return_year', 'store_id', 'drug_id'])

bi_data_grp = ''
data_return_grp = ''


# Fill up avg_drug_cogs and avg_drug_mrp values in bill item data table
# from returns table
# wherever they are null
merge_data['avg_drug_cogs_x'] = np.where(merge_data['avg_drug_cogs_x'].isnull(),
                                         merge_data['avg_drug_cogs_y'], merge_data['avg_drug_cogs_x'])



merge_data.drop('avg_drug_cogs_y', axis=1, inplace=True)
merge_data.rename({'avg_drug_cogs_x': 'avg_drug_cogs'},
                  axis=1, inplace=True)



merge_data['avg_drug_mrp_x'] = np.where(merge_data['avg_drug_mrp_x'].isnull(),
                                        merge_data['avg_drug_mrp_y'], merge_data['avg_drug_mrp_x'])
merge_data.drop('avg_drug_mrp_y', axis=1, inplace=True)
merge_data.rename({'avg_drug_mrp_x': 'avg_drug_mrp'}, axis=1, inplace=True)



# Fill up null values of important numeric columns
merge_data['return_quantity'].fillna(0, inplace=True)
merge_data['return_value'].fillna(0, inplace=True)

merge_data['gross_quantity'].fillna(0, inplace=True)
merge_data['gross_sales'].fillna(0, inplace=True)



# Net quantity and net sales columns are calculated
merge_data['net_quantity'] = merge_data['gross_quantity'] - merge_data['return_quantity']
merge_data['net_sales'] = merge_data['gross_sales'] - merge_data['return_value']



merge_data['avg_drug_cogs'] = pd.to_numeric(merge_data['avg_drug_cogs'])



merge_data['return_cogs'] = merge_data['avg_drug_cogs'] * merge_data['return_quantity']



merge_data['gross_cogs'].fillna(0, inplace=True)




merge_data['gross_cogs'] = pd.to_numeric(merge_data['gross_cogs'])




merge_data['net_cogs'] = merge_data['gross_cogs'] - merge_data['return_cogs']




merge_data['avg_drug_mrp'] = pd.to_numeric(merge_data['avg_drug_mrp'])
merge_data['net_quantity'] = pd.to_numeric(merge_data['net_quantity'])



merge_data['net_mrp_sales'] = merge_data['avg_drug_mrp'] * merge_data['net_quantity']



merge_data['gross_sales'] = pd.to_numeric(merge_data['gross_sales'])
merge_data['gross_cogs'] = pd.to_numeric(merge_data['gross_cogs'])



merge_data['gross_margin'] = merge_data['gross_sales'] - merge_data['gross_cogs']



merge_data['net_sales'] = pd.to_numeric(merge_data['net_sales'])
merge_data['net_cogs'] = pd.to_numeric(merge_data['net_cogs'])



merge_data['net_margin'] = merge_data['net_sales'] - merge_data['net_cogs']


merge_data['gross_margin_percentage'] = merge_data['gross_margin'] / merge_data['gross_sales'] * 100
merge_data['net_margin_percentage'] = merge_data['net_margin'] / merge_data['net_sales'] * 100



merge_data['final_month'] = merge_data['bill_month']
merge_data['final_year'] = merge_data['bill_year']

merge_data['final_month'] = np.where(merge_data['final_month'].isnull(),
                                     merge_data['return_month'], merge_data['final_month'])
merge_data['final_year'] = np.where(merge_data['final_year'].isnull(),
                                    merge_data['return_year'], merge_data['final_year'])



# Import Shortbook-1 data to calculate drug fill rate:

sb_q_total_order = '''
select
	sb."store-id",
	sb."drug-id",
	sb.quantity as sb_quantity,
	sb."created-at" as "sb-created-at" ,
	sb."received-at" as "sb-received-at"
from
	"prod2-generico"."short-book-1" sb 
where sb.quantity >0 and sb."auto-generated" =0 and date(sb."created-at")>='{start_date}' and date(sb."created-at")<='{end_date}' 
'''.format(start_date=start_date, end_date=end_date)



data_sb_1 = rs_db.get_df(query=sb_q_total_order)


sb_q_fullfilled_order = '''
select
	sb."store-id",
	sb."drug-id",
	sb.quantity as sb_quantity,
	sb."created-at" as "sb-created-at" ,
	sb."received-at" as "sb-received-at"
from
	"prod2-generico"."short-book-1" sb 
where sb.quantity >0 and sb."auto-generated" =0 and date(sb."created-at")>='{start_date}' and date(sb."created-at")<='{end_date}' 
and sb."received-at" !='0101-01-01 00:00:00.000'
'''.format(start_date=start_date, end_date=end_date)

data_sb_2 = rs_db.get_df(query=sb_q_fullfilled_order)


data_sb_1.columns = [c.replace('-', '_') for c in data_sb_1.columns]

data_sb_2.columns = [c.replace('-', '_') for c in data_sb_2.columns]

data_sb_1['sb_created_at'] = pd.to_datetime(data_sb_1['sb_created_at'])
data_sb_1['sb_month'] = data_sb_1['sb_created_at'].dt.month
data_sb_1['sb_year'] = data_sb_1['sb_created_at'].dt.year

data_sb_2['sb_created_at'] = pd.to_datetime(data_sb_2['sb_created_at'])
data_sb_2['sb_month'] = data_sb_2['sb_created_at'].dt.month
data_sb_2['sb_year'] = data_sb_2['sb_created_at'].dt.year
data_sb_1 = data_sb_1.groupby(['sb_month', 'sb_year', 'store_id', 'drug_id'])['sb_created_at'].count().to_frame(
    name='total_orders').reset_index()


#data_sb_2 = data_sb[data_sb['sb_received_at'] == '0101-01-01 00:00:00.000']


data_sb_2 = data_sb_2.groupby(['sb_month', 'sb_year', 'store_id', 'drug_id'])['sb_received_at'].count().to_frame(
    name='orders_fulfilled').reset_index()



data_sb = pd.merge(data_sb_1, data_sb_2, how='left',
                   on=['sb_month', 'sb_year', 'store_id', 'drug_id'])
data_sb['total_orders'].fillna(0, inplace=True)
data_sb['orders_fulfilled'].fillna(0, inplace=True)


# Entire bill item and returns combined data-frame is merged
# with the drugs dataframe on 'drug_id'

category_data = pd.merge(drugs, merge_data, how='right', on='drug_id')

drugs = ''



# Group by 'final_month','final_year','store_id','drug_id','drug_type'
# to find revenue and qty by drug type

category_data_grp = category_data.groupby(['final_month', 'final_year', 'store_id',
                                           'drug_id', 'drug_type']
                                          )['gross_sales', 'gross_quantity'].sum().reset_index()

category_data_grp['generic_revenue'] = np.where(category_data_grp['drug_type'] == 'generic',
                                                category_data_grp['gross_sales'], 0)
category_data_grp['generic_quantity'] = np.where(category_data_grp['drug_type'] == 'generic',
                                                 category_data_grp['gross_quantity'], 0)

category_data_grp['ethical_revenue'] = np.where(category_data_grp['drug_type'] == 'ethical',
                                                category_data_grp['gross_sales'], 0)
category_data_grp['ethical_quantity'] = np.where(category_data_grp['drug_type'] == 'ethical',
                                                 category_data_grp['gross_quantity'], 0)



# Group by 'final_month','final_year','store_id','drug_id'
# and exclude drug type to now find aggregates for later on calculating substitution %

category_data_grp = category_data_grp.groupby(['final_month', 'final_year', 'store_id', 'drug_id'])[
    'gross_sales', 'gross_quantity', 'generic_revenue', 'generic_quantity',
    'ethical_revenue', 'ethical_quantity'].sum().reset_index()



# Drop gross sales and gross quantity columns to avoid column duplicates later on
category_data_grp.drop(['gross_sales', 'gross_quantity'], axis=1, inplace=True)

# Merge main category data frame with the substitution(category_data_grp) data frame
category_data = pd.merge(category_data, category_data_grp, how='left',
                         on=['final_month', 'final_year', 'store_id', 'drug_id'])

# Merge this data-frame with short-book dataframe on 'month','year','store_id','drug_id'
category_data = pd.merge(category_data, data_sb, how='left',
                         left_on=['final_month', 'final_year',
                                  'store_id', 'drug_id'],
                         right_on=['sb_month', 'sb_year',
                                   'store_id', 'drug_id'])
data_sb = ''
category_data_grp = ''

# Calculate drug fill rate by dividing orders fulfilled by total orders drug-wise
category_data['drug_fill_rate_percentage'] = category_data['orders_fulfilled'] / category_data['total_orders'] * 100



# Calculate normalized date using final_month and final_year
category_data['final_year'] = category_data['final_year'].astype(int)
category_data['final_month'] = category_data['final_month'].astype(int)
category_data['day'] = 1

category_data.rename({'final_year': 'year', 'final_month': 'month'}, axis=1, inplace=True)

category_data['final_date'] = pd.to_datetime(category_data[['year', 'month', 'day']])


# Drop day column and rename month year columns to final_month and final_year.
# Also change their data types to float again
category_data.drop('day', axis=1, inplace=True)
category_data.rename({'year': 'final_year', 'month': 'final_month'}, axis=1, inplace=True)

category_data['final_year'] = category_data['final_year'].astype(float)
category_data['final_month'] = category_data['final_month'].astype(float)


# Re-order columns
category_data = category_data[
    ['final_month', 'final_year', 'bill_month',
     'bill_year', 'return_month', 'return_year',
     'store_id', 'drug_id',
     'drug_name', 'drug_composition', 'drug_dosage',
     'drug_company', 'drug_type', 'drug_category',
     'drug_schedule', 'drug_pack', 'drug_pack_form',
     'drug_repeatability_index', 'drug_is_repeatable',
     'no_of_customers', 'no_of_bills', 'abv',
     'generic_revenue', 'ethical_revenue',
     'generic_quantity', 'ethical_quantity',
     'gross_quantity', 'avg_selling_rate', 'gross_sales',
     'return_quantity', 'avg_return_rate', 'return_value',
     'net_quantity', 'net_sales', 'avg_drug_mrp',
     'gross_mrp_sales', 'net_mrp_sales', 'avg_drug_cogs',
     'gross_cogs', 'return_cogs', 'net_cogs',
     'gross_margin', 'net_margin',
     'gross_margin_percentage', 'net_margin_percentage',
     'sb_month', 'sb_year', 'total_orders', 'orders_fulfilled',
     'drug_fill_rate_percentage', 'final_date']]



# Round off all numeric columns to two decimal places
numeric_cols = ['final_month', 'final_year', 'bill_month', 'bill_year',
                'return_month', 'return_year',
                'store_id', 'drug_id', 'drug_repeatability_index',
                'no_of_customers', 'no_of_bills', 'abv',
                'generic_revenue', 'ethical_revenue',
                'generic_quantity', 'ethical_quantity',
                'gross_quantity', 'avg_selling_rate', 'gross_sales',
                'return_quantity', 'avg_return_rate', 'return_value',
                'net_quantity', 'net_sales',
                'avg_drug_mrp', 'gross_mrp_sales', 'net_mrp_sales',
                'avg_drug_cogs', 'gross_cogs', 'return_cogs',
                'net_cogs', 'gross_margin', 'net_margin',
                'gross_margin_percentage', 'net_margin_percentage',
                'sb_month', 'sb_year',
                'total_orders', 'orders_fulfilled',
                'drug_fill_rate_percentage']


category_data[numeric_cols] = category_data[numeric_cols].round(2)

category_data = category_data.replace([np.inf, -np.inf], np.nan)





category_data['created-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
category_data['updated-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
category_data['created-by'] = 'etl-automation'
category_data['updated-by'] = 'etl-automation'



category_data.columns = [c.replace('_', '-') for c in category_data.columns]
category_data['final-date'] = category_data['final-date'].dt.date


# Delete records of current and last month from table data
delete_q = """
        DELETE
        FROM
            "prod2-generico".category
        WHERE
            "final-date" >= '{start_date_n}'
            and "final-date" <= '{end_date_n}'
    """.format(start_date_n=start_date_n, end_date_n=end_date_n)



rs_db.execute(delete_q)



logger.info('Delete for recent period done')


s3 = S3()

schema = 'prod2-generico'
table_name = 'category'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# Upload data in table for current and last month
s3.write_df_to_db(df=category_data[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)
rs_db.close_connection()