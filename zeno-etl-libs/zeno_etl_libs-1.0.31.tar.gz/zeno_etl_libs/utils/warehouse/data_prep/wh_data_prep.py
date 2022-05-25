"""
Author - vivek.sidagam@zeno.health
Objective - Using IPC stores data prep for warehouse data prep
"""

import pandas as pd
import numpy as np


from datetime import timedelta, datetime
from calendar import monthrange
from zeno_etl_libs.utils.ipc.data_prep import forecast_data_prep


def data_checks(drug_sales_monthly, wh_drug_list, reset_date, logger,
                rs_db):
    # MONTHLY CHECKS
    logger.info(
        str(drug_sales_monthly.drug_id.nunique()) +
        str(drug_sales_monthly['month_begin_dt'].nunique()))
    logger.info(str(
        drug_sales_monthly.drug_id.nunique() *
        drug_sales_monthly['month_begin_dt'].nunique()))
    assert (drug_sales_monthly.drug_id.nunique() *
            drug_sales_monthly['month_begin_dt'].nunique()
            == len(drug_sales_monthly))

    # CHECKING FOR DRUGS NOT IN SALES DATA MONTHLY
    drug_missed_fcst = wh_drug_list[
        ~wh_drug_list.drug_id.isin(drug_sales_monthly['drug_id'])]['drug_id']
    drug_missed_fcst = str(list(drug_missed_fcst))
    drug_missed_fcst = drug_missed_fcst.replace('[', '(').replace(']', ')')
    if len(drug_missed_fcst) > 0:
        drug_missed_fcst = rs_db.get_df('''
            select
                id as drug_id,
                "drug-name" as drug_name,
                type,
                date("created-at") as creation_date
            from
                "prod2-generico".drugs
            where
                id in {}
        '''.format(drug_missed_fcst))
        drug_missed_sale_history = rs_db.get_df('''
            select
                "drug-id" as drug_id,
                date(max("created-at")) as last_sale_date
            from
                "prod2-generico".sales
            where
                "created-at" < {reset_date}
                and quantity > 0
                and "drug-id" in {drug_id_list}
            group by
                "drug-id"
        '''.format(drug_id_list = str(
            list(drug_missed_fcst['drug_id'])).replace('[', '(').replace(
            ']', ')'), reset_date = str(reset_date)))
        drug_missed_fcst = drug_missed_fcst.merge(
            drug_missed_sale_history, on='drug_id', how='inner')
        logger.info(
            'Drug in SKU list but with no history' + str(drug_missed_fcst))

        # DRUGS NOT -> DISCONTINUIED/BANNED OR NULL & SALE NOT ZERO IN 6 MONTH
        days = 152
        logger.info('Total missing sales' + str(len(drug_missed_fcst)))
        logger.info(
            'Removing unnecessary drug types' +
            str(drug_missed_fcst[
                    drug_missed_fcst.type.isin(
                        ['discontinued-products', 'banned', ''])
                ].shape[0]))
        logger.info(
            'Removing drugs with no sales in last 6 months' +
            str(drug_missed_fcst[
                    drug_missed_fcst['last_sale_date'] <=
                    (reset_date - timedelta(days=days))].shape[0]))

        drug_missed_fcst_list = drug_missed_fcst[
            (~drug_missed_fcst.type.isin(
                ['discontinued-products', 'banned', ''])) &
            (drug_missed_fcst['last_sale_date'] >
             (reset_date - timedelta(days=days)))
            ].sort_values('last_sale_date')
        logger.info('Missing drug list' + str(drug_missed_fcst_list))

    return 0

def get_product_list(rs_db):
    '''Getting product list to be kept in warehousee'''
    # TODO - IN FUTURE TO BE COMIING FROM WMS DB
    wh_drug_list_query = '''
        select
            wssm."drug-id" as drug_id,
            d."drug-name" drug_name,
            d."type",
            d.category,
            d.company,
            'NA' as bucket
        from
            "prod2-generico"."wh-sku-subs-master" wssm
        left join "prod2-generico".drugs d on
            d.id = wssm."drug-id"
        where
            wssm."add-wh" = 'Yes'
            and d."type" not in ('discontinued-products')
            and d.company <> 'GOODAID'
        '''
    wh_drug_list = rs_db.get_df(wh_drug_list_query)

    return wh_drug_list


