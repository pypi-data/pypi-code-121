import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from dateutil.relativedelta import relativedelta
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
import pandas as pd
import numpy as np
import dateutil
import datetime
from dateutil.tz import gettz
import gc

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name1 = 'dexter-medicine-suggestion'
table_info1 = helper.get_table_info(db=rs_db, table_name=table_name1, schema=schema)

#########################################################
# Billing data (lengthy dataset)
########################################################

bills_q = """
    select
        "created-date" as "bill-date",
        "patient-id" ,
        "bill-id" ,
        "drug-id",
        sum("revenue-value") as "spend",
        sum("net-quantity") as "quantity"
    from
        "prod2-generico"."sales"
    where
        "bill-flag" = 'gross'
        and "created-date" >= date(date_trunc('month', current_date) - interval '12 month')
    group by
        "created-date" ,
        "patient-id" ,
        "bill-id" ,
        "drug-id"
   """
data_bill = rs_db.get_df(bills_q)
data_bill.columns = [c.replace('-', '_') for c in data_bill.columns]

data_bill['bill_date'] = pd.to_datetime(data_bill['bill_date'])

logger.info('Column names of data_bill table {}'.format(str(data_bill.columns)))

drugs_q = """
       SELECT
           "id" as drug_id,
           "composition",
           "drug-name",
           "type",
           "category",
           "repeatability-index",
           "front-img-url"
       FROM
           "prod2-generico"."drugs"
   """
data_drugs = rs_db.get_df(drugs_q)
data_drugs.columns = [c.replace('-', '_') for c in data_drugs.columns]

logger.info("Data for drugs fetched")

# Merge these data-frames

data_raw = data_bill.merge(data_drugs, how='left', on=['drug_id'])
data_raw[['quantity','spend']].fillna(0,inplace=True)
data_raw['quantity']=data_raw['quantity'].astype('int64')
data_raw['spend']=data_raw['spend'].astype('float64')
logger.info('Column names of data_raw table {}'.format(str(data_raw.columns)))

# Delete temp data-frames
del [[data_bill]]
gc.collect()
data_bill = pd.DataFrame()


# Fill NA
logger.info("Composition NA is {}".format(data_raw['composition'].isnull().sum()))
data_raw['composition'] = data_raw['composition'].fillna('')

logger.info("Front image url NA is {}".format(data_raw['front_img_url'].isnull().sum()))
data_raw['front_img_url'] = data_raw['front_img_url'].fillna('')

logger.info("Raw data length - {}".format(len(data_raw)))

logger.info("Raw data info - {}".format(str(data_raw.info())))

# Grp on unique columns
data_bill_base = data_raw.groupby(['patient_id', 'composition',
                                   'bill_date', 'bill_id', 'drug_id',
                                   'drug_name', 'type',
                                   'category', 'repeatability_index',
                                   'front_img_url'])[
    ['spend' ,'quantity']].sum().reset_index()
logger.info(str(data_bill_base.columns))
# Avg rate again
data_bill_base['rate'] = data_bill_base['spend'] / data_bill_base['quantity']

# Delete temp dataframes
del [[data_raw]]
gc.collect()
data_raw = pd.DataFrame()

logger.info("Data length after grouping at unique level - "
            "{}".format(len(data_bill_base)))

# Last bill date and NOB
data_bill_base_grp = data_bill_base.groupby(['patient_id']).agg({'bill_date': 'max',
                                                                 'bill_id': 'nunique'}
                                                                ).reset_index()
data_bill_base_grp = data_bill_base_grp.rename(columns={'bill_date': 'overall_last_bill_date',
                                                        'bill_id': 'overall_num_orders'})

logger.info("Length of patient level last bill date and nob is "
            "{}".format(len(data_bill_base_grp)))

# Drug level Last bill date and NOB
data_bill_base_grp2 = data_bill_base.groupby(['patient_id', 'drug_id']).agg(
    {'bill_date': 'max', 'bill_id': 'nunique'}).reset_index()
data_bill_base_grp2 = data_bill_base_grp2.rename(columns={'bill_date': 'last_bill_date',
                                                          'bill_id': 'num_orders'})

logger.info("Length of patient drug level last bill date and nob is "
            "{}".format(len(data_bill_base_grp2)))

