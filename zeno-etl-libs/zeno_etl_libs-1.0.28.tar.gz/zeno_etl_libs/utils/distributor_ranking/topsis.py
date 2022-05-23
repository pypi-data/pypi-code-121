"""code logic for topsis algorithm is implemented"""

import pandas as pd
import numpy as np
from sklearn import preprocessing


def apply_topsis(features, x_train, weights, cutoff_percentage, volume_fraction):
    ''' cutoff percentage is cutoff for determining whether a distributor is low volume or not'''

    scaler = preprocessing.MinMaxScaler()

    # normalize features
    x_normalized = pd.DataFrame(
        scaler.fit_transform(x_train), columns=x_train.columns)

    # multiply with normalized weights here.
    x_weighted = np.multiply(x_normalized, weights)

    # merge drug id, dist id and dc id for reference
    x_weighted = pd.merge(features[['drug_id', 'partial_distributor_id', 'partial_dc_id']],
                          x_weighted, left_index=True, right_index=True, how='inner')

    # define ideal best vector here
    ideal_best = x_weighted.agg({'lead_time': 'min', 'margin': 'max', 'bounce_rate': 'min',
                                 'ff': 'max',
                                 'lost_recency': 'max',
                                 'success_recency': 'min'}).reset_index()

    ideal_best = ideal_best.set_index(
        'index').rename(columns={0: 'ideal_best'})

    # define ideal worse vector here.
    ideal_worse = x_weighted.agg({'lead_time': 'max', 'margin':'min',
                                  'bounce_rate': 'max',
                                  'ff': 'min',
                                  'lost_recency': 'min',
                                  'success_recency': 'max'}).reset_index()

    ideal_worse = ideal_worse.set_index(
        'index').rename(columns={0: 'ideal_worse'})

    x_weighted_best = pd.merge(x_weighted.T, ideal_best,
                               how='left', left_index=True, right_index=True).T

    x_weighted_worse = pd.merge(x_weighted.T, ideal_worse,
                                how='left', left_index=True, right_index=True).T

    # euclidean distance with ideal worse is calculated here.
    ideal_worse_ed = x_weighted_worse[['lead_time', 'margin', 'bounce_rate', 'ff',
                                       'lost_recency',
                                       'success_recency']].apply(lambda x: np.linalg.norm(x.values - ideal_worse['ideal_worse'].values), axis=1)

    ideal_worse_ed = pd.DataFrame(ideal_worse_ed, columns=['ideal_worse_ed'])

    # euclidean distance with ideal best is calculated here.
    ideal_best_ed = x_weighted_best[['lead_time', 'margin',
                                     'bounce_rate', 'ff',
                                     'lost_recency',
                                     'success_recency']].apply(lambda x: np.linalg.norm(x.values - ideal_best['ideal_best'].values), axis=1)

    ideal_best_ed = pd.DataFrame(ideal_best_ed, columns=['ideal_best_ed'])

    # append ideal worse euclidean distance here.
    x_eval = pd.merge(x_weighted, ideal_worse_ed, how='left',
                      left_index=True, right_index=True)

    # append ideal best euclidean distance here.
    x_eval = pd.merge(x_eval, ideal_best_ed, how='left',
                      left_index=True, right_index=True)

    x_eval['performance'] = (x_eval['ideal_worse_ed'] /
                             (x_eval['ideal_worse_ed'] + x_eval['ideal_best_ed'])) * 100

    x_rank = x_eval.copy()

    x_rank['rank'] = x_rank.groupby(['partial_dc_id', 'drug_id'])[
        'performance'].rank(method='first', ascending=False)

    x_rank['rank'] = x_rank['rank'].astype(int)

    #################heuristics #############

    features_rank = pd.merge(features,
                             x_rank[['drug_id', 'partial_distributor_id',
                                     'partial_dc_id', 'performance', 'rank']],
                             how='outer', validate='one_to_one')

    # add filter for low volume distributor exclusion for heuristic substitute
    volume = features_rank.groupby(['partial_dc_id', 'partial_distributor_id',
                                    'partial_distributor_name']).agg(
        total_requests=('total_requests', 'sum'))
    small_dist = volume.copy()
    cutoff = max(small_dist['total_requests']) * cutoff_percentage
    print(max(small_dist))
    print('low volumne cutoff: ', cutoff)
    small_dist['is_small'] = np.where(volume['total_requests'] < cutoff, 1, 0)
    small_dist = small_dist.reset_index()
    small_dist['fraction_total_requests'] = small_dist['total_requests'] / \
        small_dist['total_requests'].sum()

    # add flag for small distributors here
    features_rank = pd.merge(features_rank,
                             small_dist[['partial_dc_id',
                                         'partial_distributor_id', 'is_small']],
                             on=['partial_dc_id', 'partial_distributor_id'],
                             validate='many_to_one',
                             how='left')

    dc_type_performance = features_rank.groupby(['partial_dc_id', 'drug_type', 'partial_distributor_id']).agg(
        dc_type_performance=('performance', 'mean')).reset_index()

    features_rank = pd.merge(features_rank, dc_type_performance,
                             on=['partial_dc_id', 'drug_type', 'partial_distributor_id'], how='left',
                             validate='many_to_one')

    # determine dc type rank
    features_rank['dc_type_rank'] = \
        features_rank[(features_rank['is_small'] == 0) | ((features_rank['drug_type'] != 'generic') & (features_rank['drug_type'] != 'ethical'))].groupby(['partial_dc_id', 'drug_type'])['dc_type_performance'].rank(
        method='dense', ascending=False).astype(int, errors='ignore')

    dc_type_rank_ref = pd.pivot_table(features_rank, index=['partial_dc_id', 'drug_type'], columns=['dc_type_rank'],
                                      values='partial_distributor_id').add_prefix('dc_drug_type_level_dist_').reset_index()

    features_rank = pd.merge(features_rank,
                             dc_type_rank_ref[['partial_dc_id', 'drug_type', 'dc_drug_type_level_dist_1.0',
                                               'dc_drug_type_level_dist_2.0', 'dc_drug_type_level_dist_3.0']],
                             how='left', on=['partial_dc_id', 'drug_type'], validate='many_to_one')

    # append enterprise type rank
    enterprise_type_performance = features_rank.groupby(['drug_type', 'partial_distributor_id']).agg(
        enterprise_type_performance=('performance', 'mean')).reset_index()

    features_rank = pd.merge(features_rank, enterprise_type_performance, on=['drug_type', 'partial_distributor_id'],
                             how='left', validate='many_to_one')

    features_rank['enterprise_type_rank'] = features_rank[(features_rank['is_small'] == 0)
                                                          | ((features_rank['drug_type'] != 'generic')
                                                             & (features_rank['drug_type'] != 'ethical'))].groupby(['drug_type'])[
        'enterprise_type_performance'].rank(method='dense', ascending=False).astype(int, errors='ignore')

    enterprise_type_rank_ref = pd.pivot_table(features_rank, index=['drug_type'], columns=['enterprise_type_rank'],
                                              values='partial_distributor_id').add_prefix('enterprise_drug_type_level_dist_').reset_index()

    features_rank = pd.merge(features_rank,
                             enterprise_type_rank_ref[['drug_type',
                                                       'enterprise_drug_type_level_dist_1.0',
                                                       'enterprise_drug_type_level_dist_2.0',
                                                       'enterprise_drug_type_level_dist_3.0']],
                             how='left', on=['drug_type'], validate='many_to_one')

    # 999 denotes that bounce rate = 1 and total requests is greater than 5 for that distributor.
    features_rank['rank'] = np.where(
        (features_rank['rank'] == 1) & (features_rank['bounce_rate'] == 1) & (
            features_rank['total_requests'] > 5),
        999, features_rank['rank'])

    features_rank['rank'] = np.where(
        (features_rank['rank'] == 2) & (features_rank['bounce_rate'] == 1) & (
            features_rank['total_requests'] > 5),
        999, features_rank['rank'])

    features_rank['rank'] = np.where(
        (features_rank['rank'] == 3) & (features_rank['bounce_rate'] == 1) & (
            features_rank['total_requests'] > 5),
        999, features_rank['rank'])

    output_ranks = pd.pivot_table(features_rank, index=['partial_dc_id', 'drug_id'], columns='rank',
                                  values='partial_distributor_id')[[1, 2, 3]].add_prefix('final_dist_').add_suffix('.0').reset_index()

    features_rank = pd.merge(features_rank, output_ranks, on=['partial_dc_id', 'drug_id'], how='left',
                             validate='many_to_one')

    # add volume fraction here
    features_rank['volume_fraction'] = volume_fraction

    ######organize output here ####################

    # remove .0 suffix from columns
    features_rank.columns = features_rank.columns.str.replace(r'.0$', '')

    # remove partial_ prefix from columns
    features_rank.columns = features_rank.columns.str.replace(r'^partial_', '')

    # decide columns to be included here
    features_rank = features_rank[['dc_id', 'dc_name', 'distributor_id',
                                   'distributor_name',
                                   'distributor_type',
                                   'is_small', 'drug_id',
                                   'drug_name', 'drug_type',
                                   'lead_time', 'margin',
                                   'total_lost', 'total_requests',
                                   'bounce_rate', 'ff',
                                   'lost_recency', 'success_recency',
                                   'performance', 'rank',
                                   'final_dist_1',
                                   'final_dist_2',
                                   'final_dist_3',
                                   'dc_drug_type_level_dist_1',
                                   'dc_drug_type_level_dist_2',
                                   'dc_drug_type_level_dist_3',
                                   'enterprise_drug_type_level_dist_1',
                                   'enterprise_drug_type_level_dist_2',
                                   'enterprise_drug_type_level_dist_3',
                                   'volume_fraction']]

    return features_rank


