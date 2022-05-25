import pandas as pd
import numpy as np
import datetime


def moving_average_std(df, k=8):
    k_sales = df.reset_index(drop=True)
    max_index = max(k_sales.index)
    k_sales = k_sales.loc[max_index - k + 1:max_index]
    std_pop = np.std(k_sales['net_sales_quantity'])
    return round(std_pop)


def moving_average(df, k=8, horizon=4):
    drug_id = df['drug_id'].unique()[0]
    start_index = max(df.index)
    start_date = df.date.max()
    date_list = [start_date + datetime.timedelta(days=d*7) for d in range(1, horizon+1)]
    fcst = [0] * horizon

    for i in range(horizon):
        fcst[i] = round((
            sum(fcst[:i]) +
            df.loc[start_index - k + 1 + i:start_index,'net_sales_quantity'].sum()
        )/k)
    std = moving_average_std(df)
    fcst_df = pd.DataFrame({'drug_id': drug_id, 'date': date_list, 'fcst': fcst, 'std': std})
    return fcst_df
