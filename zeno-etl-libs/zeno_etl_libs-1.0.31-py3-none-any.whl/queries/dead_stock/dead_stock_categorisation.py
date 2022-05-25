# import os
# import sys
#
# sys.path.append('../../../..')
#
import pandas as pd
import datetime
import numpy as np
import argparse
import os
from zeno_etl_libs.queries.dead_stock import dead_stock_queries


def dead_data_prep(store_id=None, days=270, logger=None, connection = None):

    # from zeno_etl_libs.db.db import DB
    # parser = argparse.ArgumentParser(description="This is ETL script.")
    # parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    # args, unknown = parser.parse_known_args()
    # env = args.env
    # os.environ['env'] = env
    # rs_db = DB()
    # rs_db.open_connection()

    rs_db = connection

    '''Getting sales data'''
    sales_query = dead_stock_queries.sales.format(days=days, store_id=str(store_id))
    sales = rs_db.get_df(sales_query)
    # removing DC inventory
    sales_store = sales[~sales['store-id'].isin([92, 111, 156, 160, 169, 172])]

    logger.info('Sales: Distinct # of drugs' + str(sales['drug-id'].nunique()))
    logger.info('Sales: Stores' + str(sales['store-id'].nunique()))

    '''Getting inventory data'''
    inventory_query = '''
          select
            inv."store-id",
            inv."drug-id",
            avg(coalesce(ii."net-value"/ ii."actual-quantity", inv."final-ptr")) as "mean-fptr",
            sum(inv."quantity") as "inventory-oh"
        from
            "prod2-generico"."inventory-1" inv
        left join "prod2-generico"."invoice-items" ii on
            inv."invoice-item-id" = ii."franchisee-invoice-item-id"
        where
            inv.quantity > 0
            and inv."store-id" = {store_id}
        group by
            inv."store-id",
            inv."drug-id"
    '''.format(store_id=store_id)
    
    inventory = rs_db.get_df(inventory_query)
    # removing DC inventory
    inventory_store = inventory[~inventory['store-id'].isin([92, 111, 156, 160, 169, 172])]

    logger.info('Inv: Distinct # of drugs ' + str(inventory_store['drug-id'].nunique()))
    logger.info('Inv: Stores ' + str(inventory_store['store-id'].nunique()))

    store_inventory_sales = inventory_store.merge(
        sales_store, on=['store-id', 'drug-id'], how='outer',
        suffixes=('', '-y'))
    # print(store_inventory_sales.columns)
    store_inventory_sales['mean-fptr'] = store_inventory_sales['mean-fptr'].combine_first(
        store_inventory_sales['mean-fptr-y'])
    store_inventory_sales.drop('mean-fptr-y', axis=1, inplace=True)
    store_inventory_sales['quantity'].fillna(0, inplace=True)
    store_inventory_sales['inventory-oh'].fillna(0, inplace=True)
    # print('# of line items', store_inventory_sales.shape[0])
    logger.info('Distinct # of drugs', store_inventory_sales['drug-id'].nunique())
    logger.info('Store - ', store_id)

    logger.info('Total inventory count', store_inventory_sales['inventory-oh'].sum())
    logger.info('Total sales count', store_inventory_sales.quantity.sum())

    '''Getting drug and store info '''
    drug_store_info_query = '''
        select
            store.id,
            store.name,
            d.id,
            d."drug-name",
            d.type,
            d.category,
            coalesce(doi."drug-grade", 'NA') as "drug-grade"
        from
            "prod2-generico".stores store
        cross join "prod2-generico".drugs d
        left join "prod2-generico"."drug-order-info" doi on
            d.id = doi."drug-id"
            and store.id = doi."store-id"
        where
            store.id = {store_id}
    '''.format(store_id=store_id)
    
    drug_store_info = rs_db.get_df(drug_store_info_query)

    drug_store_info.columns = ['store-id', 'store-name', 'drug-id', 'drug-name',
                               'type', 'category', 'drug-grade']

    store_inventory_sales = store_inventory_sales.merge(
        drug_store_info, on=['store-id', 'drug-id'], how='left')

    #rs_db.close_connection()

    # store_inventory_sales = store_inventory_sales.merge(ptr, how='left', on='drug_id')

    return sales, inventory, store_inventory_sales


