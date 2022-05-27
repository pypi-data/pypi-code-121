"""main wrapper to build selling and cumulative probability matrix to be used
by ipc V3 corrections"""

import os
import sys
import argparse

import pandas as pd
import numpy as np
import datetime as dt
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email


def main(debug_mode, db_read, db_write, read_schema, write_schema, s3, logger):

    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'

    try:
        # previous day taken to remove the day on which code is run.
        # start_date is the date from which analysis begins. start_date is previous day - 28*4 days
        # store cutoff date put as same as that of start_date
        # period between (previous_day) & (previous_day - 28*4days)

        previous_day = (dt.date.today() - pd.DateOffset(days=1))  # start analysis from the previous day.
        start_date = pd.to_datetime(
            (previous_day - pd.DateOffset(days=4 * 28)).strftime('%Y-%m-%d'))
        store_date_cutoff = pd.to_datetime(
            (previous_day - pd.DateOffset(days=4 * 28)).strftime('%Y-%m-%d'))

        logger.info("Corrections ran for dates {0} to {1}".format(
                                        start_date.strftime('%Y-%m-%d'),
                                        previous_day.strftime('%Y-%m-%d')))

        # remove stores opened before start_date (i.e. four months from previous_day).
        Q_STORE = """
                select id as "store-id", "opened-at" from "{read_schema}".stores
                where "opened-at" <= '{store_date_cutoff}'
                and "opened-at" != '0101-01-01 00:00:00' 
                """.format(read_schema=read_schema,
                           store_date_cutoff=store_date_cutoff)

        df_stores = pull_data(Q_STORE, db_read)

        store_filter = tuple(df_stores['store_id'].to_list())

        logger.info("Total stores considered for corrections: {0} ".format(len(store_filter)))

        # pull sales data with store filter between start_date and previous day.
        Q_REF = """
                select "store-id" , "drug-id" 
                from "{read_schema}".sales
                where date("created-at") >= date('{start_date}')
                and date("created-at") <= date('{end_date}')
                and "store-id" in {store_filter}
                group by "store-id" , "drug-id"  
                """.format(read_schema=read_schema,
                           start_date=start_date,
                           end_date=previous_day,
                           store_filter=store_filter)

        df_ref = pull_data(Q_REF, db_read)

        logger.info("Calculating probability matrix for store-drugs")

        # matrix_111 contains list of 111 drugs in current bucket
        matrix, matrix_111, probability_matrix_1, probability_matrix_2 = calculate_probabilities(df_ref, db_read, read_schema)

        probability_matrix_1['historical_flag_ma_less_than_2'] = 1
        probability_matrix_2['historical_flag_ma_less_than_2'] = 0

        probability_matrix = pd.concat([probability_matrix_1, probability_matrix_2])

        # formatting and adding required fields for RS-DB write
        matrix.columns = [c.replace('_', '-') for c in matrix.columns]
        matrix_111.columns = [c.replace('_', '-') for c in matrix_111.columns]
        probability_matrix.columns = [c.replace('_', '-') for c in probability_matrix.columns]

        logger.info("Formatting table for RS-DB write")
        matrix['created-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        matrix['created-by'] = 'etl-automation'
        matrix['updated-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        matrix['updated-by'] = 'etl-automation'

        matrix_111['created-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        matrix_111['created-by'] = 'etl-automation'
        matrix_111['updated-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        matrix_111['updated-by'] = 'etl-automation'

        probability_matrix['created-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        probability_matrix['created-by'] = 'etl-automation'
        probability_matrix['updated-at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        probability_matrix['updated-by'] = 'etl-automation'

        if debug_mode == 'N':
            logger.info(f"Truncating ipc-corrections-rest-cases in {write_schema}")
            truncate_query = f"""
                            truncate table "{write_schema}"."ipc-corrections-rest-cases"
                            """
            db_write.execute(truncate_query)

            logger.info(f"Truncating ipc-corrections-111-cases in {write_schema}")
            truncate_query = f"""
                            truncate table "{write_schema}"."ipc-corrections-111-cases"
                            """
            db_write.execute(truncate_query)

            logger.info(f"Truncating ipc-corrections-probability-matrix in {write_schema}")
            truncate_query = f"""
                            truncate table "{write_schema}"."ipc-corrections-probability-matrix"
                            """
            db_write.execute(truncate_query)

            logger.info("Writing table to RS-DB")
            logger.info("Writing to table: ipc-corrections-rest-cases")
            s3.write_df_to_db(df=matrix,
                              table_name='ipc-corrections-rest-cases',
                              db=db_write, schema=write_schema)
            logger.info("Writing to table: ipc-corrections-111-cases")
            s3.write_df_to_db(df=matrix_111,
                              table_name='ipc-corrections-111-cases',
                              db=db_write, schema=write_schema)
            logger.info("Writing to table: ipc-corrections-probability-matrix")
            s3.write_df_to_db(df=probability_matrix,
                              table_name='ipc-corrections-probability-matrix',
                              db=db_write, schema=write_schema)
            logger.info("Writing table to RS-DB completed!")

        else:
            logger.info("Writing to RS-DB skipped")

        status = 'Success'

    except Exception as error:
        logger.exception(error)

    return status


# ======================= SQL QUERIES =======================

Q_REPEATABLE = """
        SELECT id AS "drug-id",
        CASE 
            WHEN (category ='chronic' AND "repeatability-index">=40)
            OR ("repeatability-index">=80) THEN 1 ELSE 0 END AS "is-repeatable"
        FROM "{schema}".drugs 
        """

Q_CURRENT_INV_AND_PTR = """
        SELECT "drug-id", "store-id", avg(ptr) AS "avg-ptr", 
        SUM("locked-quantity"+quantity+"locked-for-audit"+"locked-for-transfer" 
           +"locked-for-check"+"locked-for-return") AS "current-inventory" 
        FROM "{schema}"."inventory-1" 
        GROUP BY "store-id", "drug-id" 
        """

Q_SOLD_QUANTITY = """
        select "store-id", "drug-id", date("created-at") as "created-at", 
        sum(quantity) as "total-sales-quantity"
        from "{schema}".sales
        where quantity > 0
        and date("created-at") >= date('{start_date}') and date("created-at") <= date('{end_date}') 
        group by "store-id", "drug-id", "created-at"
        """

Q_MAX = """
        SELECT "store-id", "drug-id", "max" FROM "{schema}"."drug-order-info"
        """

Q_COMPOSITION = """
        SELECT id AS "drug-id", composition FROM "{schema}".drugs
        """

# ======================= HELPER FUNCTIONS =======================

def pull_data(query, db):
    df = db.get_df(query)
    df.columns = [c.replace('-', '_') for c in df.columns]

    return df


def divide_time(df, start_date, end_date):
    ''' Adds 28 days bucket label to df for later pivot table division.
    quantity0 for last month, quantity3 for the oldest month.'''

    df['created_at'] = pd.to_datetime(df['created_at'])

    df = df[df['created_at'] >= start_date]

    df['divide_time'] = 999 # a proxy for removing possible errors
    for i in range(4):
        date1 = end_date - pd.DateOffset(days=i * 28)
        date2 = end_date - pd.DateOffset(days=(i + 1) * 28)
        df['divide_time'] = np.where(((df['created_at'] <= date1)
                                      & (df['created_at'] > date2)), 'quantity' + str(i),
                                     df['divide_time'])

    df = df[df['divide_time'] != '999'] #possible errors removed.
    return df


def make_flags(df, db, schema, metric):
    ''' Add quantity0, quantity1, quantity2, quantity3 flags. '''

    end_date = dt.date.today() - pd.DateOffset(days=1)

    start_date = (end_date - pd.DateOffset(days=(4 * 28))).strftime('%Y-%m-%d')

    end_date = pd.to_datetime(end_date)
    start_date = pd.to_datetime(start_date)

    q = Q_SOLD_QUANTITY.format(schema=schema,
                               start_date=start_date,
                               end_date=end_date)
    df_flags = pull_data(q, db)

    flags = divide_time(df_flags, start_date=start_date, end_date=end_date)

    flags = flags.pivot_table(metric, index=['store_id', 'drug_id'],
                              columns='divide_time', aggfunc=np.sum).fillna(0)

    flags = flags.reset_index()

    df = pd.merge(df, flags, how='left', on=['store_id', 'drug_id'],
                  validate='one_to_one').fillna(0)

    return df


def append_binary_tags(df, buckets):
    ''' convert quantity sold/comp sold into binary tags'''

    for x in buckets:
        df[x + '_b'] = np.where(df[x] > 0, 1, 0)

    return df


def output_comps(df, comp_buckets, i):
    '''Looks at number of times substitute composition is sold in the four buckets
    -1 is appended for drugs for which composition that don't exist.'''


    df_comp = df.copy()

    df_comp['total_months_comp_sold_'+str(i)] = 0

    for x in comp_buckets:
        df_comp['total_months_comp_sold_'+str(i)] = df_comp['total_months_comp_sold_'+str(i)] + df_comp[x]

    print('columns used to create total_comp_sold are:', comp_buckets)

    df_comp = df_comp[['store_id', 'composition', 'total_months_comp_sold_'+str(i)]]

    df_comp.loc[((df_comp['composition'] == 'Doesnt exist') | (df_comp['composition'] == '') | (
                df_comp['composition'] == '(mg)')), 'total_months_comp_sold_'+str(i)] = -1

    df_comp['total_months_comp_sold_'+str(i)] = df_comp['total_months_comp_sold_'+str(i)].astype(int)

    return df_comp


def add_features(df, db, schema):
    ''' add features like repeatable(1 or 0), composition sold (-1,0,1,2,3), current_inv and ptr, max values '''

    # merge all features here

    # add max values here
    df_max = pull_data(Q_MAX.format(schema=schema), db)[['store_id', 'drug_id', 'max']]

    df = pd.merge(df, df_max, on=['store_id', 'drug_id'], how='left', validate='one_to_one')

    df = df.dropna()  # removing drugs with no entry for max values.

    # add average ptr and current inventory here
    df_current_inv_ptr = pull_data(Q_CURRENT_INV_AND_PTR.format(schema=schema),
                                   db)[['store_id', 'drug_id', 'avg_ptr', 'current_inventory']]

    df_current_inv_ptr['avg_ptr'] = df_current_inv_ptr['avg_ptr'].astype(float)

    df = pd.merge(df, df_current_inv_ptr, on=['store_id', 'drug_id'],
                  how='left', validate='one_to_one')

    df = df.fillna(0) #fixing na values for ptr and current inventory

    # merge repeatability here
    df_repeatable = pull_data(Q_REPEATABLE.format(schema=schema), db)

    df = pd.merge(df, df_repeatable, on=['drug_id'], how='left', validate='many_to_one')

    # merge composition here. two entries for compostion are made.
    # 1 is for total historical composition sold. 2 is for total current composition sold.
    df_composition = pull_data(Q_COMPOSITION.format(schema=schema), db)

    df_composition['composition'] = df_composition['composition'].fillna('Doesnt exist')

    df_composition.loc[((df_composition['composition'] == '') | (
                df_composition['composition'] == '(mg)')), 'composition'] = 'Doesnt exist'

    df = pd.merge(df, df_composition, on=['drug_id'], how='left', validate='many_to_one')

    df_comp = df.groupby(['store_id',
                          'composition']).sum().reset_index()[['store_id',
                                                               'composition',
                                                               'quantity0',
                                                               'quantity1',
                                                               'quantity2',
                                                               'quantity3']].rename(columns={'quantity0':'comp_quantity0',
                                                                                             'quantity1':'comp_quantity1',
                                                                                             'quantity2':'comp_quantity2',
                                                                                             'quantity3':'comp_quantity3'})

    df_comp = append_binary_tags(df_comp,
                                 buckets=['comp_quantity0',
                                          'comp_quantity1',
                                          'comp_quantity2',
                                          'comp_quantity3'])

    df_comp_1 = output_comps(df_comp.copy(), comp_buckets=['comp_quantity1_b',
                                                           'comp_quantity2_b',
                                                           'comp_quantity3_b'], i=1)

    df = pd.merge(df, df_comp_1, on=['store_id', 'composition'], how='left', validate='many_to_one')

    df_comp_2 = output_comps(df_comp.copy(), comp_buckets=['comp_quantity0_b', 'comp_quantity1_b', 'comp_quantity2_b'], i=2)

    df = pd.merge(df, df_comp_2, on=['store_id', 'composition'], how='left', validate='many_to_one')

    return df


def add_filters(df):
    ''' remove 000 and 111 before passing to probability matrix for drugs bucketwise'''

    df = df[~(df['historical_bucket'].str.endswith('000'))]
    df = df[~(df['historical_bucket'].str.endswith('111'))]
    return df


def add_bucket(df, buckets, name):
    ''' make buckets is_repeatable + total_comp_sold + quantity0 + quantity1+quantity2'''

    df_bucket = df.copy()
    print('columns to create final buckets are:', buckets)

    df_bucket[name] = ''
    # only _b wale are considered. Is_repeatable etc. are all
    for x in buckets:
        df_bucket[x] = df_bucket[x].map(int)
        df_bucket[name] = df_bucket[name] + df_bucket[x].map(str)

    df[name] = df_bucket[name]

    return df_bucket


def build_probability_matrix(dfi):
    ''' build cumulative probability matrix. quantity0 means last month quantity sold'''
    df = dfi.copy()

    df['sold_analysis_month_flag'] = np.where(df['quantity0'] > 0, 1, 0)

    df = df.groupby(['historical_bucket'], as_index=False).agg({'sold_analysis_month_flag': 'mean',
                                                                'drug_id': 'count'})
    df.rename({'sold_analysis_month_flag': 'selling_probability',
               'drug_id': 'total_drugs_in_bucket'}, axis=1, inplace=True)


    df = df.sort_values(by=['selling_probability'], ascending=False)
    df['sold_cumm'] = (df['selling_probability'] * df['total_drugs_in_bucket']).cumsum()
    df['total_cumm'] = (df['total_drugs_in_bucket']).cumsum() #cumulative number of total drugs
    df['cumm_prob'] = df['sold_cumm'] / df['total_cumm']  #cummulative probability = sold_cumm/total cummulative drugs

    df = df.drop(columns=['total_drugs_in_bucket', 'sold_cumm', 'total_cumm'], axis=1)

    return df


def calculate_probabilities(df, db, schema):
    '''
    calculate probabilties for buckets in order as follows
       1. is_repeatable.
       2. total_months composition sold (i.e. -1,1,2,3).-1 means composition doesn't exist
       3. quantity0 is previous month. quantity4 is oldest month:
           3.1 previous month - 0
           3.2 two months ago - 1
           3.3 three months ago - 2
           3.4 four months ago - 3

           -- 3,2,1 are historical months
           -- 2,1,0 are current months

    --make flags: adds quantity sold for each month.

    --append_binary_tags converts quantity sold into binary tags (1 or 0)

    -- add features: appends repeatability, total number of times
    composition is sold, current inv and ptr, original max values

    -- add bucket: appends bucket in the order of features it is supplied with.

    -- add filters removes drugs which aren't used while building the probability matrix (removed 000 and 111 cases from historical)

    -- build probability matrix calculates the final probabilities
    '''

    df = make_flags(df.copy(), db, schema, metric='total_sales_quantity')

    df = append_binary_tags(df, buckets=['quantity0', 'quantity1', 'quantity2', 'quantity3'])

    df = add_features(df.copy(), db, schema)

    df = add_bucket(df.copy(),
                    buckets=['is_repeatable', 'total_months_comp_sold_1', 'quantity3_b', 'quantity2_b', 'quantity1_b'],
                    name='historical_bucket')

    df = add_bucket(df.copy(),
                    buckets=['is_repeatable', 'total_months_comp_sold_2', 'quantity2_b', 'quantity1_b', 'quantity0_b'],
                    name='current_bucket')

    #add moving average for last 3 months and current 3 months
    df['current_ma_3_months'] = (df['quantity0'] + df['quantity1'] + df['quantity2']) / 3
    df['historical_ma_3_months'] = (df['quantity1'] + df['quantity2'] + df['quantity3']) / 3

    #make separation between moving average less than 2 and greater than 2 based on moving average of historical months. (month3, month2,month1)
    df['historical_flag_ma_less_than_2'] = np.where(df['historical_ma_3_months'] < 2, 1, 0)
    df['historical_flag_ma_greater_than_5'] = np.where(df['historical_ma_3_months'] > 5, 1, 0)

    df['current_flag_ma_less_than_2'] = np.where(df['current_ma_3_months'] < 2, 1, 0)

    #1 is for ma less than 2.
    #2 is for ma greater than 2

    hist_df1 = df[df['historical_flag_ma_less_than_2'] == 1]
    hist_df2 = df[((df['historical_flag_ma_less_than_2'] == 0) & (df['historical_flag_ma_greater_than_5'] == 0))]

    # this would remove 000 and 111 drugs before removing historical buckets.
    # Done separately because some buckets in historical might be 111 which are not 111 in current bucket
    hist_df1 = add_filters(hist_df1)
    hist_df2 = add_filters(hist_df2)

    probability_matrix_1 = build_probability_matrix(hist_df1)
    probability_matrix_2 = build_probability_matrix(hist_df2)

    #drugs which are 111 and 000 in current buckets are removed.'
    df_eligible = df[~((df['current_bucket'].str.endswith('000')) | (df['current_bucket'].str.endswith('111')))]

    df_eligible_1 = df_eligible[(df_eligible['current_flag_ma_less_than_2'] == 1)]
    df_eligible_2 = df_eligible[(df_eligible['current_flag_ma_less_than_2'] == 0)]

    df_eligible_1 = df_eligible_1.drop(['historical_bucket'], axis=1)
    df_eligible_2 = df_eligible_2.drop(['historical_bucket'], axis=1)

    #mapping historical bucket probabilites onto current buckets
    df_eligible_1 = pd.merge(df_eligible_1, probability_matrix_1, how='left', left_on=['current_bucket'], right_on=['historical_bucket'], validate='many_to_one')
    df_eligible_2 = pd.merge(df_eligible_2, probability_matrix_2, how='left', left_on=['current_bucket'], right_on=['historical_bucket'], validate='many_to_one')

    matrix = pd.concat([df_eligible_1, df_eligible_2])

    # add relevant variables
    matrix['corrected_max'] = np.where(matrix['max'] != 0, matrix['max'], np.round(matrix['current_ma_3_months']))

    matrix['corrected_max'] = np.where(matrix['current_flag_ma_less_than_2'] == 1, 1, # put default value of MA<2 as 1.
                                       matrix['corrected_max'])

    matrix['inv_impact'] = np.where(matrix['current_inventory'] >= matrix['corrected_max'], 0,
                                    (matrix['corrected_max'] - matrix['current_inventory']) * matrix['avg_ptr'])

    matrix['max_impact'] = matrix['corrected_max'] * matrix['avg_ptr']

    matrix['cumm_prob'] = np.round(matrix['cumm_prob'], 2)
    matrix['selling_probability'] = np.round(matrix['selling_probability'], 2)

    matrix = matrix[['store_id', 'drug_id', 'composition', 'max', 'avg_ptr', 'current_inventory',
                   'current_ma_3_months', 'is_repeatable', 'total_months_comp_sold_2', 'quantity2',
                   'quantity1', 'quantity0', 'current_bucket', 'current_flag_ma_less_than_2',
                   'selling_probability', 'cumm_prob', 'corrected_max', 'inv_impact', 'max_impact']]

    #separating 111 for further analysis.
    matrix_111 = df[df['current_bucket'].str.endswith('111')][['store_id', 'drug_id','composition','avg_ptr',
                                                            'current_inventory', 'quantity0', 'quantity1',
                                                            'quantity2', 'max', 'current_ma_3_months']]

    matrix_111['corrected_max'] = np.where(matrix_111['max'] == 0, np.round(matrix_111['current_ma_3_months']), matrix_111['max'])

    matrix_111['inv_impact'] = np.where(matrix_111['current_inventory'] >= matrix_111['corrected_max'], 0,
                                    (matrix_111['corrected_max'] - matrix_111['current_inventory']) * matrix_111['avg_ptr'])

    matrix_111['max_impact'] = matrix_111['corrected_max'] * matrix_111['avg_ptr']

    # quantity0 is prev month.  quantity1 is two months ago and so on.
    matrix = matrix.rename(columns={"quantity0": "quantity_sold_0",
                                    "quantity1": "quantity_sold_1",
                                    "quantity2": "quantity_sold_2",
                                    "quantity3": "quantity_sold_3",
                                    'max': 'original_max',
                                    'is_repeatable': 'bucket_flag_is_repeatable',
                                    'total_months_comp_sold_2': 'bucket_flag_total_months_comp_sold',
                                    'quantity0_b': 'bucket_flag_quantity0_b',
                                    'quantity1_b': 'bucket_flag_quantity1_b',
                                    'quantity2_b': 'bucket_flag_quantity2_b',
                                    'quantity3_b': 'bucket_flag_quantity3_b'
                                    })

    matrix_111 = matrix_111.rename(columns={"quantity0": "quantity_sold_0",
                                    "quantity1": "quantity_sold_1",
                                    "quantity2": "quantity_sold_2",
                                    'current_ma_3_months':"ma_3_months",
                                    "max":"original_max"})

    return matrix, matrix_111, probability_matrix_1, probability_matrix_2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)

    parser.add_argument('-d', '--debug_mode', default="Y", type=str, required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to

    debug_mode = args.debug_mode

    logger = get_logger()
    s3 = S3()
    rs_db_read = DB(read_only=True)
    rs_db_write = DB(read_only=False)
    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'

    # open RS connection
    rs_db_read.open_connection()
    rs_db_write.open_connection()

    """ calling the main function """
    status = main(debug_mode, rs_db_read, rs_db_write, read_schema,
                  write_schema, s3, logger)

    # close RS connection
    rs_db_read.close_connection()
    rs_db_write.close_connection()

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    reset_date = dt.date.today().strftime("%Y-%m-%d")
    email.send_email_file(
        subject=f"IPC V3 Corrections Matrix (GLUE-{env}) {reset_date}: {status}",
        mail_body=f"""
                Debug Mode: {debug_mode}
                Job Params: {args}
                """,
        to_emails=email_to)

    logger.info("Script ended")