def apply_topsis_franchisee(features, x_train, weights, cutoff_percentage, volume_fraction):
    '''cutoff percentage is cutoff for determining whether a distributor is low volume or not'''

    scaler = preprocessing.MinMaxScaler()

    # normalize features
    x_normalized = pd.DataFrame(
        scaler.fit_transform(x_train), columns=x_train.columns)

    # multiply with normalized weights here.
    x_weighted = np.multiply(x_normalized, weights)

    # merge drug id, dist id and store id for reference
    x_weighted = pd.merge(
        features[['drug_id', 'partial_distributor_id', 'store_id']],
        x_weighted, left_index=True, right_index=True, how='inner')

    # define ideal best vector here
    ideal_best = x_weighted.agg(
        {'lead_time': 'min', 'margin': 'max', 'bounce_rate': 'min',
         'ff': 'max',
         'lost_recency': 'max',
         'success_recency': 'min'}).reset_index()

    ideal_best = ideal_best.set_index(
        'index').rename(columns={0: 'ideal_best'})

    # define ideal worse vector here.
    ideal_worse = x_weighted.agg({'lead_time': 'max', 'margin': 'min',
                                  'bounce_rate': 'max',
                                  'ff': 'min',
                                  'lost_recency': 'min',
                                  'success_recency': 'max'}).reset_index()

    ideal_worse = ideal_worse.set_index(
        'index').rename(columns={0: 'ideal_worse'})

    x_weighted_best = pd.merge(x_weighted.T, ideal_best,
                               how='left', left_index=True, right_index=True).T

    x_weighted_worse = pd.merge(x_weighted.T, ideal_worse,
                                how='left', left_index=True, right_index=True).T

    # euclidean distance with ideal worse is calculated here.
    ideal_worse_ed = x_weighted_worse[
        ['lead_time', 'margin', 'bounce_rate', 'ff',
         'lost_recency',
         'success_recency']].apply(
        lambda x: np.linalg.norm(x.values - ideal_worse['ideal_worse'].values),
        axis=1)

    ideal_worse_ed = pd.DataFrame(ideal_worse_ed, columns=['ideal_worse_ed'])

    # euclidean distance with ideal best is calculated here.
    ideal_best_ed = x_weighted_best[['lead_time', 'margin',
                                     'bounce_rate', 'ff',
                                     'lost_recency',
                                     'success_recency']].apply(
        lambda x: np.linalg.norm(x.values - ideal_best['ideal_best'].values),
        axis=1)

    ideal_best_ed = pd.DataFrame(ideal_best_ed, columns=['ideal_best_ed'])

    # append ideal worse euclidean distance here.
    x_eval = pd.merge(x_weighted, ideal_worse_ed, how='left',
                      left_index=True, right_index=True)

    # append ideal best euclidean distance here.
    x_eval = pd.merge(x_eval, ideal_best_ed, how='left',
                      left_index=True, right_index=True)

    x_eval['performance'] = (x_eval['ideal_worse_ed'] /
                             (x_eval['ideal_worse_ed'] + x_eval[
                                 'ideal_best_ed'])) * 100

    x_rank = x_eval.copy()

    x_rank['rank'] = x_rank.groupby(['store_id', 'drug_id'])[
        'performance'].rank(method='first', ascending=False)

    x_rank['rank'] = x_rank['rank'].astype(int)

    #################heuristics #############

    features_rank = pd.merge(features,
                             x_rank[['drug_id', 'partial_distributor_id',
                                     'store_id', 'performance', 'rank']],
                             how='outer', validate='one_to_one')

    # add filter for low volume distributor exclusion for heuristic substitute
    volume = features_rank.groupby(['store_id', 'partial_distributor_id',
                                    'partial_distributor_name']).agg(
        total_requests=('total_requests', 'sum'))
    small_dist = volume.copy()
    cutoff = max(small_dist['total_requests']) * cutoff_percentage
    print(max(small_dist))
    print('low volumne cutoff: ', cutoff)
    small_dist['is_small'] = np.where(volume['total_requests'] < cutoff, 1, 0)
    small_dist = small_dist.reset_index()
    small_dist['fraction_total_requests'] = small_dist['total_requests'] / \
                                            small_dist['total_requests'].sum()

    # add flag for small distributors here
    features_rank = pd.merge(features_rank,
                             small_dist[['store_id',
                                         'partial_distributor_id', 'is_small']],
                             on=['store_id', 'partial_distributor_id'],
                             validate='many_to_one',
                             how='left')

    store_type_performance = features_rank.groupby(
        ['store_id', 'drug_type', 'partial_distributor_id']).agg(
        store_type_performance=('performance', 'mean')).reset_index()

    features_rank = pd.merge(features_rank, store_type_performance,
                             on=['store_id', 'drug_type',
                                 'partial_distributor_id'], how='left',
                             validate='many_to_one')

    # determine store type rank
    features_rank['store_type_rank'] = \
        features_rank[(features_rank['is_small'] == 0) | (
                    (features_rank['drug_type'] != 'generic') & (
                        features_rank['drug_type'] != 'ethical'))].groupby(
            ['store_id', 'drug_type'])['store_type_performance'].rank(
            method='dense', ascending=False).astype(int, errors='ignore')

    store_type_rank_ref = \
    pd.pivot_table(features_rank, index=['store_id', 'drug_type'],
                   columns=['store_type_rank'],
                   values='partial_distributor_id')[[1, 2, 3]].add_prefix(
        'store_drug_type_level_dist_').reset_index()

    features_rank = pd.merge(features_rank,
                             store_type_rank_ref[['store_id', 'drug_type',
                                                  'store_drug_type_level_dist_1',
                                                  'store_drug_type_level_dist_2',
                                                  'store_drug_type_level_dist_3']],
                             how='left', on=['store_id', 'drug_type'],
                             validate='many_to_one')

    # 999 denotes that bounce rate = 1 and total requests is greater than 5 for that distributor.
    features_rank['rank'] = np.where(
        (features_rank['rank'] == 1) & (features_rank['bounce_rate'] == 1) & (
                features_rank['total_requests'] > 5),
        999, features_rank['rank'])

    features_rank['rank'] = np.where(
        (features_rank['rank'] == 2) & (features_rank['bounce_rate'] == 1) & (
                features_rank['total_requests'] > 5),
        999, features_rank['rank'])

    features_rank['rank'] = np.where(
        (features_rank['rank'] == 3) & (features_rank['bounce_rate'] == 1) & (
                features_rank['total_requests'] > 5),
        999, features_rank['rank'])

    output_ranks = \
    pd.pivot_table(features_rank, index=['store_id', 'drug_id'], columns='rank',
                   values='partial_distributor_id')[[1, 2, 3]].add_prefix(
        'final_dist_').add_suffix('.0').reset_index()

    features_rank = pd.merge(features_rank, output_ranks,
                             on=['store_id', 'drug_id'], how='left',
                             validate='many_to_one')

    # add volume fraction here
    features_rank['volume_fraction'] = volume_fraction

    ######organize output here ####################

    # remove .0 suffix from columns
    features_rank.columns = features_rank.columns.str.replace(r'.0$', '')

    # remove partial_ prefix from columns
    features_rank.columns = features_rank.columns.str.replace(r'^partial_', '')

    # decide columns to be included here
    features_rank = features_rank[['store_id', 'store_name', 'franchisee_id',
                                   'distributor_id',
                                   'distributor_name',
                                   'distributor_type',
                                   'is_small', 'drug_id',
                                   'drug_name', 'drug_type',
                                   'lead_time', 'margin',
                                   'total_lost', 'total_requests',
                                   'bounce_rate', 'ff',
                                   'lost_recency', 'success_recency',
                                   'performance', 'rank',
                                   'final_dist_1',
                                   'final_dist_2',
                                   'final_dist_3',
                                   'store_drug_type_level_dist_1',
                                   'store_drug_type_level_dist_2',
                                   'store_drug_type_level_dist_3',
                                   'volume_fraction']]

    return features_rank