# Sort the base data and make unique on patient-drug
data_bill_base_unique = data_bill_base.sort_values(by=['patient_id',
                                                       'drug_id',
                                                       'bill_date'],
                                                   ascending=[True, True, False])
data_bill_base_unique = data_bill_base_unique.drop_duplicates(subset=['patient_id',
                                                                      'drug_id'])

logger.info("Patient drug level unique base data length is "
            "{}".format(len(data_bill_base_unique)))

# Merge with patient-drug metadata
data_bill_base2 = data_bill_base_unique.merge(data_bill_base_grp2,
                                              how='left',
                                              on=['patient_id', 'drug_id'])

logger.info("After merging with patient drug metadata, length is "
            "{}".format(len(data_bill_base2)))

# Merge with patient-metadata
data_bill_base2 = data_bill_base2.merge(data_bill_base_grp,
                                        how='left',
                                        on=['patient_id'])

logger.info("After merging with patient metadata, length is "
            "{}".format(len(data_bill_base2)))

# Recency
data_bill_base2['recency'] = (data_bill_base2['overall_last_bill_date'] -
                              data_bill_base2['last_bill_date']).dt.days

# Recency flag
data_bill_base2['recency_flag'] = np.where(data_bill_base2['recency'] <= 90, 1, 0)

# Sort on recency and drug nob and last bill date
data_bill_base2 = data_bill_base2.sort_values(by=['recency_flag',
                                                  'num_orders',
                                                  'last_bill_date'],
                                              ascending=[False, False, False])

# Rank
data_bill_base2['recommendation_rank'] = data_bill_base2.groupby(['patient_id']
                                                                 ).cumcount() + 1

# Filter top 12
data_bill_base_f = data_bill_base2[data_bill_base2['recommendation_rank'] <= 12]

logger.info("After rank filtering length is {}".format(len(data_bill_base_f)))

##############################################
# Necessary columns
##############################################
data_bill_base_f['is_chronic'] = np.where(data_bill_base_f['category'] == 'chronic', 1, 0)
data_bill_base_f['is_repeatable'] = np.where((
        ((data_bill_base_f['category'] == 'chronic') &
         (data_bill_base_f['repeatability_index'] >= 40))
        | (data_bill_base_f['repeatability_index'] >= 80)), 1, 0)

data_bill_base_f = data_bill_base_f.rename(columns={'type': 'drug_type',
                                                    'category': 'drug_category',
                                                    'num_orders': 'drug_nob',
                                                    'front_img_url': 'drug_front_image_url'})

data_bill_base_f['last_bill_quantity'] = data_bill_base_f['quantity']
data_bill_base_f['refill_date'] = data_bill_base_f['bill_date'] + datetime.timedelta(days=15)

data_bill_base_f['price_rank'] = data_bill_base_f.sort_values(
    by=['patient_id', 'rate'], ascending=[True, True]).groupby(
    ['patient_id']).cumcount() + 1

data_bill_base_f['refill_date_rank'] = data_bill_base_f.sort_values(
    by=['patient_id', 'refill_date'], ascending=[True, True]).groupby(
    ['patient_id']).cumcount() + 1

data_bill_base_f = data_bill_base_f[~data_bill_base_f['drug_id'].isnull()]

logger.info("After non-null drug-id length is {}".format(len(data_bill_base_f)))

data_export = data_bill_base_f[['patient_id', 'composition', 'drug_id',
                                'drug_name', 'drug_category', 'drug_type',
                                'bill_date', 'quantity', 'refill_date',
                                'price_rank', 'refill_date_rank', 'is_repeatable',
                                'is_chronic', 'recommendation_rank', 'last_bill_date',
                                'last_bill_quantity', 'drug_nob',
                                'drug_front_image_url', 'recency_flag']]

# Convert to date-month-year format
for i in ['bill_date', 'refill_date', 'last_bill_date']:
    data_export[i] = data_export[i].dt.strftime("%d-%b-%Y")

data_export.columns = [c.replace('_', '-') for c in data_export.columns]

logger.info("Data export length is - {}".format(len(data_export)))

data_export['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['created-by'] = 'etl-automation'
data_export['updated-by'] = 'etl-automation'

if isinstance(table_info1, type(None)):
    raise Exception(f"table: {table_name1} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name1} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name1}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=data_export[table_info1['column_name']], table_name=table_name1, db=rs_db,
                      schema=schema)


# Closing the DB Connection
rs_db.close_connection()