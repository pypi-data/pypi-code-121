# !pip install -U pandasql

"""
# Author - shubham.jangir@zeno.health, shubham.gupta@zeno.health
# Purpose - script with DSS write action for customer behaviour (transactional) segment
"""

import argparse
import sys

from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import gc
import pandasql as ps
from datetime import datetime as dt


# Normalisation (Standardization)
def standardize(x_var, mean_x, std_x):
    """
    Standardizing 'x' variable by it's mean and std provided
    """
    return (x_var - mean_x) / std_x


def cluster_predict(data_matrix, centroids):
    """
    Predict cluster number, from data matrix given
    And centroids given
    Just find nearest cluster for each data point
    """
    clusters = []
    for unit in data_matrix:
        distances = []
        for center in centroids:
            dist = np.sum((unit - center) ** 2)
            # print(dist)
            distances.append(dist)
        # print(distances)
        closest_centroid = np.argmin(distances)
        # print(closest_centroid)
        clusters.append(closest_centroid)
    return clusters


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default=["shubham.jangir@zeno.health", "shubham.gupta@zeno.health"], type=str,
                    required=False)
parser.add_argument('-pedp', '--period_end_d_plus1', default="0", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
period_end_d_plus1 = args.period_end_d_plus1

logger = get_logger()

logger.info(f"env: {env}")

schema = 'prod2-generico'
table_name = 'customer-behaviour-segment-test'

rs_db = DB()
rs_db.open_connection()

s3 = S3(bucket_name='datascience-manager')


def seek():
    """ get the data """
    pass


def run_fun(rs_db, s3):
    # write logic here
    pass


table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

logger.info(table_info)

# Segment calculation date can either be fetched from db manager or from run-date
try:
    period_end_d_plus1 = args.period_end_d_plus1
    period_end_d_plus1 = str(datetime.strptime(period_end_d_plus1, "%Y-%m-%d").date())
except ValueError:
    period_end_d_plus1 = datetime.today().strftime('%Y-%m-%d')

if isinstance(table_info, type(None)):
    print(f"table: {table_name} do not exist")
else:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" 
                        WHERE "segment-calculation-date" =  '{period_end_d_plus1}' 
                        '''
    logger.info(truncate_query)
    rs_db.execute(truncate_query)

read_schema = 'prod2-generico'

calc_year_month = datetime.strptime(period_end_d_plus1, "%Y-%m-%d").strftime("%Y_%b")

# Period start date
period_start_d_ts = datetime.strptime(period_end_d_plus1, '%Y-%m-%d') - timedelta(days=180)
period_start_d = period_start_d_ts.strftime('%Y-%m-%d')

# Period end date
period_end_d_ts = datetime.strptime(period_end_d_plus1, '%Y-%m-%d') - timedelta(days=1)
period_end_d = period_end_d_ts.strftime('%Y-%m-%d')

###################################################
# Patients and bills in last 6 months
###################################################
bills_q = f"""
     SELECT
        "id" AS "bill-id",
        "patient-id",
        DATE("created-at") AS "bill-date"
     FROM
        "{read_schema}"."bills-1"
     WHERE
        DATE("created-at") between '{period_start_d}' and '{period_end_d}'
        """
data_bill = rs_db.get_df(query=bills_q)

###################################################
# Bill-items in last 6months
###################################################

bi_q = f"""
    SELECT
        "bill-id",
        "inventory-id",
        "rate",
        "quantity"
    FROM
        "{read_schema}"."bill-items-1"
    WHERE
        DATE("created-at") between '{period_start_d}' and '{period_end_d}'
"""
data_billitem = rs_db.get_df(query=bi_q)

###################################################
# Inventory data
###################################################

inv_q = f"""
    SELECT
        "id" AS "inventory-id",
        "drug-id"
    FROM
        "{read_schema}"."inventory-1"
    GROUP BY
        "id",
        "drug-id"
"""
data_inventory = rs_db.get_df(query=inv_q)

###################################################
# Drugs
###################################################

drugs_q = f"""
    SELECT
        "id" AS "drug-id",
        "type" AS "drug-type",
        "category" AS "drug-category",
        "is-repeatable",
        "repeatability-index"
    FROM
        "{read_schema}"."drugs"
"""
data_drugs = rs_db.get_df(query=drugs_q)

# Merge these data-frames
data = data_bill.merge(data_billitem, how='inner', on=['bill-id'])

data = data.merge(data_inventory, how='left', on=['inventory-id'])

data = data.merge(data_drugs, how='left', on=['drug-id'])

# Delete temp data-frames
del [[data_bill, data_billitem,
      data_inventory, data_drugs]]
gc.collect()
data_bill = pd.DataFrame()
data_billitem = pd.DataFrame()
data_inventory = pd.DataFrame()
data_drugs = pd.DataFrame()

data['bill-date'] = pd.to_datetime(data['bill-date']).dt.date
data['rate'] = data['rate'].astype(float)

###################################################
# Bill level summary
###################################################
bill_summ_q = """
    SELECT
        `bill-id`,
        `patient-id`,
        `bill-date`,
        SUM(quantity) AS `total-quantity-bill`,
        SUM(rate*quantity) AS `total-spend-bill`,

        SUM(CASE
                WHEN `drug-type` IN ('ethical','high-value-ethical') THEN quantity
                ELSE 0
            END) AS `quantity-ethical`,
        SUM(CASE
                WHEN `drug-type` IN ('generic','high-value-generic') THEN quantity
                ELSE 0
            END) AS `quantity-generic`,
        SUM(CASE
                WHEN `drug-type` = 'surgical' THEN quantity
                ELSE 0
            END) AS `quantity-surgical`,
        SUM(CASE
                when `drug-type` = 'ayurvedic' THEN quantity
                ELSE 0
            END) AS `quantity-ayurvedic`,
        SUM(CASE
                WHEN `drug-type` = 'general' THEN quantity
                ELSE 0
            END) AS `quantity-general`,
        SUM(CASE
                WHEN `drug-type` = 'otc' THEN quantity
                ELSE 0
            END) AS `quantity-otc`,
        SUM(CASE
                WHEN `drug-category` = 'chronic' THEN quantity
                ELSE 0
            END) AS `quantity-chronic`
    FROM
        data
    GROUP BY
        `bill-id`,
        `patient-id`,
        `bill-date`
        """
bill_grp = ps.sqldf(bill_summ_q, locals())

###################################################
# Patient level grouping
###################################################
patient_summ_q = """
    SELECT
        `patient-id`,
        COUNT(distinct `bill-id`) AS `num-bills-period`,
        MIN(`bill-date`) AS `first-time-in-period`,
        MAX(`bill-date`) AS `last-time-in-period`,
        COUNT(DISTINCT `bill-date`) AS `num-days-visited`,
        SUM(`total-quantity-bill`) AS `total-quantity-period`,
        SUM(`total-spend-bill`) AS `total-spend-period`,
        SUM(`quantity-ethical`) AS `quantity-ethical`,
        SUM(`quantity-generic`) AS `quantity-generic`,
        SUM(`quantity-surgical`) AS `quantity-surgical`,
        SUM(`quantity-ayurvedic`) AS `quantity-ayurvedic`,
        SUM(`quantity-general`) AS `quantity-general`,
        SUM(`quantity-otc`) AS `quantity-otc`,
        SUM(`quantity-chronic`) AS `quantity-chronic`
    FROM
        bill_grp
    GROUP BY
        `patient-id`
        """
patient_level = ps.sqldf(patient_summ_q, locals())

###################################################
# Customer minimum bill date
###################################################

acq_q = f"""
    SELECT
        "patient-id",
        MIN(DATE("created-at")) AS "overall-min-bill-date"
    FROM
        "{read_schema}"."bills-1"
    WHERE
        DATE("created-at") <= '{period_end_d}'
    GROUP BY
        "patient-id"
        """
data_cc = rs_db.get_df(query=acq_q)

data_cc['overall-min-bill-date'] = pd.to_datetime(data_cc['overall-min-bill-date'])

###################################################
# HD customers
###################################################

hd_q = f"""
    SELECT
        "patient-id",
        MIN(DATE("created-at")) AS "min-hd-creation-date"
    FROM
        "{read_schema}"."patients-store-orders"
    WHERE
        "order-type" = 'delivery'
        and DATE("created-at") <= '{period_end_d}'
    GROUP BY
        "patient-id"  
"""
data_hd = rs_db.get_df(query=hd_q)

data_hd['min-hd-creation-date'] = pd.to_datetime(data_hd['min-hd-creation-date'])

# Append this info
data_merge = patient_level.merge(data_cc, how='left', on=['patient-id', 'patient-id'])
data_merge = data_merge.merge(data_hd, how='left', on=['patient-id', 'patient-id'])

# Change data-sets names
data = data_merge.copy()

for types_col in ['quantity-ethical', 'quantity-generic', 'quantity-surgical',
                  'quantity-ayurvedic', 'quantity-general', 'quantity-otc',
                  'quantity-chronic']:
    logger.info(types_col + "-pc")

###################################################
# Derived features
###################################################
data['spend-per-bill'] = np.round(data['total-spend-period'] / data['num-bills-period'], 2)
data['units-per-bill'] = np.round(data['total-quantity-period'] / data['num-bills-period'], 2)

data['total-interaction-period'] = (pd.to_datetime(data['last-time-in-period']).dt.normalize()
                                    - pd.to_datetime(data['first-time-in-period']).dt.normalize()
                                    ).dt.days
data['avg-purchase-interval'] = data['total-interaction-period'] / (data['num-days-visited'] - 1)

# Generico age is defined as last date in period, to date creation of customer
data['generico-age-customer'] = (pd.to_datetime(data['last-time-in-period']).dt.normalize()
                                 - pd.to_datetime(data['overall-min-bill-date']).dt.normalize()
                                 ).dt.days
data['recency-customer'] = (pd.to_datetime(period_end_d).normalize()
                            - pd.to_datetime(data['last-time-in-period']).dt.normalize()
                            ).dt.days

for types_col in ['quantity-ethical', 'quantity-generic', 'quantity-surgical',
                  'quantity-ayurvedic', 'quantity-general', 'quantity-otc',
                  'quantity-chronic']:
    data[types_col + "-pc"] = data[types_col] / data['total-quantity-period']

data['chronic-yes'] = np.where(data['quantity-chronic-pc'] > 0, 1, 0)

###################################################
# Remove outliers - custom defined as of now
###################################################
data_for_mean_std = data[data['units-per-bill'] <= 50]
data_for_mean_std = data_for_mean_std[data_for_mean_std['spend-per-bill'] <= 10000]
data_for_mean_std = data_for_mean_std[data_for_mean_std['num-days-visited'] <= 52]
data_for_mean_std = data_for_mean_std[data_for_mean_std['num-bills-period'] <= 52]

###################################################
# Clustering is done for old repeat customers only, so
###################################################
old_c_period_end_d_ts = datetime.strptime(period_end_d, '%Y-%m-%d') - timedelta(days=60)
old_c_period_end_d = old_c_period_end_d_ts.strftime('%Y-%m-%d')

data_for_mean_std = data_for_mean_std[
    (pd.to_datetime(data_for_mean_std['overall-min-bill-date']) <= old_c_period_end_d) &
    (data_for_mean_std['num-days-visited'] > 1)]

feature_names = ['num-days-visited', 'spend-per-bill', 'units-per-bill',
                 'total-interaction-period', 'avg-purchase-interval',
                 'generico-age-customer', 'recency-customer',
                 'quantity-ethical-pc', 'quantity-generic-pc',
                 'quantity-surgical-pc', 'quantity-ayurvedic-pc',
                 'quantity-general-pc', 'quantity-otc-pc', 'quantity-chronic-pc']

# feature_names
data_for_mean_std = data_for_mean_std[feature_names]

# Save mean and sd
mean_std_old_repeat_14f = pd.DataFrame(columns=['feature-name', 'mean', 'std'])
mean_std_old_repeat_14f['feature-name'] = data_for_mean_std.columns
for i in data_for_mean_std.columns:
    data_i_mean = data_for_mean_std[i].mean()
    data_i_std = data_for_mean_std[i].std()
    mean_std_old_repeat_14f.loc[mean_std_old_repeat_14f['feature-name'] == i,
                                'mean'] = data_i_mean
    mean_std_old_repeat_14f.loc[mean_std_old_repeat_14f['feature-name'] == i,
                                'std'] = data_i_std

###################################################
# Pre-processing starts here
###################################################
# Extra info appended
data['home-delivery-flag'] = np.where(data['min-hd-creation-date'] <= period_end_d,
                                      'yes', 'no')

# HD flag for summarization purpose
data['hd-yes'] = np.where(data['home-delivery-flag'] == 'yes',
                          1, 0)

data['newcomer-flag'] = np.where(pd.to_datetime(data['overall-min-bill-date']) > old_c_period_end_d,
                                 'newcomer', 'old-customer')
data['singletripper-flag'] = np.where(data['num-days-visited'] == 1,
                                      'singletripper', 'repeat-customer')

data_superset = data.copy()

data_old_repeat = data[
    (data['newcomer-flag'] == 'old-customer') &
    (data['singletripper-flag'] == 'repeat-customer')].copy()

# Save this as main data
data = data_old_repeat.copy()
data = data[feature_names]

# Import mean and std per feature
mean_std_features = mean_std_old_repeat_14f.copy()
mean_std_features = mean_std_features[['feature-name', 'mean', 'std']]

# Standardization
for i in data.columns:
    mean_i = list(mean_std_features.loc[mean_std_features['feature-name'] == i, 'mean'])[0]
    std_i = list(mean_std_features.loc[mean_std_features['feature-name'] == i, 'std'])[0]
    # Standardize
    data[i + "-norm"] = standardize(data[i], mean_i, std_i)

# Keep only Standardized columns for modelling
norm_cols = [i for i in data.columns if i.endswith("-norm")]
data = data[norm_cols]

# Read PCA Components
pca_components = pd.read_csv(s3.download_file_from_s3('data/Job-6/input/pca_repeat_14f_10pca_94pc_variance.csv'))
pca_components.drop(columns=['Unnamed: 0'], inplace=True)

# Convert dataset to matrix form
data_mat = np.array(data)
# Convert PCA components to matrix form
pca_mat = np.array(pca_components).T

# Multiply data matrix to PCA matrix, to transform into PCA features
data_to_pca = np.matmul(data_mat, pca_mat)

# KMeans
# centroids import
kmeans_centroids = pd.read_csv(s3.download_file_from_s3('data/Job-6/input/kmeans_centroids_repeat_6c_14f_10pca.csv'))
kmeans_centroids.drop(columns=['Unnamed: 0'], inplace=True)

# Convert centroids data-set to matrix form
kmeans_centroids_mat = np.array(kmeans_centroids)

###################################################
# Predict
###################################################
# Predict cluster number
cluster_no = cluster_predict(data_to_pca, kmeans_centroids_mat)

# Back to pandas data-set
data_final = data.copy()
data_final['cluster'] = cluster_no

data_merge = data_old_repeat.merge(data_final, how='inner', left_index=True,
                                   right_index=True)

# To summarize on
summary_cols_median = ['num-days-visited', 'spend-per-bill',
                       'units-per-bill', 'total-interaction-period',
                       'avg-purchase-interval', 'generico-age-customer',
                       'recency-customer', 'quantity-ethical-pc',
                       'quantity-generic-pc', 'quantity-chronic-pc',
                       'total-spend-period']  # for info purpose

summary_cols_mean = summary_cols_median + ['chronic-yes', 'hd-yes']

median_agg_dict = {'num-days-visited': ['count', 'median'],
                   'spend-per-bill': 'median',
                   'units-per-bill': 'median',
                   'total-interaction-period': 'median',
                   'avg-purchase-interval': 'median',
                   'generico-age-customer': 'median',
                   'recency-customer': 'median',
                   'quantity-ethical-pc': 'median',
                   'quantity-generic-pc': 'median',
                   'quantity-chronic-pc': 'median',
                   'total-spend-period': ['median', 'sum']}

# Make it re-usable later on
mean_agg_dict = {'num-days-visited': ['count', 'mean'],
                 'spend-per-bill': 'mean',
                 'units-per-bill': 'mean',
                 'total-interaction-period': 'mean',
                 'avg-purchase-interval': 'mean',
                 'generico-age-customer': 'mean',
                 'recency-customer': 'mean',
                 'quantity-ethical-pc': 'mean',
                 'quantity-generic-pc': 'mean',
                 'quantity-chronic-pc': 'mean',
                 'total-spend-period': ['mean', 'sum'],
                 'chronic-yes': 'mean',
                 'hd-yes': 'mean'}

###################################################
# Profile summary of clusters
###################################################
# Mean profile
profile_data = data_merge[summary_cols_mean + ['cluster']].groupby(
    ['cluster']).agg(mean_agg_dict)

length_base_cluster = len(data_merge)


def profile_extra_cols(profile_data_pass, length_base_pass):
    # Segment % share in data-set
    profile_data_pass['count-pc'] = np.round(
        profile_data_pass['num-days-visited']['count'] * 100 / length_base_pass)
    # Round all numbers
    profile_data_pass = np.round(profile_data_pass, 2)
    return profile_data_pass


profile_data = profile_extra_cols(profile_data, length_base_cluster)

# Median profile
profile_data_med = data_merge[summary_cols_median + ['cluster']].groupby(
    ['cluster']).agg(median_agg_dict)

profile_data_med = profile_extra_cols(profile_data_med, length_base_cluster)

# Save both profile summaries (mean and median) to .csv
s3.save_df_to_s3(df=profile_data,
                 file_name='Behaviour_Segment_Output/profile_data_{}.csv'.format(calc_year_month),
                 index=False)

s3.save_df_to_s3(df=profile_data_med,
                 file_name='Behaviour_Segment_Output/profile_data_med_{}.csv'.format(calc_year_month),
                 index=False)

###################################################
# Name clusters
###################################################
data_merge['cluster-name'] = data_merge['cluster'].map({0: 'generic_heavy',
                                                        1: 'regular',
                                                        3: 'super',
                                                        5: 'ethical_heavy',
                                                        2: 'other_type',
                                                        4: 'other_type'})

# Patient_id wise, for all
data_superset_merge = data_superset.merge(data_merge[['patient-id', 'cluster-name']],
                                          how='left',
                                          on=['patient-id', 'patient-id'])


def assign_extra_segment(data_pass):
    """
    Add segment names to segments not covered in clustering
    """
    if (data_pass['newcomer-flag'] == 'newcomer' and
            data_pass['singletripper-flag'] == 'repeat_customer'):
        return 'newcomer_repeat'
    elif (data_pass['newcomer-flag'] == 'newcomer' and
          data_pass['singletripper-flag'] == 'singletripper'):
        return 'newcomer-singletripper'
    elif (data_pass['newcomer-flag'] == 'old_customer' and
          data_pass['singletripper-flag'] == 'singletripper'):
        return 'singletripper'
    else:
        return data_pass['cluster-name']


# Assign segment names for extra segments
data_superset_merge['behaviour-segment'] = data_superset_merge.apply(
    lambda row: assign_extra_segment(row), axis=1)

###################################################
# Profiling all segment (Summary statistics for information)
###################################################
# Mean profile
profile_data_all = data_superset_merge[summary_cols_mean + ['behaviour-segment']].groupby(
    ['behaviour-segment']).agg(mean_agg_dict)

length_base_segment = len(data_superset_merge)

profile_data_all = profile_extra_cols(profile_data_all, length_base_segment)

# Median profile
profile_data_med_all = data_superset_merge[summary_cols_median + ['behaviour-segment']].groupby(
    ['behaviour-segment']).agg(median_agg_dict)

profile_data_med_all = profile_extra_cols(profile_data_med_all, length_base_segment)

# Save both profile summaries (mean and median) to .csv
profile_data_all = s3.save_df_to_s3(df=profile_data_all,
                                    file_name='Behaviour_Segment_Output/profile_data_all_{}.csv'.format(
                                        calc_year_month),
                                    index=False)

profile_data_med_all = s3.save_df_to_s3(df=profile_data_med_all,
                                        file_name='Behaviour_Segment_Output/profile_data_med_all_{}.csv'.format(
                                            calc_year_month),
                                        index=False)

# Save as .csv, the profile summary of each segment

for i in data_superset_merge['behaviour-segment'].unique():
    segment_i = data_superset_merge[data_superset_merge['behaviour-segment'] == i]
    logger.info(f'Length of {i} segment is {len(segment_i)}')
    # Summarize
    profile_i = segment_i[summary_cols_mean].describe()
    s3.save_df_to_s3(df=profile_i,
                     file_name='profile_{}.csv'.format(i),
                     index=False)

# Now this data is source of truth
data = data_superset_merge.copy()

###################################################
# Assign unique store to patient
###################################################

patient_store_q = f"""
    SELECT
        "patient-id",
        "store-id",
        COUNT(DISTINCT "id") AS "store-bills",
        SUM("net-payable") AS "store-spend"
    FROM
        "{read_schema}"."bills-1"
    WHERE
        DATEDIFF('days', '{period_end_d_plus1}', DATE("created-at")) between -180 and -1
    GROUP BY
        "patient-id",
        "store-id"
"""
data_store = rs_db.get_df(query=patient_store_q)

data_store['rank'] = data_store.sort_values(['store-bills', 'store-spend'],
                                            ascending=[False, False]
                                            ).groupby(['patient-id']).cumcount() + 1

patient_store = data_store[data_store['rank'] == 1][['patient-id', 'store-id']]

# Stores

stores_q = f"""
    SELECT
        "id" AS "store-id",
        "name" AS "store-name"
    FROM 
        "{read_schema}"."stores"
        """
stores = rs_db.get_df(query=stores_q)

patient_store = patient_store.merge(stores, how='inner',
                                    on=['store-id', 'store-id'])

data = data.merge(patient_store, how='left', left_on=['patient-id'],
                  right_on=['patient-id'])

# Export data
keep_cols = ['patient-id', 'num-bills-period', 'total-spend-period',
             'spend-per-bill', 'units-per-bill',
             'generico-age-customer', 'recency-customer', 'quantity-ethical-pc',
             'quantity-generic-pc', 'quantity-chronic-pc', 'chronic-yes', 'hd-yes',
             'newcomer-flag', 'singletripper-flag', 'behaviour-segment',
             'store-id', 'store-name']

write_data = data[keep_cols]

# Round some numbers
for i in ['quantity-ethical-pc', 'quantity-generic-pc', 'quantity-chronic-pc']:
    write_data[i] = np.round(write_data[i], 2)
for i in ['total-spend-period', 'spend-per-bill']:
    write_data[i] = np.round(write_data[i], 2)

write_data = write_data.rename(columns={'units-per-bill': 'quantity-per-bill'})

# Make some columns for logging purpose
runtime_date = datetime.today().strftime('%Y-%m-%d')
runtime_month = datetime.today().strftime('%Y-%m')

write_data['segment-calculation-date'] = period_end_d_plus1
write_data['upload-date'] = runtime_date
write_data['base_list-identifier'] = runtime_month

# etl
write_data['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
write_data['created-by'] = 'etl-automation'
write_data['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
write_data['updated-by'] = 'etl-automation'

s3.save_df_to_s3(df=write_data,
                 file_name='Behaviour_Segment_Output/behaviour_segment_data_{}.csv'.format(calc_year_month),
                 index=False)

###################################################
# Append this updated_churn to Redshift DB
###################################################

s3.write_df_to_db(df=write_data[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

email = Email()

subject = "Task Status behaviour segment calculation"
mail_body = "Behaviour segments upload succeeded"

file_uris = [profile_data_all, profile_data_med_all]

email.send_email_file(subject=subject,
                      mail_body=mail_body,
                      to_emails=email_to, file_uris=file_uris, file_paths=[])