def dead_stock_categorization(
        sales, inventory, store_inventory_sales, stores_list,
        logger=None, days=270, expiry_days=120, connection = None):

    # from zeno_etl_libs.db.db import DB
    # parser = argparse.ArgumentParser(description="This is ETL script.")
    # parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    # args, unknown = parser.parse_known_args()
    # env = args.env
    # os.environ['env'] = env
    # rs_db = DB()
    # rs_db.open_connection()

    rs_db = connection
    
    '''Dead Stock Categorization
    1. Expiry - within 4 months or already expired: Return
    2. No sales at enterprise level (in 9 months): Return
    3. No sales at Store "A", but at other stores (in 9 months): Rotate
    4. FIFO dead: sold in stores but inventory created more than 9 months ago: Rotate
    '''

    # 1.
    '''Getting expired inventory data'''
    expiry_query = dead_stock_queries.expiry.format(expiry_days=expiry_days)
    expiry_barcodes = rs_db.get_df(expiry_query)

    expiry_agg = expiry_barcodes.groupby(['store-id', 'drug-id'])['quantity'].sum().reset_index()
    expiry_agg.columns = ['store-id', 'drug-id', 'expired-quantity']

    store_inventory_sales_with_exp = store_inventory_sales.merge(expiry_agg, on=['store-id', 'drug-id'], how='left')
    store_inventory_sales_with_exp['expired-quantity'].fillna(0, inplace=True)
    store_inventory_sales_with_exp['quantity-rem-after-expiry'] = (
        store_inventory_sales_with_exp['inventory-oh'] - store_inventory_sales_with_exp['expired-quantity']
    )

    logger.info('Expired to be returned: units to be returned' +
                str(store_inventory_sales_with_exp['expired-quantity'].sum()))
    logger.info('Expired to be returned: value' + str(round(
        (expiry_barcodes['value']).sum()/10000000,2)) + 'Crs')
    logger.info('Post expiry drugs inventory')
    logger.info('# of line items' + str(store_inventory_sales_with_exp.shape[0]))
    logger.info('Distinct # of drugs' + str(store_inventory_sales_with_exp['drug-id'].nunique()))
    logger.info('Stores' + str(store_inventory_sales_with_exp['store-id'].nunique()))

    # 2.
    drug_wise_sales = store_inventory_sales_with_exp[
        store_inventory_sales_with_exp['store-id'].isin(stores_list)
    ].groupby(['drug-id'])['quantity'].sum().reset_index()
    drugs_no_enterprise_sales = drug_wise_sales.loc[drug_wise_sales['quantity'] == 0, 'drug-id']
    
    drug_returns = store_inventory_sales_with_exp[
        (store_inventory_sales_with_exp['drug-id'].isin(drugs_no_enterprise_sales.values)) &
        (store_inventory_sales_with_exp['store-id'].isin(stores_list))
    ]
    store_inventory_sales_with_exp_post_returns = store_inventory_sales_with_exp[
        (~store_inventory_sales_with_exp['drug-id'].isin(drugs_no_enterprise_sales.values))
    ]
    logger.info('Drug with no enterprise sales: units to be returned' + str(drug_returns['quantity-rem-after-expiry'].sum()))
    logger.info('Drug with no enterprise sales: value' + str(round((drug_returns['mean-fptr'].astype(float)*drug_returns['quantity-rem-after-expiry'].astype(float)).sum()/10000000, 2)) + 'Crs')
    logger.info('Post returns, drugs inventory')
    logger.info('# of line items' + str(store_inventory_sales_with_exp_post_returns.shape[0]))
    logger.info('Distinct # of drugs' + str(store_inventory_sales_with_exp_post_returns['drug-id'].nunique()))
    logger.info('Stores' + str(store_inventory_sales_with_exp_post_returns['store-id'].nunique()))

    # getting barcode level info for drugs to return
    return_store_drug_comb = drug_returns['store-id'].astype(str) + '_' + drug_returns['drug-id'].astype(str)
    return_store_drug_list = str(list(
        return_store_drug_comb.values)).replace('[', '(').replace(']', ')')
    return_query = dead_stock_queries.return_and_rotation.format(
        store_drug_list=return_store_drug_list,
        inventory_type='Return',
        days=0,
        expiry_days=expiry_days)
    return_barcodes = rs_db.get_df(return_query)
    
    separate_old_inv_query = '''
        select
            concat("store-id", CONCAT('-', "drug-id")) as "store-drug-id"
        from
            "prod2-generico"."inventory-1" inv
        where
            "store-id" in {stores}
            and "drug-id" in {drugs}
            and (quantity > 0
                or ((inv.quantity != 0)
                    or (inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" > 0)))
            and "created-at" <DATEADD(d,-{days},CURRENT_DATE)
        group by
            "store-id",
            "drug-id"
    '''.format(days=days, stores=tuple(drug_returns['store-id'].unique()) + (0,0), drugs=tuple(drug_returns['drug-id'].unique()) + (0,0))
    
    separate_old_inv = rs_db.get_df(separate_old_inv_query)
    
    return_barcodes['store-drug-id'] = return_barcodes['store-id'].astype(str) + '-' + return_barcodes['drug-id'].astype(str)
    return_barcodes = return_barcodes[return_barcodes['store-drug-id'].isin(tuple(separate_old_inv['store-drug-id']))]
    return_barcodes = return_barcodes.drop(columns=['store-drug-id'])
    
    # 3.
    # store drug combination (store active for than 6 months)
    store_inventory_sales_active = store_inventory_sales_with_exp_post_returns[
        store_inventory_sales_with_exp_post_returns['store-id'].isin(stores_list)]
    store_drug_no_sale = store_inventory_sales_active.loc[
        (store_inventory_sales_active['quantity'] == 0)]
    store_drug_with_sale = store_inventory_sales_with_exp_post_returns.loc[
        (store_inventory_sales_with_exp_post_returns['quantity'] != 0)
    ]
    zippin_inventory = store_drug_no_sale.groupby(
        ['type', 'category', 'drug-id'])['quantity-rem-after-expiry'].\
        sum().reset_index()
    logger.info('Rotating inventory stats')
    logger.info('# of drugs to rotate' + str(zippin_inventory.shape[0]))
    logger.info('Quantity to be rotated' + str(zippin_inventory['quantity-rem-after-expiry'].sum()))
    logger.info('Rotation Drugs value' + str(round((store_drug_no_sale['mean-fptr'].astype(float) *store_drug_no_sale['quantity-rem-after-expiry'].astype(float)).sum()/10000000,2)) + 'Crs')
    
    # getting barcode level info for drugs to rotate
    rotate_store_drug_comb = store_drug_no_sale['store-id'].astype(str) + '-' + store_drug_no_sale['drug-id'].astype(str)
    #logger.info(list(rotate_store_drug_comb.values))
    #logger.info(len(list(rotate_store_drug_comb.values)))
    rotation_drug_list = str(list(
        rotate_store_drug_comb.values)).replace('[', '(').replace(']', ')')
    if len(list(rotate_store_drug_comb.values))==0:
        rotation_drug_list = [0]
        rotation_drug_list = str(list(rotation_drug_list)).replace('[', '(').replace(']', ')')

    rotation_query = dead_stock_queries.return_and_rotation.format(
            store_drug_list=rotation_drug_list,
            inventory_type='Rotate',
            days=0,
            expiry_days=expiry_days)
    rotation_barcodes = rs_db.get_df(rotation_query)
    
    separate_old_inv_query = '''
        select
            concat("store-id", CONCAT('-', "drug-id")) as "store-drug-id"
        from
            "prod2-generico"."inventory-1" inv
        where
            "store-id" in {stores}
            and "drug-id" in {drugs}
            and (quantity > 0
                or ((inv.quantity != 0)
                    or (inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" > 0)))
            and "created-at" < Dateadd(d,-{days},CURRENT_DATE)
        group by
            "store-id",
            "drug-id"     
    '''.format(days=days,stores=tuple(store_drug_no_sale['store-id'].unique()) + (0,0), drugs=tuple(store_drug_no_sale['drug-id'].unique()) + (0,0))
    
    separate_old_inv = rs_db.get_df(separate_old_inv_query)
    
    rotation_barcodes['store-drug-id'] = rotation_barcodes['store-id'].astype(str) + '-' + rotation_barcodes['drug-id'].astype(str)
    rotation_barcodes = rotation_barcodes[rotation_barcodes['store-drug-id'].isin(tuple(separate_old_inv['store-drug-id']))]
    rotation_barcodes = rotation_barcodes.drop(columns=['store-drug-id'])

    
    # 4.
    fifo_drug = store_drug_with_sale.loc[store_drug_with_sale['inventory-oh'] != 0,
                                     ['store-id', 'drug-id']].drop_duplicates()
    fifo_drug_list = fifo_drug['store-id'].astype(str) + '-' + fifo_drug['drug-id'].astype(str)
    fifo_drug_list = str(list(fifo_drug_list)).replace('[','(').replace(']',')')

    #print('fifo drug list - {}'.format(fifo_drug_list))
    fifo_query = dead_stock_queries.return_and_rotation.format(
            store_drug_list=fifo_drug_list,
            inventory_type='FIFO Dead',
            days=days,
            expiry_days=expiry_days)
    # logger.info(fifo_query)
    fifo_barcodes = rs_db.get_df(fifo_query)
    
    logger.info('FIFO dead stock stats')
    logger.info('Quantity to be rotated' + str(fifo_barcodes['quantity'].sum()))
    logger.info('FIFO Drugs value' + str(round((fifo_barcodes['fptr'].astype(float) *fifo_barcodes['quantity'].astype(float)).sum()/10000000,2)) + 'Crs')

    # rs_db.close_connection()

    return zippin_inventory, store_drug_no_sale, store_drug_with_sale,        expiry_barcodes, return_barcodes, rotation_barcodes, fifo_barcodes


