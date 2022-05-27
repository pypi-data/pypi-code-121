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
from datetime import timedelta
from dateutil.tz import gettz
import gc
from zeno_etl_libs.django.api import Sql

import typing
from functools import reduce
from sklearn.preprocessing import StandardScaler

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-sd', '--datem', default='', type=str, required=False)

parser.add_argument('-my', '--sqlwrite', default='yes', type=str, required=False)

args, unknown = parser.parse_known_args()

env = args.env
datem = args.datem
sqlwrite = args.sqlwrite
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name = 'drug-grades'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

if datem == '':
    date1 = datetime.date.today().strftime('%Y-%m-%d')
    logger.info('Entry taken from params:{}'.format(str(date1)))
else:
    date1 = datem
    logger.info('Selecting the default date as the job run date: {}'.format(str(date1)))

q_aa = f"""
        select
            "bill-id",
            "patient-id" ,
            "store-id" ,
            "store-name" as "name",
            "drug-id" ,
            "drug-name" ,
            "type" ,
            "created-date" as "created-at" ,
            NVL(sum(case when "bill-flag" = 'gross' then quantity end),
            0) as "sold-quantity",
            NVL(sum(case when "bill-flag" = 'return' then quantity end),
            0) as "returned-quantity",
            sum("net-quantity") as "quantity",
            sum(rate) as "rate"
        from
            "prod2-generico"."sales"
        where
            datediff('day','{date1}',
            "created-date") between -180 and -1
        group by
            "bill-id",
            "patient-id" ,
            "store-id" ,
            "store-name",
            "drug-id" ,
            "drug-name" ,
            "type" ,
            "created-date"
        having
            sum("net-quantity")>0 
"""

df_aa = rs_db.get_df(q_aa)
df_aa.columns = [c.replace('-', '_') for c in df_aa.columns]

logger.info('Shape of data: {}'.format(str(df_aa.shape)))

df_aa['quantity'].fillna(0,inplace=True)
df_aa['rate'].fillna(0,inplace=True)

df_aa['value'] = df_aa['rate'] * df_aa['quantity']

# =============================================================================
# Store opened at
# =============================================================================

q_bb = f"""
        SELECT
            "id",
            datediff('day' ,
            "opened-at",
            '{date1}') as "age"
        FROM
            "prod2-generico"."stores"
        WHERE
            datediff('day' ,
            "opened-at",
            '{date1}' ) < 180
"""

df_bb = rs_db.get_df(q_bb)
df_bb.columns = [c.replace('-', '_') for c in df_bb.columns]

logger.info('Shape of stores data: {}'.format(str(df_bb.shape)))

def store_age(df_bb):
    if df_bb['age'] >= 90:
        return '3-6 month'
    else:
        return '1-3 month'

df_bb['age1'] = df_bb.apply(lambda x: store_age(x), axis=1)

# =============================================================================
# quantity sold
# =============================================================================

df_qty = df_aa.groupby(['drug_id', 'store_id'])[['quantity']].sum().reset_index()
df_qty1 = df_aa.groupby(['drug_id'])[['quantity']].sum().reset_index()

# =============================================================================
# revenue
# =============================================================================

df_revenue = df_aa.groupby(['drug_id', 'store_id'])[['value']].sum().reset_index()
df_revenue1 = df_aa.groupby(['drug_id'])[['value']].sum().reset_index()
# =============================================================================
# no. of bills
# =============================================================================
df_bills = df_aa.groupby(['drug_id', 'store_id'])[['bill_id']].nunique().reset_index()
df_bills1 = df_aa.groupby(['drug_id'])[['bill_id']].nunique().reset_index()
# =============================================================================
# no. of consumers
# =============================================================================
df_consumers = df_aa.groupby(['drug_id', 'store_id'])[['patient_id']].nunique().reset_index()
df_consumers1 = df_aa.groupby(['drug_id'])[['patient_id']].nunique().reset_index()

df_aa['created_at'] = pd.to_datetime(df_aa['created_at'])
# =============================================================================
# no. of days sold
# =============================================================================

df_aa['days'] = df_aa['created_at'].dt.date
df_days = df_aa.groupby(['drug_id', 'store_id'])[['days']].nunique().reset_index()
df_days1 = df_aa.groupby(['drug_id'])[['days']].nunique().reset_index()

# =============================================================================
# recency (last sold)
# =============================================================================

