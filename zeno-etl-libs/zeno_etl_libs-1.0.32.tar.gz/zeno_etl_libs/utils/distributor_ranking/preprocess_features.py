"""preprocessing of raw data is done here"""

import pandas as pd
import numpy as np


def preprocess_features_dc(df_features, db, read_schema):
    '''df_features is the raw data variable '''

    # remove those entries where no order is given to dc or the order value doesn't exist
    df_features = df_features[(df_features['original_order'] > 0) & (
        ~df_features['original_order'].isna())]

    df_features = df_features.drop_duplicates()

    # due to stock rotation, invoice_item_id could be same. So remove duplicates.
    # Since drop duplicates drops out all na values, separate na and non na
    # and then apply drop duplicates

    df_features_1 = df_features[~df_features[
        'invoice_item_id'].isna()]
    df_features_2 = df_features[df_features['invoice_item_id'].isna()]
    df_features_1 = df_features_1.drop_duplicates(subset=['invoice_item_id'])
    # concat back na values after you separate them
    df_features = pd.concat([df_features_1, df_features_2])

    #remove cases where selling rate is 0 otherwise margin becomes infinity
    df_features = df_features[df_features['selling_rate']!=0]

    # if distributor id isn't assigned in short book then remove it.
    df_features = df_features[(~df_features['short_book_distributor_id'].isna())
                              | (~df_features['partial_distributor_id'].isna())]

    # for those cases where invoice doesn't exist, take distributor as short book distributor
    df_features['partial_distributor_id'] = df_features['partial_distributor_id'].fillna(
        df_features['short_book_distributor_id'])

    # if no dc information is present then remove those cases.
    df_features = df_features[((~df_features['partial_dc_id'].isna()) | (
        ~df_features['forward_dc_id'].isna()))]

    # for those cases where invoice doesn't exist, take invoice dc as obtained from sdm table
    df_features['partial_dc_id'] = df_features['partial_dc_id'].fillna(
        df_features['forward_dc_id'])

    df_features['partial_created_at'] = pd.to_datetime(
        df_features['partial_created_at'], errors='coerce')
    df_features['partial_invoiced_at'] = pd.to_datetime(
        df_features['partial_invoiced_at'], errors='coerce')
    df_features['original_created_at'] = pd.to_datetime(
        df_features['original_created_at'], errors='coerce')
    df_features['original_created_at_2'] = pd.to_datetime(
        df_features['original_created_at_2'], errors='coerce')

    # append number of invoices against each sb id.
    invoice_count = df_features.groupby(['short_book_1_id']).agg(
        invoice_count=('invoice_id', 'count')).reset_index()
    df_features = pd.merge(df_features, invoice_count, on=[
                           'short_book_1_id'], how='left')

    # fill those cases where no invoice is present with zero.
    df_features['invoice_count'] = df_features['invoice_count'].fillna(0)

    # to avoid cases where wrong product is received, we compare with invoice items drugs id as well.
    df_features['is_lost'] = np.where(
        (df_features['invoice_items_drug_id'] != df_features['drug_id']) | (df_features['partial_invoiced_at'].isna()), 1, 0)

    # for new drugs where drug id hasn't been assigned yet, ranking won't be generated until the drug id is assigned.
    df_features = df_features[~df_features['drug_id'].isna()]

    # remove entries for which drug type hasn't been assigned
    df_features = df_features[~df_features['drug_type'].isna()]

    # remove discontinued or banned products
    df_features = df_features[
        ~((df_features['drug_type'] == 'discontinued-products') | (df_features['drug_type'] == 'banned'))]

    # sanity check
    assert df_features[df_features['invoice_count'] ==
                       0].shape[0] == df_features[df_features['invoice_id'].isna()].shape[0]

    # filter out distributor-drugs entries
    print('pulling drug-distributor filter data')
    q_drug_distributor = """select DISTINCT "distributor-id" as "partial_distributor_id", 
                            "drug-id" as drug_id
                            from "{read_schema}"."distributor-drugs" dd """

    drug_distributor_list_filter = db.get_df(q_drug_distributor.format(read_schema=read_schema))

    df_features = pd.merge(df_features, drug_distributor_list_filter,
                           on=['partial_distributor_id', 'drug_id'],
                           how='inner', validate='many_to_one')

    return df_features


