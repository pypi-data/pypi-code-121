'''
Author - vishal.gupta@generico.in
Objective - Supporting functions for error calculations
'''
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


# absolute percentage error calculation
def ape_calc(actual, forecast):
    if (actual == 0) & (forecast == 0):
        ape = 0
    elif forecast == 0:
        ape = 1
    elif actual == 0:
        ape = 1
    else:
        ape = abs((forecast - actual)/actual)
    return ape


# abs error calculation
def ae_calc(actual, forecast):
    if (actual == 0) & (forecast == 0):
        ae = 0
    elif forecast == 0:
        ae = actual
    elif actual == 0:
        ae = forecast
    else:
        ae = abs(forecast - actual)
    return ae


# weighted mape calculation
def wmape(actual, forecast):
    wmape = sum(abs(forecast-actual))/sum(actual)
    return round(100*wmape, 1)


# avg mape, ape for the forecast horizon
def train_error(train_df):
    drug_id = train_df['drug_id'].values[-1]

    mae = np.mean(train_df['ae'])
    mape = np.mean(train_df['ape'])

    return pd.DataFrame(
        [[drug_id, mae, mape]], columns=['drug_id', 'mae', 'mape'])

def train_error_ets_h1(train_df):
    drug_id = train_df['drug_id'].values[-1]

    mae = np.mean(train_df['ae'])
    mape = np.mean(train_df['ape'])
    actual = np.mean(train_df['actual'])
    std = np.mean(train_df['std'])

    return pd.DataFrame(
        [[drug_id, mae, mape, actual, std]], columns=['drug_id', 'mae', 'mape', 'actual', 'std'])


# error reporting overall
def error_report(error_df, wh_drug_list, drug_history):
    print('MAE and MAPE error')
    error_df = error_df.copy()
    error_df['mape'] = np.round(error_df['mape'] * 100, 1)
    print(np.round(error_df.mae.mean()), error_df.mape.mean(), '\n')

    print('MAPE describe')
    print(error_df['mape'].describe(), '\n')

    print('MAPE Plots')
    fig, ax = plt.subplots()
    error_df['mape'].hist(ax=ax, bins=100, bottom=0.05)
    ax.set_yscale('log')
    ax.set_ylabel('# of SKUs')
    ax.set_xlabel('MAPE')
    print(' ', '\n')

    print('MAPE where error % > 100%')
    print(error_df.query('mape > 1').sort_values('mape')['mape'].mean(), '\n')

    print('MAE describe')
    print(error_df['mae'].describe(), '\n')

    print('MAE Plots')
    fig, ax = plt.subplots()
    error_df['mae'].hist(ax=ax, bins=100, bottom=0.05)
    ax.set_ylabel('# of SKUs')
    ax.set_xlabel('MAE')
    ax.set_yscale('log')

    print('ERROR MAPPING WITH BUCKETS AND HISTORY')
    error_bucket = error_df.merge(
        wh_drug_list[['drug_id', 'bucket']], on='drug_id').\
        merge(drug_history, on='drug_id')
    fig, ax = plt.subplots()
    error_bucket.groupby('month_history')['mape'].mean().plot()
    ax.set_ylabel('MAPE')
    ax.set_xlabel('Available history')
    print(error_bucket.groupby('bucket')['mape'].mean())

    return 0


def error_report_monthly(train_data, wh_drug_list, drug_history):
    train_data = train_data.copy()
    train_data['ape'] = np.round(train_data['ape'] * 100, 1)
    train_data['out_month'] = train_data.\
        groupby('drug_id')['month_begin_dt'].rank()

    print('MAE and MAPE error')
    print(
        train_data.groupby('out_month')['ape'].mean(),
        train_data.groupby('out_month')['ae'].mean())

    print('MAPE describe')
    print(train_data.groupby('out_month')['ape'].describe(), '\n')

    print('MAPE Plots')
    for month in train_data['out_month'].unique():
        train_data_month = train_data[train_data['out_month'] == month]
        fig, ax = plt.subplots()
        train_data_month['ape'].hist(ax=ax, bins=100, bottom=0.05)
        plt.title('MAPE: Month out {}'.format(month))
        ax.set_yscale('log')
        ax.set_ylabel('# of SKUs')
        ax.set_xlabel('APE')
        print(' ', '\n')

    print('MAPE where error % > 100%')
    print(train_data.query('ape > 1').groupby('out_month')['ape'].mean(), '\n')

    print('MAE describe')
    print(train_data.groupby('out_month')['ae'].describe(), '\n')

    print('MAE Plots')
    for month in train_data['out_month'].unique():
        train_data_month = train_data[train_data['out_month'] == month]
        fig, ax = plt.subplots()
        train_data_month['ae'].hist(ax=ax, bins=100, bottom=0.05)
        plt.title('MAE: Month out {}'.format(month))
        ax.set_yscale('log')
        ax.set_yscale('log')
        ax.set_ylabel('# of SKUs')
        ax.set_xlabel('AE')
        print(' ', '\n')

    print('ERROR MAPPING WITH BUCKETS AND HISTORY')
    train_bucket = train_data.merge(
        wh_drug_list[['drug_id', 'bucket']], on='drug_id').\
        merge(drug_history, on='drug_id')
    fig, ax = plt.subplots()

    colors = {1: 'red', 2: 'green', 3: 'blue'}
    for month in train_bucket['out_month'].unique():
        train_bucket_month = train_bucket[train_bucket['out_month'] == month]
        train_bucket_month.groupby('month_history')['ape'].mean().\
            plot(color=colors[month], title='APE: Month out {}'.format(month),
                 label=month)
        print('APE: Month out {}'.format(month))
        print(train_bucket_month.groupby('bucket')['ape'].mean())
    plt.title('APE: Month out vs Data history' + str(colors))
    ax.set_ylabel('APE')
    ax.set_xlabel('Available history')

    return 0


# weigheted mape report
def wmape_report(train_data, wh_drug_list, drug_history):
    train_data = train_data.copy()
    train_data['out_month'] = train_data.\
        groupby('drug_id')['month_begin_dt'].rank()

    print('wMAPE', wmape(train_data['actual'], train_data['fcst']))
    print('Month out wMAPE', train_data.groupby('out_month').
          apply(lambda row: wmape(row['actual'], row['fcst'])))

    train_bucket = train_data.merge(
        wh_drug_list[['drug_id', 'bucket']], on='drug_id').\
        merge(drug_history, on='drug_id')
    print('Bucket out wMAPE', train_bucket.groupby('bucket').
          apply(lambda row: wmape(row['actual'], row['fcst'])))
    print('Bucket out 1st Month wMAPE', train_bucket.query('out_month == 1').
          groupby('bucket').apply(
              lambda row: wmape(row['actual'], row['fcst'])))

    return 0