days = timedelta(1)
period_end_d = pd.to_datetime(date1) - days

df_recency = df_aa.groupby(['drug_id', 'store_id'])[['created_at']].max().reset_index()
df_recency1 = df_aa.groupby(['drug_id'])[['created_at']].max().reset_index()
df_recency['recency'] = (pd.to_datetime(period_end_d) - df_recency['created_at']).dt.days

df_recency1['recency'] = (pd.to_datetime(period_end_d) - df_recency1['created_at']).dt.days
# =============================================================================
# merge all features
# =============================================================================

meg = [df_qty, df_revenue, df_bills, df_consumers, df_days, df_recency]
df_features = reduce(lambda left, right: pd.merge(left, right, on=[
    'drug_id', 'store_id'], how='outer'), meg)
del (df_features['created_at'])

meg1 = [df_qty1, df_revenue1, df_bills1, df_consumers1, df_days1, df_recency1]
df_features1 = reduce(lambda left, right: pd.merge(left, right, on=[
    'drug_id'], how='outer'), meg1)
del (df_features1['created_at'])

df_features = df_features1.append(df_features)

df_features['store_id'] = df_features['store_id'].fillna(999)

df_features = df_features.reset_index().drop('index', axis=1)

# =============================================================================
# creating standard scaler store wise
# =============================================================================

temp_normalise = df_features[['store_id', 'quantity', 'value', 'bill_id', 'patient_id', 'days', 'recency']]

class SklearnWrapper:
    def __init__(self, transform: typing.Callable):
        self.transform = transform

    def __call__(self, df):
        transformed = self.transform.fit_transform(df.values)
        return pd.DataFrame(transformed, columns=df.columns, index=df.index)

# This one will apply any sklearn transform you pass into it to a group.

df_rescaled = (
    temp_normalise.groupby('store_id')
        .apply(SklearnWrapper(StandardScaler()))
        .drop('store_id', axis=1)
)

temp2_normalise = df_rescaled

# =============================================================================
# importing pca_components and appling to scaled data set.
# =============================================================================
pca_file_name= 'drug_grades/pca_components.csv'
pca_file_path= s3.download_file_from_s3(file_name=pca_file_name)

pca_components=pd.read_csv(pca_file_path,delimiter=',')


# =============================================================================
#  creating Euclidean Distance Caculator and applyin to nearest cluster
# =============================================================================
cluster_file_name= 'drug_grades/cluster_centers_1.csv'
pca_file_path= s3.download_file_from_s3(file_name=cluster_file_name)

cluster_centers_set=pd.read_csv(pca_file_path,delimiter=',')

cluster_centers_set = np.array(cluster_centers_set)

# Euclidean Distance Caculator
def dist(a, b, ax=1):
    return np.linalg.norm(a - b, axis=ax)

clusters = []

test = np.dot(np.array(temp2_normalise), (np.array(pca_components).T))

for i in range(len(test)):
    distances = dist(np.array(test[i]), (cluster_centers_set))
    cluster = np.argmin(distances)
    clusters.append(cluster)

cluster_df = pd.DataFrame(clusters)
cluster_df.columns = ['final_cluster']

# =============================================================================
# Summary pivot 1
# =============================================================================

test_df = pd.DataFrame(test)
cluster_lvl_1 = pd.merge(test_df, cluster_df,
                         right_index=True, left_index=True)

cluster_lvl1_output = pd.merge(cluster_lvl_1, df_features, how='inner',
                               left_index=True, right_index=True)

cluster_lvl1_output_pivot = cluster_lvl1_output.groupby(['final_cluster', 'store_id'],
                                                        as_index=False).agg({'drug_id': ['count'],
                                                                             'value': ['sum'],
                                                                             'bill_id': ['mean'],
                                                                             'patient_id': ['mean'],
                                                                             'days': ['mean'],
                                                                             'recency': ['mean']}).reset_index(
    drop=True)
cluster_lvl1_output_pivot.columns = ['_'.join(x) for x in
                                     cluster_lvl1_output_pivot.columns.ravel()]


cluster_lvl1_output_pivot_name = 'drug_grades/cluster_lv1_output.csv'

# Uploading File to S3
s3.save_df_to_s3(df=cluster_lvl1_output_pivot, file_name=cluster_lvl1_output_pivot_name)


# =============================================================================
# # 2nd level
# =============================================================================

# =============================================================================
# Further split of large cluster
# =============================================================================

