import numpy as np


def post_processing(store_id, drug_class, weekly_fcst, safety_stock_df,
                    db, schema, logger):
    ''' getting drug name, type, grades, store name'''
    drug_id_list = tuple(drug_class.drug_id.unique())
    drug_info_query = """
        select d.id as drug_id, "drug-name" as drug_name, type,
            coalesce(doi."drug-grade", 'NA') as drug_grade
        from "{schema}".drugs d 
        left join "{schema}"."drug-order-info" doi
        on d.id = doi."drug-id"
        where d.id in {0}
        and doi."store-id" = {1}
        """.format(str(drug_id_list), store_id, schema=schema)
    drug_info = db.get_df(drug_info_query)

    q_store_name = f""" select name from "{schema}".stores where id = {store_id} """
    store_name = db.get_df(q_store_name)['name'][0]

    safety_stock_df['store_id'] = store_id
    safety_stock_df['store_name'] = store_name
    safety_stock_df = safety_stock_df.merge(
        drug_info, on='drug_id', how='left')
    safety_stock_df['drug_grade'].fillna('NA', inplace=True)
    safety_stock_df = safety_stock_df[[
        'store_id', 'store_name', 'model', 'drug_id', 'drug_name', 'type',
        'drug_grade', 'bucket', 'percentile', 'fcst', 'std',
        'lead_time_mean', 'lead_time_std', 'safety_stock', 'reorder_point',
        'order_upto_point', 'safety_stock_days', 'reorder_days',
        'order_upto_days', 'fptr', 'curr_inventory', 'max_value','correction_flag']]

    weekly_fcst['store_id'] = store_id
    weekly_fcst['store_name'] = store_name
    weekly_fcst = weekly_fcst[['store_id', 'store_name', 'model',
                               'drug_id', 'date', 'fcst', 'std']]

    drug_class['store_id'] = store_id
    drug_class['store_name'] = store_name
    drug_class = drug_class.merge(
        drug_info[['drug_id', 'drug_grade', 'type']], on='drug_id', how='left')
    drug_class['drug_grade'].fillna('NA', inplace=True)
    drug_class = drug_class[['store_id', 'store_name', 'drug_id', 'drug_grade',
                             'type', 'net_sales', 'sales_std_dev', 'sales_cov',
                             'bucket_abc', 'bucket_xyz']]

    '''Getting order value'''
    safety_stock_df['to_order_quantity'] = np.where(
        safety_stock_df['curr_inventory'] <= safety_stock_df['reorder_point'],
        safety_stock_df['order_upto_point'] - safety_stock_df['curr_inventory'], 0)

    safety_stock_df['to_order_value'] = (
        safety_stock_df['to_order_quantity'] * safety_stock_df['fptr'])

    order_value = safety_stock_df.pivot_table(
        index=['type', 'store_name', 'drug_grade'],
        values=['to_order_quantity', 'to_order_value'], aggfunc='sum',
        margins=True, margins_name='Total').reset_index()

    return drug_class, weekly_fcst, safety_stock_df, order_value
