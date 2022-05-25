"""
Author      - Shubham Jangir (shubham.jangir@zeno.health)
Objective   - New stores (1 to 3 month) stock triggers (non-sales) for max corrections
            - Triggers considered are Search, PR, MS, LP, Stock transfer
            - This module to be integrated in new store safety stock algo
"""
from zeno_etl_libs.utils.new_stores.helper_functions import *

import pandas as pd
import numpy as np


def query_search(store_id, schema):
    query = f"""
    SELECT
        id,
        "store-id",
        "drug-id",
        "created-at"
    FROM
        "{schema}".searches
    WHERE
        "store-id" = {store_id}
    """
    return query


def query_patient_request(store_id, schema):
    query = f"""
    SELECT
        id,
        "store-id",
        "drug-id",
        "quantity",
        "created-at"
    FROM
        "{schema}"."short-book-1"
    WHERE
        "auto-short" = 0
        and "auto-generated" = 0
        and "store-id" = {store_id}
    """
    return query


def query_manual_short(store_id, schema):
    query = f"""
    SELECT
        id,
        "store-id",
        "drug-id",
        "quantity",
        "created-at"
    FROM
        "{schema}"."short-book-1"
    WHERE
        "auto-short" = 1
        and "home-delivery" = 0
        and "patient-id" != 4480
        and "store-id" = {store_id}
    """
    return query


def query_local_purchase(store_id, schema):
    query = f"""
        SELECT
            i."store-id",
            i."drug-id",
            i."created-at",
            ii."invoice-item-reference",
            ii."actual-quantity" as quantity,
            ii."net-value" as "lp-value"
        FROM
            "{schema}"."inventory-1" i
        LEFT JOIN
            "{schema}"."invoice-items-1" ii ON ii.id = i."invoice-item-id"
        WHERE
            i."store-id" = {store_id}
            AND ii."invoice-item-reference" IS NULL
    """
    return query


def query_stock_transfer(store_id, schema):
    query = f"""
    SELECT
        a."source-store",
        a."destination-store",
        b."inventory-id",
        c."drug-id",
        b.quantity,
        b."received-at"
    FROM
        "{schema}"."stock-transfers-1" a
    INNER JOIN "{schema}"."stock-transfer-items-1" b
        on a.id = b."transfer-id"
    LEFT JOIN "{schema}"."inventory-1" c
        on b."inventory-id" = c.id
    WHERE
        a."destination-store" = {store_id}
    """
    return query


def triggers_combined(store_id, run_date, max0_drugs_df, db, schema):
    #############################
    # Main consolidated function, for triggers
    #############################

    # Get formatted SQL queries
    q_search = query_search(store_id, schema)
    q_pr = query_patient_request(store_id, schema)
    q_ms = query_manual_short(store_id, schema)
    q_lp = query_local_purchase(store_id, schema)
    q_st = query_stock_transfer(store_id, schema)

    # Data prep, using SQL
    data_merge_c = data_prep_triggers(q_search, q_pr, q_ms, q_lp, q_st, run_date, db, schema)

    # Augment with max0 info, current inventory info, ptr info
    data_merge_c = data_augment_doi_inv(data_merge_c, store_id, max0_drugs_df, db, schema)

    # Rule for which drugs to set max for
    data_merge_c = make_keep_col(data_merge_c)

    # Some extra filters and final df
    # max_set_final is the final df at drug level
    max_set_final, max_set_summary, max_set_f_store_summary = final_reset_sku(data_merge_c, db, schema)

    return max_set_final, max_set_summary, max_set_f_store_summary