further_split_lvl2 = cluster_lvl1_output[cluster_lvl1_output['final_cluster'] == 0]
# change features here if needed
further_split_lvl2 = pd.DataFrame(further_split_lvl2[[0, 1, 2, 3]])

further_split_lvl2_mat = np.array(further_split_lvl2)

cluster2_file_name= 'drug_grades/cluster_centers_2.csv'
pca_file_path= s3.download_file_from_s3(file_name=cluster2_file_name)

cluster_centers_set2=pd.read_csv(pca_file_path,delimiter=',')

cluster_centers_set2 = np.array(cluster_centers_set2)

clusters_lvl2 = []

for i in range(len(further_split_lvl2)):
    distances = dist((further_split_lvl2_mat[i]), (cluster_centers_set2))
    clusterlvl2 = np.argmin(distances)
    clusters_lvl2.append(clusterlvl2)

further_split_lvl2_df = pd.DataFrame(further_split_lvl2)

further_split_lvl2_df['final_cluster_lvl2'] = clusters_lvl2

# =============================================================================
# Summary pivot 2
# =============================================================================

cluster_lvl2_output = pd.merge(cluster_lvl1_output, further_split_lvl2_df[['final_cluster_lvl2']],
                               how='inner',
                               left_index=True, right_index=True)

cluster_lvl2_output_pivot = cluster_lvl2_output.groupby(['final_cluster_lvl2', 'store_id'],
                                                        as_index=False).agg({'drug_id': ['count'],
                                                                             'value': ['sum'],
                                                                             'bill_id': ['mean'],
                                                                             'patient_id': ['mean'],
                                                                             'days': ['mean'],
                                                                             'recency': ['mean']}).reset_index(
    drop=True)

cluster_lvl2_output_pivot.columns = ['_'.join(x) for x in
                                     cluster_lvl2_output_pivot.columns.ravel()]


cluster_lvl2_output_pivot_name = 'drug_grades/cluster_lvl2_output.csv'

# Uploading File to S3
s3.save_df_to_s3(df=cluster_lvl2_output_pivot, file_name=cluster_lvl2_output_pivot_name)


# =============================================================================
# Final cluster
# =============================================================================

cluster_file = cluster_lvl1_output[cluster_lvl1_output['final_cluster'] != 0]

final_cluster_file = cluster_file.append(cluster_lvl2_output)

final_cluster_file['cluster'] = final_cluster_file['final_cluster'
                                ].astype(str) + '_' + final_cluster_file['final_cluster_lvl2'].astype(str)

final_output_pivot = final_cluster_file.groupby(['cluster', 'store_id'],
                                                as_index=False).agg({'drug_id': ['count'],
                                                                     'value': ['sum'],
                                                                     'bill_id': ['mean'],
                                                                     'patient_id': ['mean'],
                                                                     'days': ['mean'],
                                                                     'recency': ['mean']}).reset_index(drop=True)

final_output_pivot.columns = ['_'.join(x) for x in
                              final_output_pivot.columns.ravel()]

final_output_pivot['drug%'] = final_output_pivot['drug_id_count'
                              ] / final_output_pivot['drug_id_count'].sum()

final_output_pivot['spend%'] = final_output_pivot['value_sum'
                               ] / final_output_pivot['value_sum'].sum()

final_output_pivot['drug%']=final_output_pivot['drug%'].astype('float64')
final_output_pivot['spend%']=final_output_pivot['spend%'].astype('float64')

final_output_pivot['factor'] = final_output_pivot['spend%'] / final_output_pivot['drug%']

# =============================================================================
# cluster allocation
# =============================================================================

new_store = df_bb['id'].values

new_store1 = df_bb['id'][df_bb['age1'] == '3-6 month'].values

new_store2 = df_bb['id'][df_bb['age1'] == '1-3 month'].values

new_store1_cluster = final_cluster_file[final_cluster_file.store_id.isin(new_store1)]

new_store2_cluster = final_cluster_file[final_cluster_file.store_id.isin(new_store2)]

Enterprise_cluster = final_cluster_file[final_cluster_file.store_id == 999]

old_stores_cluster = final_cluster_file[(~final_cluster_file.store_id.isin(new_store)) &
                                        (final_cluster_file.store_id != 999)]

new_store1_cluster.drop(['cluster'], axis=1, inplace=True)

new_store2_cluster.drop(['cluster'], axis=1, inplace=True)

