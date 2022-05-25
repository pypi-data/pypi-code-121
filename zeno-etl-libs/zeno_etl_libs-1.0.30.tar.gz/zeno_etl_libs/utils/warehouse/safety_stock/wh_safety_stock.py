"""
Author - vishal.gupta@generico.in
Objective - Inventory level calculations
"""

import numpy as np
import pandas as pd
from calendar import monthrange
from zeno_etl_libs.utils.warehouse.data_prep.wh_data_prep \
    import get_launch_stock_per_store


def wh_safety_stock_calc(
        ss_runtime_var, wh_drug_list, forecast, last_month_sales, logger=None,
        expected_nso=0, nso_history_days=90, rs_db=None):
    """ Safety stock calculation for warehouse """
    lead_time_mean = ss_runtime_var['lead_time_mean']  # 4
    lead_time_std = ss_runtime_var['lead_time_std']  # 2
    service_level = ss_runtime_var['service_level']  # 0.95
    ordering_freq = ss_runtime_var['ordering_freq']  # 4
    max_review_period = ss_runtime_var['max_review_period']  # 4
    z = ss_runtime_var['z']

    # getting latest month forecast
    forecast['month_begin_dt'] = pd.to_datetime(
        forecast['month_begin_dt']).dt.date
    first_month = forecast['month_begin_dt'].min()
    forecast_first_month = forecast[forecast['month_begin_dt'] == first_month]

    # creating inventory level dataframe
    repln = forecast_first_month.copy()
    repln['lead_time_mean'] = lead_time_mean
    repln['lead_time_std'] = lead_time_std
    repln['max_review_period'] = max_review_period
    repln['ordering_freq'] = ordering_freq
    repln['service_level'] = service_level
    repln['z_value'] = z
    repln = wh_drug_list.merge(repln, on='drug_id')
    num_days = monthrange(first_month.year, first_month.month)[1]
    repln['demand_daily'] = repln['fcst'] / num_days
    repln['demand_daily_deviation'] = repln['std'] / np.sqrt(num_days)

    # warehouse overall safety stock
    repln['safety_stock'] = np.round(repln['z_value'] * np.sqrt(
        (
                repln['lead_time_mean'] *
                repln['demand_daily_deviation'] *
                repln['demand_daily_deviation']
        ) +
        (
                repln['lead_time_std'] *
                repln['lead_time_std'] *
                repln['demand_daily'] *
                repln['demand_daily']
        )))
    repln['rop_without_nso'] = np.round(
        repln['safety_stock'] + repln['demand_daily'] * (
                repln['lead_time_mean'] + repln['max_review_period']))

    # tweaking ROP to include launch stock
    launch_stock_per_store = get_launch_stock_per_store(rs_db, nso_history_days)
    repln = repln.merge(launch_stock_per_store, on='drug_id', how='left')
    repln['launch_stock_per_store'].fillna(0, inplace=True)
    repln['expected_nso'] = expected_nso
    repln['reorder_point'] = repln['rop_without_nso'] + \
                             np.round((repln['lead_time_mean'] +
                                      repln['max_review_period']) *
                                      repln['expected_nso'] / num_days) * \
                             repln['launch_stock_per_store']
    repln['reorder_point'] = np.round(repln['reorder_point'])

    repln['oup_without_nso'] = np.round(
        repln['rop_without_nso'] +
        repln['demand_daily'] * repln['ordering_freq'])
    repln['order_upto_point'] = np.round(
        repln['reorder_point'] +
        repln['demand_daily'] * repln['ordering_freq'])

    # shelf safety stock
    repln['shelf_min'] = np.round(repln['safety_stock'] / 2)
    repln['shelf_max'] = repln['safety_stock']

    # days of safety stock, reorder point and order upto point calculations
    repln = repln.merge(last_month_sales, on='drug_id', how='left')
    repln['last_month_sales'].fillna(0, inplace=True)
    repln['safety_stock_days'] = np.round(
        repln['safety_stock'] * num_days / repln['last_month_sales'], 1)
    repln['reorder_point_days'] = np.round(
        repln['reorder_point'] * num_days / repln['last_month_sales'], 1)
    repln['order_upto_days'] = np.round(
        repln['order_upto_point'] * num_days / repln['last_month_sales'], 1)

    return repln
