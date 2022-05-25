'''
Author - vishal.gupta@generico.in
Objective - naive
'''
import numpy as np
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import make_future_df


# naive forecast
def naive_predict_monthly(df, horizon=3, std_dev=0.5):
    df = df.copy()
    predict_df = make_future_df(df, horizon)
    predict_df['fcst'] = np.round(df['net_sales_quantity'].values[-1])
    predict_df['std'] = np.round(df['net_sales_quantity'].mean()*std_dev)

    return predict_df
