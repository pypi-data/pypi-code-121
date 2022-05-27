'''
Author - vishal.gupta@generico.in
Objective - consolidate SKU max for generic drugs which are to be substituted
'''

import pandas as pd


def stores_ss_consolidation(safety_stock_df, db, schema,
                            min_column='safety_stock',
                            ss_column='reorder_point',
                            max_column='order_upto_point'):

    # getting list of SKUs to be substituted and substituted with
    wh_list_query = f"""
        select "drug-id" , "drug-id-replaced" , "same-release" 
        from "{schema}"."wh-sku-subs-master"
        where "add-wh" = 'No'
        """
    wh_list = db.get_df(wh_list_query)
    wh_list.columns = [c.replace('-', '_') for c in wh_list.columns]

    # 3 lists - to not keep, to substitute and to substitute with
    sku_reject_list = wh_list.loc[
        wh_list['same_release'] == 'NO', 'drug_id']
    sku_to_replace_list = wh_list.loc[
        wh_list['same_release'] == 'YES', 'drug_id']
    sku_substitute_list = wh_list.loc[
        wh_list['same_release'] == 'YES', 'drug_id_replaced']

    # seperating safety_stock_df where change will happen and where it wont
    sku_cnsld_list = list(sku_reject_list) + list(sku_to_replace_list) + list(sku_substitute_list)
    safety_stock_df_cnsld = safety_stock_df[
        (safety_stock_df['drug_id'].isin(sku_cnsld_list))
    ]
    print('SS to be changed due to WH ', safety_stock_df_cnsld.shape[0])
    safety_stock_df_rest = safety_stock_df[
        ~(safety_stock_df['drug_id'].isin(sku_cnsld_list))
    ]

    if len(safety_stock_df_cnsld) > 0:

        # SKU to be changed - not to keep and substitute with
        sku_reject = safety_stock_df_cnsld.merge(
            wh_list.query('same_release == "NO"')[
                ['drug_id']].drop_duplicates(),
            how='inner', on='drug_id')
        sku_to_replace = safety_stock_df_cnsld.merge(
            wh_list.query('same_release == "YES"')[
                ['drug_id', 'drug_id_replaced']].drop_duplicates(),
            how='inner', on='drug_id')
        sku_substitute = safety_stock_df_cnsld.merge(
            wh_list.query('same_release == "YES"')[
                ['drug_id_replaced']].drop_duplicates(),
            how='inner', left_on='drug_id', right_on='drug_id_replaced')
        sku_substitute.drop('drug_id_replaced', axis=1, inplace=True)
        print('SKU rejected ', sku_reject.shape[0])
        print('SKU replace ', sku_to_replace.shape[0])
        print('SKU substitute ', sku_substitute.shape[0])

        # updated ss calculation - to reject
        sku_reject_new = sku_reject.copy()
        sku_reject_new[min_column] = 0
        sku_reject_new[ss_column] = 0
        sku_reject_new[max_column] = 0

        # updated ss calculation - to replace with wh skus
        sku_substitute_new = sku_to_replace.groupby('drug_id_replaced')[
            [min_column, ss_column, max_column]].sum().reset_index()
        sku_substitute_new.rename(columns={'drug_id_replaced': 'drug_id'}, inplace=True)

        sku_to_replace_new = sku_to_replace.copy()
        sku_to_replace_new.drop('drug_id_replaced', axis=1, inplace=True)
        sku_to_replace_new[min_column] = 0
        sku_to_replace_new[ss_column] = 0
        sku_to_replace_new[max_column] = 0

        # updated ss calculation - to substitute with
        sku_substitute_new = sku_substitute.merge(
            sku_substitute_new[['drug_id', min_column, ss_column, max_column]],
            on='drug_id', suffixes=('', '_y'), how='left')
        sku_substitute_new[min_column + '_y'].fillna(0, inplace=True)
        sku_substitute_new[ss_column + '_y'].fillna(0, inplace=True)
        sku_substitute_new[max_column + '_y'].fillna(0, inplace=True)

        sku_substitute_new[min_column] = (
            sku_substitute_new[min_column] +
            sku_substitute_new[min_column + '_y'])
        sku_substitute_new[ss_column] = (
            sku_substitute_new[ss_column] +
            sku_substitute_new[ss_column + '_y'])
        sku_substitute_new[max_column] = (
            sku_substitute_new[max_column] +
            sku_substitute_new[max_column + '_y'])
        sku_substitute_new.drop(
            [min_column + '_y', ss_column + '_y',  max_column + '_y'],
            axis=1, inplace=True)

        # merging final dataframe
        safety_stock_df_prev = pd.concat(
            [sku_reject, sku_to_replace, sku_substitute],
            axis=0, ignore_index=True)
        safety_stock_df_new = pd.concat(
            [safety_stock_df_rest, sku_reject_new, sku_to_replace_new,
             sku_substitute_new], axis=0, ignore_index=True)
    else:
        safety_stock_df_new = safety_stock_df.copy()
        safety_stock_df_prev = pd.DataFrame()

    # test cases 1- pre and post count should be same
    pre_drug_count = safety_stock_df.shape[0]
    post_drug_count = safety_stock_df_new.shape[0]
    pre_max_qty = safety_stock_df[max_column].sum()
    post_max_qty = safety_stock_df_new[max_column].sum()

    if pre_drug_count == post_drug_count:
        print('WARNING: SKU count dont match after consolidation')

    print('Reduction in max quantity:',
          str(round(100*(1 - post_max_qty/pre_max_qty), 2)) + '%')

    return safety_stock_df_new, safety_stock_df_prev