def wh_data_prep(
        store_id_list, current_month_date, reset_date, type_list, rs_db, logger,
        ss_runtime_var, schema):
    '''Getting data prepared for warehouse forecasting'''

    # CALLING STORES DATA PREP FOR ALL STORES AS LOGIC IS SAME
    last_date = datetime(day=1, month=4, year=2021).date()
    next_month_date = datetime(current_month_date.year +
                               int(current_month_date.month / 12),
                               ((current_month_date.month % 12) + 1), 1).date()
    _, drug_sales_monthly, _ = forecast_data_prep(
        store_id_list, type_list, reset_date, rs_db, schema, logger, last_date=None,
        is_wh='Y')

    # GETTING PRODUCT LIST
    wh_drug_list = get_product_list(rs_db)
    logger.info('# of Drugs in WH list' + str(len(wh_drug_list)))

    # FILTERING OUT DRUG ID NOT CONSIDERED IN ABX-XYZ CLASSIFICATION
    drug_sales_monthly = drug_sales_monthly[
        drug_sales_monthly.drug_id.isin(wh_drug_list['drug_id'])]

    # Extrapolate current month's sales but with condition
    if ss_runtime_var['for_next_month'] == 'Y':
        curr_day = datetime.now().day - 1
        curr_month_days = monthrange(
            current_month_date.year, current_month_date.month)[1]
        drug_sales_monthly['net_sales_quantity'] = np.where(
            drug_sales_monthly['month_begin_dt'] == str(current_month_date),
            round(drug_sales_monthly['net_sales_quantity'] *
                  curr_month_days / curr_day),
            drug_sales_monthly['net_sales_quantity'])
    else:
        drug_sales_monthly = drug_sales_monthly[
            drug_sales_monthly['month_begin_dt'] != str(current_month_date)]

    # DATA CHECKS
    _ = data_checks(
        drug_sales_monthly, wh_drug_list, current_month_date, logger, rs_db)

    # FILTERING OUT LENGTH OF TIME SERIES BASED ON FIRST BILL DATE
    drug_list = drug_sales_monthly.drug_id.unique()
    bill_date_query = '''
        select
            i."drug-id" as drug_id,
            min(date(bi."created-at")) as "first_bill_date"
        from
            "prod2-generico"."bill-items-1" bi
        join "prod2-generico"."inventory-1" i on
            i.id = bi."inventory-id"
        where
            i."drug-id" in {}
        group by
            i."drug-id"
    '''.format(tuple(drug_list) + (0, 0))
    bill_date = rs_db.get_df(bill_date_query)
    bill_date['first_bill_date'] = pd.to_datetime(bill_date['first_bill_date'])
    bill_date['bill_month'] = [
        datetime(b_date.year, b_date.month, 1).date()
        for b_date in bill_date['first_bill_date']]

    # TAKING HISTORY FROM THE POINT FIRST SALE IS MADE
    drug_sales_monthly = drug_sales_monthly.merge(
        bill_date, how='left', on='drug_id')
    assert sum(drug_sales_monthly['first_bill_date'].isna()) == 0
    drug_sales_monthly = drug_sales_monthly.query(
        'month_begin_dt >= bill_month')

    # EXPLORING HISTORY OF DRUGS
    drug_history = drug_sales_monthly. \
        groupby('drug_id')['net_sales_quantity'].count().reset_index()
    drug_history.columns = ['drug_id', 'month_history']
    logger.info('Total Drugs' + str(len(drug_history)))
    logger.info('History >= 12 months' + str(
        len(drug_history.query('month_history >=12'))))
    logger.info('History 3-11 months' + str(
        len(drug_history.query('month_history < 12').
            query('month_history >=3'))))
    logger.info('History < 3 months' + str(
        len(drug_history.query('month_history < 3'))))

    return drug_sales_monthly, wh_drug_list, drug_history


def get_launch_stock_per_store(rs_db, days):
    new_stores_list_query = """
        select
            id as store_id,
            date("opened-at") as opened_at
        from
            "prod2-generico".stores s
        where
            "opened-at" >= CURRENT_DATE - {days}
            and id not in (281, 297)
            and "franchisee-id" = 1
    """.format(days=days)
    new_stores_list = rs_db.get_df(new_stores_list_query)

    store_ids_list = tuple(new_stores_list['store_id'].astype(str))

    # get shortbook launch orders
    sb_orders_query = '''
        select
            distinct sb."store-id" as store_id,
            sb."drug-id" as drug_id,
            date(sb."created-at") as created_at,
            sb.quantity as ordered_quantity,
            date(s2."opened-at") as opened_at
        from
            "prod2-generico"."short-book-1" sb
        left join "prod2-generico".stores s2 on
            s2.id = sb."store-id"
        where
            "store-id" in {store_ids}
            and date(sb."created-at") < date(s2."opened-at")
    '''.format(store_ids=store_ids_list, days=days)
    sb_orders = rs_db.get_df(sb_orders_query)

    wh_drug_list = get_product_list(rs_db)
    df = sb_orders.copy()
    df = df[df['drug_id'].isin(wh_drug_list['drug_id'])]
    df = df[['store_id', 'drug_id', 'ordered_quantity']]
    df.drop_duplicates(inplace=True)
    new_stores_count = sb_orders['store_id'].nunique()
    df = df[['drug_id', 'ordered_quantity']]
    launch_stock = df.groupby('drug_id').sum().reset_index()
    launch_stock_per_store = launch_stock.copy()
    launch_stock_per_store['ordered_quantity'] = \
        launch_stock['ordered_quantity'] / new_stores_count
    launch_stock_per_store.rename(
        columns={'ordered_quantity': 'launch_stock_per_store'}, inplace=True)

    return launch_stock_per_store