def dead_value_bucket(dead_rotate):
    dead_rotate = dead_rotate.groupby('inventory-id')['value'].        sum().reset_index()
    dead_rotate = dead_rotate.sort_values('value', ascending=False)
    dead_rotate['cumsum-percentage'] = (
        dead_rotate['value'].cumsum()/dead_rotate['value'].sum())
    dead_rotate['bucket'] = np.select(
        [dead_rotate['cumsum-percentage'] <= 0.01,
         (dead_rotate['cumsum-percentage'] > 0.01) &
         (dead_rotate['cumsum-percentage'] <= 0.02),
         (dead_rotate['cumsum-percentage'] > 0.02) &
         (dead_rotate['cumsum-percentage'] <= 0.05),
         (dead_rotate['cumsum-percentage'] > 0.05) &
         (dead_rotate['cumsum-percentage'] <= 0.10),
         (dead_rotate['cumsum-percentage'] > 0.10) &
         (dead_rotate['cumsum-percentage'] <= 0.20),
         (dead_rotate['cumsum-percentage'] > 0.20) &
         (dead_rotate['cumsum-percentage'] <= 0.40),
         (dead_rotate['cumsum-percentage'] > 0.40) &
         (dead_rotate['cumsum-percentage'] <= 0.60),
         (dead_rotate['cumsum-percentage'] > 0.60) &
         (dead_rotate['cumsum-percentage'] <= 0.80),
         dead_rotate['cumsum-percentage'] > 0.80
         ],
        ['under 1%', '1-2%', '2-5%', '5-10%', '10-20%', '20-40%',
         '40-60%', '60-80%', 'more than 80%'])
    return dead_rotate

