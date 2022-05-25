'''
Author - vishal.gupta@generico.in
Objective - moving average
'''
import numpy as np
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import make_future_df
from zeno_etl_libs.utils.warehouse.forecast.errors import ape_calc, ae_calc


# MA train
def ma_train_monthly(df, k=3, out_of_sample=3):
    train = df.copy()
    train.drop(train.tail(out_of_sample).index, inplace=True)

    predict_df = make_future_df(train, out_of_sample)
    predict_df['fcst'] = np.round(
        train['net_sales_quantity'].values[-k:].mean())
    predict_df['std'] = np.round(
        np.std(train['net_sales_quantity'].values[-k:]))
    predict_df['actual'] = df['net_sales_quantity'].tail(out_of_sample).values

    predict_df['ape'] = predict_df.apply(
        lambda row: ape_calc(row['actual'], row['fcst']), axis=1)
    predict_df['ae'] = predict_df.apply(
        lambda row: ae_calc(row['actual'], row['fcst']), axis=1)

    return predict_df


# MA predict
def ma_predict_monthly(df, k=3, horizon=3):
    df = df.copy()
    predict_df = make_future_df(df, horizon)
    predict_df['fcst'] = np.round(df['net_sales_quantity'].values[-k:].mean())
    predict_df['std'] = np.round(np.std(df['net_sales_quantity'].values[-k:]))

    return predict_df
