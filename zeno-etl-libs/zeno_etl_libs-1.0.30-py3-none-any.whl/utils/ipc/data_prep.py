'''data preparation for drug forecast at store level '''
import datetime

import numpy as np
import pandas as pd


def forecast_data_prep(store_id_list, type_list, reset_date, db, schema,
                       logger=None, last_date=None, is_wh='N'):
    ''' FETCHING HISTORICAL SALES AND SALES LOSS DATA '''
    if last_date is None:
        last_date = datetime.date(day=1, month=4, year=2019)
    print('Date range', str(last_date), str(reset_date))

    # store list
    if type(store_id_list) is not list:
        store_id_list = [store_id_list]
    store_id_list = str(store_id_list).replace('[', '(').replace(']', ')')

    # drug list
    drug_list_query = """
        select id as drug_id from "{schema}".drugs where type in {0}
        """.format(type_list, schema=schema)
    drug_list = db.get_df(drug_list_query)

    # sales query
    sales_query = """
        select date("created-at") as "sales-date", "drug-id" , 
                sum("net-quantity") as "net-sales-quantity"
        from "{schema}".sales s
        where "store-id" in {store_id_list}
        and date("created-at") >= '{last_date}'
        and date("created-at") < '{reset_date}'
        group by "sales-date", "drug-id"
        """.format(
        store_id_list=store_id_list, last_date=last_date,
        reset_date=reset_date, schema=schema)
    sales_history = db.get_df(sales_query)
    sales_history.columns = [c.replace('-', '_') for c in sales_history.columns]
    calendar_query = """
        select date, year, month, "week-of-year", "day-of-week" 
        from "{schema}".calendar
        """.format(schema=schema)
    calendar = db.get_df(calendar_query)
    calendar.columns = [c.replace('-', '_') for c in calendar.columns]

    sales_history = sales_history.merge(drug_list, how='inner', on='drug_id')

    # cfr pr loss
    cfr_pr_query = f"""
        select "attributed-loss-date", "drug-id",
        sum("loss-quantity") as "loss-quantity"
        from "{schema}"."cfr-patient-request"
        where "shortbook-date" >= '{last_date}'
        and "shortbook-date" < '{reset_date}'
        and "drug-id" <> -1
        and ("drug-category" = 'chronic' or "repeatability-index" >= 40)
        and "loss-quantity" > 0
        and "drug-type" in {type_list}
        and "store-id" in {store_id_list}
        group by  "attributed-loss-date", "drug-id"
        """
    cfr_pr = db.get_df(cfr_pr_query)
    cfr_pr["loss-quantity"] = cfr_pr["loss-quantity"].astype(float)
    cfr_pr.columns = [c.replace('-', '_') for c in cfr_pr.columns]
    print(sales_history.sales_date.max())
    print(cfr_pr.attributed_loss_date.max())

    sales_history = sales_history.groupby(
        ['sales_date', 'drug_id']).sum().reset_index()

    # imputing days with no sales with zero sales
    sales_history['sales_date'] = pd.to_datetime(sales_history['sales_date'])
    sales_history = get_formatted_data(sales_history, 'drug_id', 'sales_date', 'net_sales_quantity')
    cfr_pr['attributed_loss_date'] = pd.to_datetime(cfr_pr['attributed_loss_date'])

    # total demand merge
    sales = sales_history.merge(
        cfr_pr, left_on=['sales_date', 'drug_id'],
        right_on=['attributed_loss_date', 'drug_id'], how='left')
    sales['sales_date'] = sales['sales_date'].combine_first(
        sales['attributed_loss_date'])
    sales['net_sales_quantity'].fillna(0, inplace=True)
    sales['loss_quantity'].fillna(0, inplace=True)
    sales['net_sales_quantity'] += sales['loss_quantity']
    sales.drop(['attributed_loss_date', 'loss_quantity'], axis=1, inplace=True)

    print(sales.drug_id.nunique())

    '''
    CREATING DAY-DRUG SALES CROSS TABLE
    '''
    calendar['date'] = pd.to_datetime(calendar['date'])
    sales['sales_date'] = pd.to_datetime(sales['sales_date'])
    print('Distinct drug count', sales.drug_id.nunique())
    print('No of days', sales.sales_date.nunique())
    cal_sales_weekly = calendar.loc[
        (pd.to_datetime(calendar['date']) >= sales.sales_date.min()) &
        (calendar['date'] <= sales.sales_date.max())]
    cal_sales_monthly = calendar.loc[
        (pd.to_datetime(calendar['date']) >= sales.sales_date.min()) &
        (calendar['date'] <= sales.sales_date.max())]

    # removing the first week if it has less than 7 days
    min_year = cal_sales_weekly.year.min()
    x = cal_sales_weekly.loc[(cal_sales_weekly.year == min_year)]
    min_month = x.month.min()
    x = x.loc[(x.month == min_month)]
    min_week = x.week_of_year.min()
    if x.loc[x.week_of_year == min_week].shape[0] < 7:
        print('removing dates for', min_year, min_month, min_week)
        cal_sales_weekly = cal_sales_weekly.loc[
            ~((cal_sales_weekly.week_of_year == min_week) &
              (cal_sales_weekly.year == min_year))]

    # removing the latest week if it has less than 7 days
    max_year = cal_sales_weekly.year.max()
    x = cal_sales_weekly.loc[(cal_sales_weekly.year == max_year)]
    max_month = x.month.max()
    x = x.loc[(x.month == max_month)]
    max_week = x.week_of_year.max()
    if x.loc[x.week_of_year == max_week].shape[0] < 7:
        print('removing dates for', max_year, max_month, max_week)
        cal_sales_weekly = cal_sales_weekly.loc[
            ~((cal_sales_weekly.week_of_year == max_week) &
              (cal_sales_weekly.year == max_year))]

    # adding week begin date
    cal_sales_weekly['week_begin_dt'] = cal_sales_weekly.apply(
        lambda x: x['date'] - datetime.timedelta(x['day_of_week']), axis=1)
    cal_sales_weekly['month_begin_dt'] = cal_sales_weekly.apply(
        lambda x: x['date'] - datetime.timedelta(x['date'].day - 1), axis=1)
    cal_sales_monthly['week_begin_dt'] = cal_sales_monthly.apply(
        lambda x: x['date'] - datetime.timedelta(x['day_of_week']), axis=1)
    cal_sales_monthly['month_begin_dt'] = cal_sales_monthly.apply(
        lambda x: x['date'] - datetime.timedelta(x['date'].day - 1), axis=1)

    drugs = sales[['drug_id']].drop_duplicates()
    drugs['key'] = 1

    cal_sales_weekly['key'] = 1
    cal_drug_w = drugs.merge(cal_sales_weekly, on='key', how='inner')
    cal_drug_w.drop('key', axis=1, inplace=True)
    cal_drug_sales_w = cal_drug_w.merge(
        sales, left_on=['drug_id', 'date'], right_on=['drug_id', 'sales_date'],
        how='left')
    del cal_drug_w
    cal_drug_sales_w.drop('sales_date', axis=1, inplace=True)
    cal_drug_sales_w.net_sales_quantity.fillna(0, inplace=True)

    cal_sales_monthly['key'] = 1
    cal_drug_m = drugs.merge(cal_sales_monthly, on='key', how='inner')
    cal_drug_m.drop('key', axis=1, inplace=True)
    cal_drug_sales_m = cal_drug_m.merge(
        sales, left_on=['drug_id', 'date'], right_on=['drug_id', 'sales_date'],
        how='left')
    del cal_drug_m
    cal_drug_sales_m.drop('sales_date', axis=1, inplace=True)
    cal_drug_sales_m.net_sales_quantity.fillna(0, inplace=True)

    # assertion test to check no of drugs * no of days equals total entries
    drug_count = cal_drug_sales_w.drug_id.nunique()
    day_count = cal_drug_sales_w.date.nunique()
    print('Distinct no of drugs', drug_count)
    print('Distinct dates', day_count)
    print('DF shape', cal_drug_sales_w.shape[0])
    # assert drug_count*day_count == cal_drug_sales.shape[0]

    # checking for history available and store opening date
    first_bill_query = """
        select min(date("created-at")) as bill_date from "{schema}"."bills-1"
        where "store-id" in {store_id_list}
        """.format(schema=schema, store_id_list=store_id_list)
    first_bill_date = db.get_df(first_bill_query).values[0][0]
    print(first_bill_date)

    cal_drug_sales_w = cal_drug_sales_w.query(
        'date >= "{}"'.format(first_bill_date))
    cal_drug_sales_m = cal_drug_sales_m.query(
        'date >= "{}"'.format(first_bill_date))

    '''
    AGGREGATION AT WEEKLY LEVEL
    '''
    cal_drug_sales_weekly = cal_drug_sales_w.groupby(
        ['drug_id', 'week_begin_dt', 'week_of_year']
    )['net_sales_quantity'].sum().reset_index()
    del cal_drug_sales_w
    print(cal_drug_sales_weekly.drug_id.nunique())
    # getting drug ids that havent been sold in the last 26 weeks
    n = 26
    prev_n_week_dt = (
            cal_drug_sales_weekly.week_begin_dt.max() - datetime.timedelta(n * 7))
    prev_n_week_sales = cal_drug_sales_weekly[
        cal_drug_sales_weekly['week_begin_dt'] > prev_n_week_dt]. \
        groupby('drug_id')['net_sales_quantity'].sum().reset_index()
    prev_no_sales_drug_weekly = prev_n_week_sales.loc[
        prev_n_week_sales['net_sales_quantity'] <= 0, 'drug_id'].values

    cal_drug_sales_weekly = cal_drug_sales_weekly[
        ~cal_drug_sales_weekly.drug_id.isin(prev_no_sales_drug_weekly)]
    print(cal_drug_sales_weekly.drug_id.nunique())

    cal_drug_sales_weekly.rename(
        columns={'week_begin_dt': 'date'}, inplace=True)
    validation_week = 4
    validation_weeks = cal_drug_sales_weekly['date'].drop_duplicates(). \
        nlargest(validation_week)
    print(validation_weeks)
    cal_drug_sales_weekly['sample_flag'] = np.where(
        cal_drug_sales_weekly['date'].isin(validation_weeks),
        'validation', 'insample')
    '''
    AGGREGATION AT MONTHLY LEVEL
    '''
    cal_drug_sales_monthly = cal_drug_sales_m.groupby(
        ['drug_id', 'month_begin_dt', 'year', 'month']
    )['net_sales_quantity'].sum().reset_index()
    del cal_drug_sales_m
    if is_wh == 'N':
        # removing incomplete month's sales
        cal_drug_sales_monthly = cal_drug_sales_monthly[
            cal_drug_sales_monthly.month_begin_dt != max(
                cal_drug_sales_monthly.month_begin_dt)]
    # getting drug ids that havent been sold in the 6 months
    print(cal_drug_sales_monthly.drug_id.nunique())
    n = 6
    prev_n_month_dt = cal_drug_sales_monthly[
        ['month_begin_dt']].drop_duplicates(). \
        sort_values('month_begin_dt', ascending=False
                    )['month_begin_dt'].head(n - 1)
    prev_n_month_sales = cal_drug_sales_monthly[
        cal_drug_sales_monthly['month_begin_dt'].isin(prev_n_month_dt)]. \
        groupby('drug_id')['net_sales_quantity'].sum().reset_index()
    prev_no_sales_drug_monthly = prev_n_month_sales.loc[
        prev_n_month_sales['net_sales_quantity'] <= 0, 'drug_id'].values
    # removing such drugs
    cal_drug_sales_monthly = cal_drug_sales_monthly[
        (~cal_drug_sales_monthly.drug_id.isin(prev_no_sales_drug_monthly))
    ]
    print(cal_drug_sales_monthly.drug_id.nunique())

    return cal_drug_sales_weekly, cal_drug_sales_monthly, cal_sales_weekly


def get_formatted_data(df, key_col, date_col, target_col):
    df_start = df.groupby([key_col])[date_col].min().reset_index().rename(columns={date_col: 'sales_start'})
    df = df[[key_col, date_col, target_col]]
    min_date = df[date_col].dropna().min()
    end_date = df[date_col].dropna().max()
    date_range = []
    date_range = pd.date_range(
        start=min_date,
        end=end_date,
        freq='d'
    )
    date_range = list(set(date_range) - set(df[date_col]))

    df = (
        df
            .groupby([date_col] + [key_col])[target_col]
            .sum()
            .unstack()
    )

    for date in date_range:
        df.loc[date, :] = np.nan

    df = (
        df
            .fillna(0)
            .stack()
            .reset_index()
            .rename(columns={0: target_col})
    )

    df = pd.merge(df, df_start, how='left', on=key_col)
    df = df[df[date_col] >= df['sales_start']]
    return df