def preprocess_features_franchisee(df_features, db, read_schema):
    '''df_features is the raw data variable '''

    # remove those entries where no order is given to dc or the order value doesn't exist
    df_features = df_features[(df_features['original_order'] > 0) & (
        ~df_features['original_order'].isna())]

    df_features = df_features.drop_duplicates()

    # due to stock rotation, invoice_item_id could be same. So remove duplicates.
    # Since drop duplicates drops out all na values, separate na and non na
    # and then apply drop duplicates

    df_features_1 = df_features[~df_features[
        'invoice_item_id'].isna()]
    df_features_2 = df_features[df_features['invoice_item_id'].isna()]
    df_features_1 = df_features_1.drop_duplicates(subset=['invoice_item_id'])
    # concat back na values after you separate them
    df_features = pd.concat([df_features_1, df_features_2])

    #remove cases where selling rate is 0 otherwise margin becomes infinity
    df_features = df_features[df_features['selling_rate']!=0]

    # if distributor id isn't assigned in short book then remove it.
    df_features = df_features[(~df_features['short_book_distributor_id'].isna())
                              | (~df_features['partial_distributor_id'].isna())]

    # for those cases where invoice doesn't exist, take distributor as short book distributor
    df_features['partial_distributor_id'] = df_features['partial_distributor_id'].fillna(
        df_features['short_book_distributor_id'])

    df_features['partial_created_at'] = pd.to_datetime(
        df_features['partial_created_at'], errors='coerce')
    df_features['partial_invoiced_at'] = pd.to_datetime(
        df_features['partial_invoiced_at'], errors='coerce')
    df_features['original_created_at'] = pd.to_datetime(
        df_features['original_created_at'], errors='coerce')
    df_features['original_created_at_2'] = pd.to_datetime(
        df_features['original_created_at_2'], errors='coerce')

    # append number of invoices against each sb id.
    invoice_count = df_features.groupby(['short_book_1_id']).agg(
        invoice_count=('invoice_id', 'count')).reset_index()
    df_features = pd.merge(df_features, invoice_count, on=[
                           'short_book_1_id'], how='left')

    # fill those cases where no invoice is present with zero.
    df_features['invoice_count'] = df_features['invoice_count'].fillna(0)

    # to avoid cases where wrong product is received, we compare with invoice items drugs id as well.
    df_features['is_lost'] = np.where(
        (df_features['invoice_items_drug_id'] != df_features['drug_id']) | (df_features['partial_invoiced_at'].isna()), 1, 0)

    # for new drugs where drug id hasn't been assigned yet, ranking won't be generated until the drug id is assigned.
    df_features = df_features[~df_features['drug_id'].isna()]

    # remove entries for which drug type hasn't been assigned
    df_features = df_features[~df_features['drug_type'].isna()]

    # remove discontinued or banned products
    df_features = df_features[
        ~((df_features['drug_type'] == 'discontinued-products') | (df_features['drug_type'] == 'banned'))]

    # sanity check
    assert df_features[df_features['invoice_count'] ==
                       0].shape[0] == df_features[df_features['invoice_id'].isna()].shape[0]

    # filter out distributor-drugs entries
    print('pulling drug-distributor filter data')
    q_drug_distributor = """select DISTINCT "distributor-id" as "partial_distributor_id", 
                                "drug-id" as drug_id
                                from "{read_schema}"."distributor-drugs" dd """

    drug_distributor_list_filter = db.get_df(q_drug_distributor.format(read_schema=read_schema))

    df_features = pd.merge(df_features, drug_distributor_list_filter,
                           on=['partial_distributor_id', 'drug_id'],
                           how='inner', validate='many_to_one')

    return df_features