def pre_trigger_data_prep_c(data_pass, run_date):
    data = data_pass.copy()
    data['created_at'] = pd.to_datetime(data['created_at'])

    data_merge = data.copy()
    data_merge['day_diff_current'] = (data_merge['created_at'] - pd.to_datetime(run_date)).dt.days

    # Last 84days
    data_merge_before = data_merge[data_merge['day_diff_current'].between(-84, -1)].copy()
    data_merge_before['trigger_date'] = data_merge_before['created_at'].dt.date

    # Group, to calculate unique days of trigger, and trigger quantity
    data_merge_before_grp = data_merge_before.groupby(['store_id',
                                                       'drug_id']).agg({'created_at': 'count',
                                                                        'trigger_date': 'nunique',
                                                                        'quantity': 'sum'}).reset_index()
    # Rename columns
    data_merge_before_grp = data_merge_before_grp.rename(columns={'created_at': 'times_trigger',
                                                                  'trigger_date': 'days_trigger'})

    # Change to integer
    for i in ['drug_id', 'quantity']:
        data_merge_before_grp[i] = data_merge_before_grp[i].astype(int)

    return data_merge_before_grp


def data_prep_triggers(q_search, q_pr, q_ms, q_lp, q_st, run_date, db, schema):
    ########################################
    # Search
    ########################################
    data_search_c = prep_data_from_sql(q_search, db)
    data_search_c['quantity'] = 1
    data_search_grp_c = pre_trigger_data_prep_c(data_search_c, run_date)
    data_search_grp_c = data_search_grp_c.rename(columns={'times_trigger': 'times_searched',
                                                          'days_trigger': 'days_searched',
                                                          'quantity': 'quantity_searched'})

    ########################################
    # PR
    ########################################
    data_pr_c = prep_data_from_sql(q_pr, db)
    data_pr_grp_c = pre_trigger_data_prep_c(data_pr_c, run_date)
    data_pr_grp_c = data_pr_grp_c.rename(columns={'times_trigger': 'times_pr',
                                                  'days_trigger': 'days_pr',
                                                  'quantity': 'quantity_pr'})

    ########################################
    # MS
    ########################################
    data_ms_c = prep_data_from_sql(q_ms, db)
    data_ms_grp_c = pre_trigger_data_prep_c(data_ms_c, run_date)
    data_ms_grp_c = data_ms_grp_c.rename(columns={'times_trigger': 'times_ms',
                                                  'days_trigger': 'days_ms',
                                                  'quantity': 'quantity_ms'})

    ########################################
    # LP
    ########################################
    data_lp_c = prep_data_from_sql(q_lp, db)
    data_lp_grp_c = pre_trigger_data_prep_c(data_lp_c, run_date)
    data_lp_grp_c = data_lp_grp_c.rename(columns={'times_trigger': 'times_lp',
                                                  'days_trigger': 'days_lp',
                                                  'quantity': 'quantity_lp'})

    ########################################
    # Stock transfer
    ########################################
    data_st_c = prep_data_from_sql(q_st, db)

    data_st_c['received_at'] = pd.to_datetime(data_st_c['received_at'], errors='coerce')
    data_st_c = data_st_c[~data_st_c['received_at'].isnull()]

    # Exclude central stores from source-stores
    data_st_c = data_st_c[~data_st_c['source_store'].isin([52, 60, 92, 111])]

    data_st_c['store_id'] = data_st_c['destination_store']
    data_st_c['created_at'] = data_st_c['received_at']

    data_st_grp_c = pre_trigger_data_prep_c(data_st_c, run_date)
    data_st_grp_c = data_st_grp_c.rename(columns={'times_trigger': 'times_st',
                                                  'days_trigger': 'days_st',
                                                  'quantity': 'quantity_st'})

    ########################################
    # Merge all
    ########################################
    data_merge_c = data_search_grp_c.merge(data_pr_grp_c, how='outer', on=['store_id', 'drug_id'])
    data_merge_c = data_merge_c.merge(data_ms_grp_c, how='outer', on=['store_id', 'drug_id'])
    data_merge_c = data_merge_c.merge(data_lp_grp_c, how='outer', on=['store_id', 'drug_id'])
    data_merge_c = data_merge_c.merge(data_st_grp_c, how='outer', on=['store_id', 'drug_id'])

    # Fill missing values with 0
    data_merge_c = data_merge_c.fillna(0).astype(int)

    # Binary columns, which will be used later
    for i in ['times_searched', 'times_pr', 'times_ms', 'times_lp', 'times_st']:
        data_merge_c[i + '_b'] = np.where(data_merge_c[i] > 0, 1, 0)

    # Aggregate
    data_merge_c['num_triggers'] = (data_merge_c['times_searched_b'] + data_merge_c['times_pr_b'] +
                                    data_merge_c['times_ms_b'] + data_merge_c['times_lp_b'] +
                                    data_merge_c['times_st_b'])

    # Repeatable info merge
    data_r = prep_data_from_sql(Q_REPEATABLE.format(schema=schema), db)

    data_merge_c = data_merge_c.merge(data_r, how='left', on='drug_id')
    data_merge_c['is_repeatable'] = data_merge_c['is_repeatable'].fillna(0)

    # Columns about repeat event flags
    for i in ['days_searched', 'days_pr', 'days_ms', 'days_lp', 'days_st']:
        data_merge_c[i + '_r'] = np.where(data_merge_c[i] > 1, 1, 0)

    # Number of repeat triggers sum
    data_merge_c['num_repeat_triggers'] = (data_merge_c['days_searched_r'] + data_merge_c['days_pr_r'] +
                                           data_merge_c['days_ms_r'] + data_merge_c['days_lp_r'] +
                                           data_merge_c['days_st_r'])

    # Number of non search triggers
    data_merge_c['num_repeat_triggers_non_search'] = (data_merge_c['days_pr_r'] + data_merge_c['days_ms_r'] +
                                                      data_merge_c['days_lp_r'] + data_merge_c['days_st_r'])

    return data_merge_c


