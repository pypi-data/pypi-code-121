"""all main calculation of distributor ranking take place via this module.
output is all the features associated with each distributor for both PR and AS"""

import pandas as pd

from zeno_etl_libs.utils.distributor_ranking.pull_data import pull_data, pull_data_franchisee
from zeno_etl_libs.utils.distributor_ranking.preprocess_features import preprocess_features_dc, preprocess_features_franchisee
from zeno_etl_libs.utils.distributor_ranking.calculate_features import calculate_features
from zeno_etl_libs.utils.distributor_ranking.topsis import apply_topsis, apply_topsis_franchisee


def ranking_calc_dc(time_interval, weights_as, weights_pr, as_low_volume_cutoff,
                    pr_low_volume_cutoff, volume_fraction, db, read_schema, logger):
    '''output distributor ranking for AS and PR separately'''

    logger.info('starting to import data')

    # add 7 days to time interval since we do not want to include last week's data.
    time_interval = time_interval + 7

    df_features, df_distributors = pull_data(time_interval, db, read_schema)
    logger.info('finished importing data')

    ######################### preprocessing starts #########################

    logger.info('started preprocessing')

    df_features = preprocess_features_dc(df_features, db, read_schema)

    # add distributor name and distributor features here.
    df_features = pd.merge(df_features, df_distributors, on=['partial_distributor_id'],
                           how='left', validate='many_to_one')

    logger.info('finished preprocessing')

    ########################## preprocessing ends ##########################

    ####################### features calculation starts #######################

    features = calculate_features(df_features, group_cols=['partial_dc_id','partial_distributor_id','drug_id'])

    ##### add neccessary columns in features #####

    # add drug type column here
    features = pd.merge(features, df_features[['drug_id', 'drug_type']].drop_duplicates(), on=['drug_id'],
                        how='left',
                        validate='many_to_one')

    # add dist type column here
    features = pd.merge(features, df_features[
        ['partial_distributor_id', 'partial_distributor_name', 'partial_distributor_type']].drop_duplicates(),
        on=['partial_distributor_id'], how='left',
        validate='many_to_one')

    # add dc name here.
    features = pd.merge(features, df_features[['partial_dc_id', 'dc_name']].dropna().drop_duplicates(),
                        on=['partial_dc_id'], validate='many_to_one', how='left')

    # add drug name here
    features = pd.merge(features, df_features[['drug_id', 'drug_name']].drop_duplicates(),
                        on=['drug_id'], validate='many_to_one', how='left')

    #### apply topsis ####

    # weights format is [lead time, margin, bounce rate, ff, lost recency, success recency]

    x_train = features[['lead_time', 'margin', 'bounce_rate',
                        'ff', 'lost_recency', 'success_recency']]

    features_as = apply_topsis(features=features,
                               x_train=x_train, weights=weights_as, cutoff_percentage=as_low_volume_cutoff,
                               volume_fraction=volume_fraction)

    logger.info('applied topsis for as')

    features_pr = apply_topsis(features=features,
                               x_train=x_train, weights=weights_pr, cutoff_percentage=pr_low_volume_cutoff,
                               volume_fraction=volume_fraction)
    logger.info('applied topsis for pr')

    features_as.loc[:, 'request_type'] = 'AS/MS'
    features_pr.loc[:, 'request_type'] = 'PR'

    features_rank = pd.concat([features_as, features_pr])

    return features_rank



def ranking_calc_franchisee(time_interval, weights_as, weights_pr,
                            low_volume_cutoff, volume_fraction, db,
                            read_schema, logger):
    '''output distributor ranking for AS and PR separately'''

    logger.info('starting to import data')

    # add 7 days to time interval since we do not want to include last week's data.
    time_interval = time_interval + 7

    df_features, df_distributors = pull_data_franchisee(time_interval, db, read_schema)
    logger.info('finished importing data')

    ######################### preprocessing starts #########################

    logger.info('started preprocessing')

    df_features = preprocess_features_franchisee(df_features, db, read_schema)

    # add distributor name and distributor features here.
    df_features = pd.merge(df_features, df_distributors, on=['partial_distributor_id'],
                           how='left', validate='many_to_one')

    logger.info('finished preprocessing')

    ########################## preprocessing ends ##########################

    ####################### features calculation starts #######################

    features = calculate_features(df_features, group_cols=['store_id','partial_distributor_id', 'drug_id'])

    ##### add neccessary columns in features #####

    # add drug type column here
    features = pd.merge(features,
                        df_features[['drug_id', 'drug_type']].drop_duplicates(),
                        on=['drug_id'],
                        how='left',
                        validate='many_to_one')

    # add dist type column here
    features = pd.merge(features, df_features[
        ['partial_distributor_id', 'partial_distributor_name',
         'partial_distributor_type']].drop_duplicates(),
                        on=['partial_distributor_id'], how='left',
                        validate='many_to_one')

    # add store name and franchisee_id here.
    features = pd.merge(features, df_features[
        ['store_id', 'store_name', 'franchisee_id']].dropna().drop_duplicates(),
                        on=['store_id'], validate='many_to_one', how='left')

    # add drug name here
    features = pd.merge(features,
                        df_features[['drug_id', 'drug_name']].drop_duplicates(),
                        on=['drug_id'], validate='many_to_one', how='left')

    #### apply topsis ####

    # weights format is [lead time, margin, bounce rate, ff, lost recency, success recency]

    x_train = features[['lead_time', 'margin', 'bounce_rate',
                        'ff', 'lost_recency', 'success_recency']]

    features_rank_as = apply_topsis_franchisee(features=features,
                                               x_train=x_train,
                                               weights=weights_as,
                                               cutoff_percentage=low_volume_cutoff,
                                               volume_fraction=volume_fraction)

    logger.info('applied topsis for franchisee as')

    features_rank_pr = apply_topsis_franchisee(features=features,
                                               x_train=x_train,
                                               weights=weights_pr,
                                               cutoff_percentage=low_volume_cutoff,
                                               volume_fraction=volume_fraction)

    logger.info('applied topsis for franchisee pr')

    features_rank_as.loc[:, 'request_type'] = 'AS/MS'
    features_rank_pr.loc[:, 'request_type'] = 'PR'

    features_rank = pd.concat([features_rank_as, features_rank_pr])

    return features_rank