new_store1_predict = pd.merge(new_store1_cluster, Enterprise_cluster[['drug_id', 'cluster']], how='left',
                              left_on='drug_id', right_on='drug_id')

for i in range(len(new_store2)):
    Enterprise_temp = Enterprise_cluster.copy()
    Enterprise_temp['new_store_id'] = new_store2[i]
    if i == 0:
        new_store2_predict_data = Enterprise_temp
    else:
        new_store2_predict_data = new_store2_predict_data.append(Enterprise_temp)

new_store2_predict = new_store2_predict_data

del new_store2_predict['store_id']

new_store2_predict = new_store2_predict.rename({'new_store_id': 'store_id'}, axis=1)

cluster_all = new_store1_predict.append(new_store2_predict)

cluster_all = cluster_all.append(Enterprise_cluster)

cluster_all = cluster_all.append(old_stores_cluster)

# =============================================================================
# Summary report
# =============================================================================

cluster_all_pivote = cluster_all.groupby(['cluster', 'store_id'],
                                         as_index=False).agg({'drug_id': ['count'],
                                                              'value': ['sum'],
                                                              'bill_id': ['mean'],
                                                              'patient_id': ['mean'],
                                                              'days': ['mean'],
                                                              'recency': ['mean']}).reset_index(drop=True)

cluster_all_pivote.columns = ['_'.join(x) for x in
                              cluster_all_pivote.columns.ravel()]

cluster_all_pivote['drug%'] = cluster_all_pivote['drug_id_count'
                              ] / cluster_all_pivote['drug_id_count'].sum()

cluster_all_pivote['spend%'] = cluster_all_pivote['value_sum'
                               ] / cluster_all_pivote['value_sum'].sum()

cluster_all_pivote['drug%'] = cluster_all_pivote['drug%'].astype('float64')
cluster_all_pivote['spend%'] = cluster_all_pivote['spend%'].astype('float64')

cluster_all_pivote['factor'] = cluster_all_pivote['spend%'
                               ] / cluster_all_pivote['drug%']


cluster_all_pivote_name = 'drug_grades/cluster_all_pivot.csv'

# Uploading File to S3
s3.save_df_to_s3(df=cluster_all_pivote, file_name=cluster_all_pivote_name)


# =============================================================================
# Assigning Cluster
# =============================================================================

def assign_cluster(cluster_all):
    if cluster_all['cluster'] == '1_nan':
        return 'A1'
    elif cluster_all['cluster'] == '2_nan':
        return 'A1'
    elif cluster_all['cluster'] == '4_nan':
        return 'A2'
    elif cluster_all['cluster'] == '0_2.0':
        return 'B'
    elif cluster_all['cluster'] == '3_nan':
        return 'D'
    elif cluster_all['cluster'] == '0_0.0':
        return 'C'
    elif cluster_all['cluster'] == '0_1.0':
        return 'C'
    else:
        return cluster_all['cluster']

cluster_all['grade'] = cluster_all.apply(lambda row: assign_cluster(row), axis=1)


cluster_all_name = 'drug_grades/cluster_all.csv'

# Uploading File to S3
s3.save_df_to_s3(df=cluster_all, file_name=cluster_all_name)

cluster_all_pivote1 = cluster_all.groupby(['grade', 'store_id'],
                                          as_index=False).agg({'drug_id': ['count'],
                                                               'value': ['sum'],
                                                               'bill_id': ['mean'],
                                                               'patient_id': ['mean'],
                                                               'days': ['mean'],
                                                               'recency': ['mean']}).reset_index(drop=True)

cluster_all_pivote1.columns = ['_'.join(x) for x in
                               cluster_all_pivote1.columns.ravel()]

cluster_all_pivote1['drug%'] = cluster_all_pivote1['drug_id_count'
                               ] / cluster_all_pivote1['drug_id_count'].sum()

cluster_all_pivote1['spend%'] = cluster_all_pivote1['value_sum'
                                ] / cluster_all_pivote1['value_sum'].sum()

cluster_all_pivote1['drug%'] = cluster_all_pivote1['drug%'].astype('float64')

cluster_all_pivote1['spend%'] = cluster_all_pivote1['spend%'].astype('float64')

cluster_all_pivote1['factor'] = cluster_all_pivote1['spend%'
                                ] / cluster_all_pivote1['drug%']



cluster_all_pivote1_name = 'drug_grades/cluster_all_pivot1.csv'