def data_augment_doi_inv(data_pass, store_id, max0_drugs_df, db, schema):
    # Formatted SQL queries
    # q_max0 = query_max_zero(store_id)
    q_inv = query_inventory(store_id, schema)

    data_merge_c = data_pass.copy()

    ########################################
    # Max0 drugs
    ########################################
    # connection = current_config.mysql_conn()
    # data_max0 = prep_data_from_sql(q_max0, connection)
    # data_max0['max0'] = 1

    # Take max0 from df passed
    data_max0 = max0_drugs_df.copy()
    data_max0['store_id'] = store_id
    data_max0['max0'] = 1

    ########################################
    # Current inventory
    ########################################
    q_inv = query_inventory(store_id, schema=schema)
    data_inv = prep_data_from_sql(q_inv, db)
    data_inv['curr_inv0'] = np.where(data_inv['current_inventory'] == 0, 1, 0)

    ########################################
    # PTR
    ########################################
    # SQL
    data_ptr = prep_data_from_sql(Q_PTR.format(schema=schema), db)
    data_ptr["ptr"] = data_ptr["ptr"].astype(float)

    # Merge Max info, and impute if not present
    data_merge_c = data_merge_c.merge(data_max0, how='inner', on=['store_id', 'drug_id'])
    data_merge_c['max0'] = data_merge_c['max0'].fillna(0)

    # Merge inventory and impute if not present
    data_merge_c = data_merge_c.merge(data_inv, how='left', on=['store_id', 'drug_id'])
    data_merge_c['curr_inv0'] = data_merge_c['curr_inv0'].fillna(1)

    # Merge PTR and impute an average value if null
    data_merge_c = data_merge_c.merge(data_ptr, how='left', on=['drug_id'])
    data_merge_c['ptr'] = data_merge_c['ptr'].fillna(67)

    # Max0, inv0 both
    data_merge_c['max0_inv0'] = data_merge_c['max0'] * data_merge_c['curr_inv0']

    return data_merge_c


