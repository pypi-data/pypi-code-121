'''getting current ss/min/max and replacing them with new'''
import pandas as pd
import numpy as np
from zeno_etl_libs.django.api import Sql
from zeno_etl_libs.db.db import MySQL


def doid_update(data, type_list, db, schema, logger=None, gaid_omit=True):
    # GA skus to be omitted
    ga_sku_query = f"""
            select "drug-id" as drug_id
            from "{schema}"."wh-sku-subs-master" wh
            left join "{schema}".drugs d
            on d.id = wh."drug-id" 
            where d."company-id" = 6984
            """
    ga_sku = db.get_df(ga_sku_query)
    ga_sku_list = tuple(ga_sku['drug_id'])

    # import pdb; pdb.set_trace()
    new_drug_entries = pd.DataFrame()
    missed_entries = pd.DataFrame()
    data = data[['store_id', 'drug_id', 'corr_min', 'corr_ss', 'corr_max']]
    data = data.rename(columns={
        'corr_min': 'min', 'corr_ss': 'safe_stock', 'corr_max': 'max'})

    # check if gaid drugs need not to be omitted
    if gaid_omit == False:
        ga_sku_list = (0, 0)

    data = data[~data['drug_id'].isin(ga_sku_list)]

    mysql = MySQL()
    sql = Sql()
    for store_id in data['store_id'].unique():
        current_ss_query = """
            SELECT doid.id, doid.`store-id` , doid.`drug-id` , doid.min,
            doid.`safe-stock` , doid.max
            FROM `drug-order-info-data` doid 
            left join drugs d 
            on d.id = doid.`drug-id` 
            where doid.`store-id` = {store_id}
            and d.`type` in {type_list}
            and d.id not in {ga_sku_list}
            """.format(store_id=store_id,
                       type_list=type_list,
                       ga_sku_list=ga_sku_list,
                       schema=schema)
        mysql.open_connection()
        current_ss = pd.read_sql(current_ss_query, mysql.connection)
        mysql.close()
        current_ss.columns = [c.replace('-', '_') for c in current_ss.columns]

        data_store = data.loc[
            data['store_id'] == store_id,
            ['store_id', 'drug_id', 'min', 'safe_stock', 'max']]

        # Not let the code erroneously force non-gaid drugs to zero
        how = 'outer'
        if not gaid_omit:
            how = 'right'

        ss_joined = current_ss.merge(
            data_store, on=['store_id', 'drug_id'], how=how,
            suffixes=('_old', ''))
        ss_joined['min'].fillna(0, inplace=True)
        ss_joined['safe_stock'].fillna(0, inplace=True)
        ss_joined['max'].fillna(0, inplace=True)
        new_drug_entries = new_drug_entries.append(
            ss_joined[ss_joined['id'].isna()])
        ss_joined = ss_joined[~ss_joined['id'].isna()]

        logger.info('Mysql upload for store ' + str(store_id))
        logger.info('New entries ' + str(
            ss_joined[ss_joined['id'].isna()].shape[0]))

        ss_joined['flag'] = np.where(
            (ss_joined['min_old'] == ss_joined['min']) &
            (ss_joined['safe_stock_old'] == ss_joined['safe_stock']) &
            (ss_joined['max_old'] == ss_joined['max']),
            'values same', 'values changed'
        )

        ss_to_upload = ss_joined.loc[
            ss_joined['flag'] == 'values changed',
            ['id', 'min', 'safe_stock', 'max']]
        logger.info('SS to update only for ' + str(
            ss_joined[ss_joined['flag'] != 'values same'].shape[0]))

        data_to_be_updated_list = list(ss_to_upload.apply(dict, axis=1))
        if len(data_to_be_updated_list) > 0:
            chunk_size = 1000
            for i in range(0, len(data_to_be_updated_list), chunk_size):
                status, msg = sql.update(
                    {'table': 'DrugOrderInfoData',
                     'data_to_be_updated': data_to_be_updated_list[i:i+chunk_size]}, logger)
                logger.info(f"DrugOrderInfoData update API "
                            f"count: {min(i+chunk_size, len(data_to_be_updated_list))}, status: {status}, msg: {msg}")

            drug_list = str(list(ss_joined.loc[
                        ss_joined['flag'] == 'values changed', 'drug_id'].unique())
                            ).replace('[', '(').replace(']', ')')
            update_test_query = """
                    SELECT `store-id` , `drug-id` , min , `safe-stock` , max
                    from `drug-order-info-data` doid 
                    where `store-id` = {store_id}
                    and `drug-id` in {drug_list} 
                    """.format(store_id=store_id,
                               drug_list=drug_list,
                               schema=schema)
            mysql.open_connection()
            update_test = pd.read_sql(update_test_query, mysql.connection)
            mysql.close()
            update_test.columns = [c.replace('-', '_') for c in update_test.columns]

            update_test = ss_joined.loc[
                ss_joined['flag'] == 'values changed',
                ['store_id', 'drug_id', 'min', 'safe_stock', 'max']].merge(
                update_test, on=['store_id', 'drug_id'],
                suffixes=('_new', '_prod'))
            update_test['mismatch_flag'] = np.where(
                (update_test['min_new'] == update_test['min_prod']) &
                (update_test['safe_stock_new'] == update_test[
                    'safe_stock_prod']) &
                (update_test['max_new'] == update_test['max_prod']),
                'updated', 'not updated'
            )
            missed_entries = missed_entries.append(
                update_test[update_test['mismatch_flag'] == 'not updated'])
            logger.info(
                'Entries updated successfully: ' +
                str(update_test[
                        update_test['mismatch_flag'] == 'updated'].shape[0]))
            logger.info(
                'Entries not updated successfully: ' +
                str(update_test[
                        update_test['mismatch_flag'] == 'not updated'].shape[
                        0]))

    return new_drug_entries, missed_entries
