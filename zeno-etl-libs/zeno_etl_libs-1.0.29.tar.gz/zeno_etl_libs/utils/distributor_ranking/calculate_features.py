
"""
features for ranking algorithm, namely
1. Lead time
2. Margin
3. Bounce rate
4. FF
5. Success recency
6. Lost recency
"""

from functools import reduce

import numpy as np
import pandas as pd


def calculate_features(df_features, group_cols):
    """
    DC-LEVEL: group_cols=['partial_dc_id','partial_distributor_id', 'drug_id']
    FRANCHISEE-LEVEL: group_cols=['store_id','partial_distributor_id', 'drug_id']
    """

    '''outputs the calculated features when supplied with raw data'''

    dfx = df_features[df_features['invoice_count'] != 0]

    ####################### feature calculation starts ########################

    ####lead time calculations ########

    df_lead_time = df_features.copy()

    cond_0 = (df_lead_time['invoice_count'] == 0)

    df_lead_time['lead_time'] = float('NaN')

    # for those cases where reordered does not exists and invoice count is 0
    # lead time is invoiced-at - created at for invoice count 0

    df_lead_time['lead_time'] = np.where((df_lead_time['original_created_at_2'].isna()) & (~cond_0),
                                         (df_lead_time['partial_invoiced_at'] -
                                          df_lead_time['original_created_at']).astype('timedelta64[h]'),
                                         df_lead_time['lead_time'])

    # for cases where invoiced_at - reordered_at < 8, lead time is unreliable.
    df_lead_time['lead_time'] = np.where(
        (~df_lead_time['original_created_at_2'].isna() |

         (((df_lead_time['partial_invoiced_at'] -
            df_lead_time['original_created_at_2']).astype('timedelta64[h]')) > 8))

        & (~cond_0),

        (df_lead_time['partial_invoiced_at'] -
         df_lead_time['original_created_at_2']).astype('timedelta64[h]'),
        df_lead_time['lead_time'])

    df_lead_time['lead_time'] = np.where(
        (~df_lead_time['original_created_at_2'].isna() |

         (((df_lead_time['partial_invoiced_at'] -
            df_lead_time['original_created_at_2']).astype('timedelta64[h]')) < 8))

        & (~cond_0),

        (df_lead_time['partial_invoiced_at'] -
         df_lead_time['original_created_at']).astype('timedelta64[h]'),
        df_lead_time['lead_time'])

    # invoice count 0, take lead time as max value
    # This is done because we are eventually scaling things between 0 to 1.
    df_lead_time['lead_time'] = np.where(cond_0,
                                         df_lead_time['lead_time'].max(),
                                         df_lead_time['lead_time'])

    # If after taking the condition for lead time less than 8,
    # still cases are present then those are unreliable, take lead time as mean.

    df_lead_time.loc[df_lead_time['lead_time'] < 8, 'lead_time'] = df_lead_time[df_lead_time['lead_time'] > 8][
        'lead_time'].mean()

    # lead time for a distributor per drug id is the average of lead time per order.
    df_lead_time = df_lead_time.groupby(group_cols).agg(
        lead_time=('lead_time', 'mean')).reset_index()

    # sanity check
    assert df_lead_time.shape[0] == \
        df_features[group_cols].drop_duplicates().shape[0]

    print('finished lead time calculations')

    ####### margin calculation starts #######

    df_margin = dfx.copy()

    df_margin['margin'] = (df_margin['selling_rate'] -
                           df_margin['distributor_rate']) / df_margin['selling_rate']

    df_margin = df_margin.groupby(group_cols).agg(margin=('margin', 'mean')).reset_index()

    # sanity check
    assert df_margin.shape[0] == dfx[group_cols].drop_duplicates().shape[0]

    print('finished margin calculations')

    ####### bounce rate calculation #######

    df_br = df_features.groupby(group_cols).agg(
        total_lost=('is_lost', 'sum'),
        total_requests=('is_lost', 'count')).reset_index()

    df_br['bounce_rate'] = (df_br['total_lost']) / df_br['total_requests']

    # sanity check
    assert df_br.shape[0] == df_features[group_cols].drop_duplicates().shape[0]

    print('finished bounce rate calculations')

    ####### ff calculation #######

    df_sorted = dfx.groupby(['short_book_1_id'], as_index=False).apply(
        lambda x: x.sort_values(by=['partial_invoiced_at']))

    # for multiple invoices, calculate cumulative fulfilled quantities
    df_sorted = df_sorted.groupby(['short_book_1_id']).apply(
        lambda x: x['partial_quantity'].cumsum()).reset_index().rename(
        columns={'partial_quantity': 'cum_partial_quantity'})

    df_sorted = df_sorted.set_index('level_1')

    df_fulfillment = pd.merge(df_sorted, dfx, left_index=True,
                              right_index=True, how='left', suffixes=('', '_y'))
    assert df_fulfillment['short_book_1_id'].equals(
        df_fulfillment['short_book_1_id_y'])

    df_fulfillment = df_fulfillment[
        ['short_book_1_id'] + group_cols + ['original_order', 'partial_quantity',
         'cum_partial_quantity']]

    # cum required quantity is quantity left after subtracting cum quantity from all previous invoices.
    df_fulfillment['cum_required_quantity'] = df_fulfillment['original_order'] - \
        df_fulfillment['cum_partial_quantity']

    # the real required quantity while placing an order is quantity
    # unfulfilled by the previours invoice. Hence shifted by 1
    df_fulfillment['actual_required'] = df_fulfillment.groupby(
        ['short_book_1_id']).shift(1)['cum_required_quantity']

    # fill single invoices with the original order
    df_fulfillment['actual_required'] = df_fulfillment['actual_required'].fillna(
        df_fulfillment['original_order'])

    # put actual required = 0 when ordered exceeds required.
    df_fulfillment.loc[df_fulfillment['actual_required']
                       < 0, 'actual_required'] = 0

    df_fulfillment['redundant_order_flag'] = np.where(
        df_fulfillment['actual_required'] == 0, 1, 0)

    df_fulfillment = df_fulfillment[['short_book_1_id'] + group_cols +
                                    ['original_order', 'partial_quantity', 'actual_required', 'redundant_order_flag']]

    df_fulfillment['ff'] = df_fulfillment['partial_quantity'] / \
        df_fulfillment['actual_required']

    # for those quantities where nothing was required and still order placed, take them as 0.
    df_fulfillment.loc[(df_fulfillment['actual_required'] == 0) & (
        df_fulfillment['partial_quantity'] > 0), 'ff'] = 1

    df_fulfillment.loc[(df_fulfillment['ff'] > 1), 'ff'] = 1

    # removed redundant orders here.
    df_ff = df_fulfillment[df_fulfillment['redundant_order_flag'] != 1].groupby(group_cols).agg(ff=('ff', 'mean')).reset_index()


    print('finished ff calculations')

    ####### recency lost calculations #######

    # number of days ago it was marked lost.

    df_recency_lost = df_features[df_features['is_lost'] == 1].groupby(group_cols).agg(
        max_lost_date=('original_created_at', 'max')).reset_index()

    df_recency_lost['lost_recency'] = (
        pd.datetime.today() - pd.to_datetime(df_recency_lost['max_lost_date'])).dt.days

    df_recency_lost = df_recency_lost[group_cols + ['lost_recency']]

    ####### recency success calculations #######

    # number of days ago it was marked success

    df_recency_success = df_features[df_features['is_lost'] == 0].groupby(group_cols).agg(
        max_success_date=('original_created_at', 'max')).reset_index()

    df_recency_success['success_recency'] = (
        pd.datetime.today() - pd.to_datetime(df_recency_success['max_success_date'])).dt.days

    df_recency_success = df_recency_success[group_cols + ['success_recency']]

    print('finished recency calculations')

    ######################## feature calculation ends #########################

    ################## compiling all the features #############################

    meg_list = [df_lead_time, df_margin, df_br,
                df_ff, df_recency_lost, df_recency_success]

    features = reduce(
        lambda left, right: pd.merge(left, right,
                                     on=group_cols,
                                     how='outer'), meg_list)

    # lead_time: Replace lead time NA (i.e. bounce rate 1) with max lead time.
    features['lead_time'] = features['lead_time'].fillna(
        features['lead_time'].max())

    # margin
    features['margin'] = features['margin'].fillna(features['margin'].mean())

    # ff
    features.loc[(features['ff'].isna()) & (
        features['bounce_rate'] == 1), 'ff'] = 0
    features['ff'] = features['ff'].fillna(features['ff'].mean())

    # for bounce rate = 0.
    features['lost_recency'] = features['lost_recency'].fillna(
        features['lost_recency'].max())

    # for bounce rate = 1
    features['success_recency'] = features['success_recency'].fillna(
        features['success_recency'].max())

    print('finished compiling features')

    return features