def make_keep_col(data_pass):
    data = data_pass.copy()

    # Rule is written here, for if we want to set max for a drug
    data['keep'] = np.where(((data['num_triggers'] >= 4) |

                             ((data['num_triggers'] == 3) & (data['num_repeat_triggers'] >= 1)) |
                             ((data['num_triggers'] == 3) & (data['num_repeat_triggers'] == 0) & (
                                     data['is_repeatable'] == 1)) |

                             ((data['num_triggers'] == 2) & (data['num_repeat_triggers'] >= 2)) |
                             ((data['num_triggers'] == 2) & (data['num_repeat_triggers'] == 1) & (
                                     data['is_repeatable'] == 1)) |
                             ((data['num_triggers'] == 2) & (data['num_repeat_triggers'] == 1) & (
                                     data['num_repeat_triggers_non_search'] == 1)) |

                             ((data['num_triggers'] == 1) & (data['num_repeat_triggers'] == 1) & (
                                     data['is_repeatable'] == 1)) |
                             ((data['num_triggers'] == 1) & (data['num_repeat_triggers'] == 1) & (
                                     data['num_repeat_triggers_non_search'] == 1))
                             ),
                            1, 0)

    # Rounding off to 2 decimals
    for i in ['max0', 'curr_inv0', 'max0_inv0']:
        data[i] = np.round(data[i], 2)

    # Columns for order information
    data['sku'] = 1
    data['keep_sku'] = (data['sku'] * data['keep'] * data['max0']).astype(int)
    data['order_sku'] = (data['sku'] * data['keep'] * data['max0_inv0']).astype(int)

    data['max_value'] = data['keep_sku'] * data['ptr']
    data['order_value'] = data['order_sku'] * data['ptr']

    return data


def final_reset_sku(data_pass, db, schema):
    data_merge_c = data_pass.copy()

    ########################################
    # Some hardcoded decisions, to control inventory rise
    ########################################
    # Should be revisited later
    max_set = data_merge_c[(data_merge_c['keep_sku'] == 1)].copy()

    # Summary by triggers
    max_set_summary = max_set.groupby(['num_triggers',
                                       'num_repeat_triggers',
                                       'num_repeat_triggers_non_search',
                                       'is_repeatable']).agg({'drug_id': 'count',
                                                              'max0': 'mean',
                                                              'curr_inv0': 'mean',
                                                              'max0_inv0': 'mean'}).reset_index()

    max_set_summary = max_set_summary.rename(columns={'drug_id': 'drugs'})

    max_set_summary['is_repeatable'] = max_set_summary['is_repeatable'].astype('int')

    max_set_summary = max_set_summary.sort_values(by=['num_triggers',
                                                      'num_repeat_triggers',
                                                      'is_repeatable',
                                                      'num_repeat_triggers_non_search'],
                                                  ascending=(False, False, False, False))

    # Some high value ethical drugs, can increase order value
    max_set_f1 = max_set[max_set['ptr'] <= 300].copy()

    # Keep only 2+ triggers for now
    max_set_f2 = max_set_f1[max_set_f1['num_triggers'] >= 2].copy()

    # Stores info merge
    # SQL
    stores = prep_data_from_sql(Q_STORES.format(schema=schema), db)
    max_set_f = max_set_f2.merge(stores, how='left', on='store_id')

    # Order summary for store
    max_set_f_store_summary = max_set_f.groupby(['store_id', 'store_name'])[
        'keep_sku', 'order_sku', 'max_value', 'order_value'].sum().reset_index()
    for i in ['max_value', 'order_value']:
        max_set_f_store_summary[i] = np.round(max_set_f_store_summary[i], 0).astype(int)

    # Min, SS, Max to be set as 0,0,1
    # Can be revisited later if policy change or more confidence
    max_set_final = max_set_f[['store_id', 'drug_id']].drop_duplicates()
    max_set_final['min'] = 0
    max_set_final['safety_stock'] = 0
    max_set_final['max'] = 1

    # 'max_set_final' is the final df, at drug level
    # Rest data-frames are summary data-frames

    return max_set_final, max_set_summary, max_set_f_store_summary