# Uploading File to S3
s3.save_df_to_s3(df=cluster_all_pivote1, file_name=cluster_all_pivote1_name)


final_data = cluster_all[['store_id', 'drug_id', 'grade']]
final_data['calculation_date'] = date1

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()


final_data.columns = [c.replace('_', '-') for c in final_data.columns]
final_data['created-at'] = datetime.datetime.now()
final_data['store-id'] = final_data['store-id'].astype(int)
final_data['drug-id'] = final_data['drug-id'].astype(int)

s3.write_df_to_db(df=final_data[table_info['column_name']], table_name=table_name, db=rs_db_write,
                  schema=schema)

'''getting current grades and replacing them with new if changed'''
new_drug_entries = pd.DataFrame()
missed_entries = pd.DataFrame()
for store_id in final_data['store-id'].unique():
    if sqlwrite == 'yes':
        if store_id != 999:

            current_grade_query = f'''
                SELECT
                    id,
                    "store-id",
                    "drug-id",
                    "drug-grade"
                FROM "prod2-generico"."drug-order-info-data"
                WHERE "store-id" = {store_id}
            '''

            current_grade = rs_db.get_df(current_grade_query)
            current_grade.columns = [c.replace('-', '_') for c in current_grade.columns]

            current_grade.columns = list(map(
                lambda s: str.replace(s, '-', '_'),
                list(current_grade.columns.values)
            ))

            final_data_store = final_data.loc[
                final_data['store-id'] == store_id,
                ['store-id', 'drug-id', 'grade']]
            final_data_store.columns = [c.replace('-', '_') for c in final_data_store.columns]
            grade_joined = current_grade.merge(
                final_data_store, on=['store_id', 'drug_id'], how='outer')
            grade_joined.loc[grade_joined['grade'].isna(), 'grade'] = 'NA'
            new_drug_entries = new_drug_entries.append(
                grade_joined[grade_joined['id'].isna()])
            grade_joined = grade_joined[~grade_joined['id'].isna()]

            grade_joined['change_flag'] = np.where(
                grade_joined['drug_grade'] == grade_joined['grade'],
                'same', 'changed')

            logger.info('Store ' + str(store_id))
            logger.info('Total grades calculated' + str(final_data_store.shape[0]))
            logger.info('Grades changed' + str(grade_joined[
                                                   grade_joined['change_flag'] == 'changed'].shape[0]))

            grades_to_change = grade_joined.loc[
                grade_joined['change_flag'] == 'changed',
                ['id', 'store_id', 'drug_id', 'grade']]
            grades_to_change.columns = ['id', 'store_id', 'drug_id', 'drug_grade']
            data_to_be_updated_list = list(
                grades_to_change[['id', 'drug_grade']].apply(dict, axis=1))

            sql = Sql()

            sql.update(
                {'table': 'DrugOrderInfoData',
                 'data_to_be_updated': data_to_be_updated_list}, logger
            )

            update_test_query = f'''
                SELECT
                    "store-id",
                    "drug-id",
                    "drug-grade"
                FROM "prod2-generico"."drug-order-info-data"
                WHERE "store-id" = {store_id}
                    and "grade-updated-at" >= CURRENT_TIMESTAMP - INTERVAL '10 MINUTE'
                    and "grade-updated-at" < CURRENT_TIMESTAMP
            '''

            update_test = rs_db.get_df(update_test_query)
            update_test.columns = [c.replace('-', '_') for c in update_test.columns]

            update_test.columns = list(map(
                lambda s: str.replace(s, '-', '_'),
                list(update_test.columns.values)
            ))
            update_test = grades_to_change.merge(
                update_test, how='left', on=['store_id', 'drug_id'],
                suffixes=('', '_updated'))
            mismatch = update_test[
                update_test['drug_grade'] != update_test['drug_grade_updated']]
            missed_entries = missed_entries.append(mismatch)
            logger.info('For store ' + str(store_id) + 'update mismatch count'
                        + str(mismatch.shape[0]))


new_drug_entries_name = 'drug_grades/new_drug_entries.csv'

# Uploading File to S3
s3.save_df_to_s3(df=new_drug_entries, file_name=new_drug_entries_name)


missed_entries_name = 'drug_grades/missed_entries.csv'

# Uploading File to S3
s3.save_df_to_s3(df=missed_entries, file_name=missed_entries_name)

rs_db.close_connection()

rs_db_write.close_connection()



