'''
Author - vishal.gupta@generico.in
Objective - Patient data prep for Non IPC stores
'''

import pandas as pd
import datetime


def forecast_patient_data(store_id_list, type_list, reset_date, db, schema,
                          logger=None, last_date=None):
    ''' FETCHING HISTORICAL PATIENT DATA'''
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
    drug_list_tuple = tuple(drug_list['drug_id'])

    # getting patient data
    patient_data_query = """
        select date(a."created-at") as "sales-date",
        inv."drug-id",
        count(distinct "patient-id") as "patient-count"
        from "{schema}"."bills-1" f
        join "{schema}"."bill-items-1" a on f.id = a."bill-id"
        left join "{schema}"."inventory-1" inv on a."inventory-id" = inv.id
        where date(a."created-at") >= '{last_date}'
        and date(a."created-at") <= '{reset_date}'
        and f."store-id" in {store_id_list}
        and inv."drug-id" in {drug_list}
        group by date(a."created-at"), inv."drug-id" 
        
        union all
        
        select date(a."returned-at") as "sales-date",
        inv."drug-id",
        count(distinct "patient-id")*-1 as "patient-count"
        from "{schema}"."customer-return-items-1" a
        join "{schema}"."bills-1" b on a."bill-id" = b.id
        left join "{schema}"."inventory-1" inv on a."inventory-id" = inv.id
        where date(a."returned-at") >= '{last_date}'
        and date(a."returned-at") <= '{reset_date}'
        and b."store-id" in {store_id_list}
        and inv."drug-id" in {drug_list}
        group by date(a."returned-at"), inv."drug-id"
        """.format(store_id_list=store_id_list, last_date=str(last_date),
                   reset_date=str(reset_date), drug_list=drug_list_tuple,
                   schema=schema)
    patient_data = db.get_df(patient_data_query)
    patient_data.columns = [col.replace('-', '_') for col in patient_data.columns]

    '''CREATING DAY-DRUG patient_data CROSS TABLE'''
    calendar_query = """
           select date, year, month, "week-of-year", "day-of-week" 
           from "{schema}".calendar
           """.format(schema=schema)
    calendar = db.get_df(calendar_query)
    calendar.columns = [c.replace('-', '_') for c in calendar.columns]

    calendar['date'] = pd.to_datetime(calendar['date'])
    patient_data['sales_date'] = pd.to_datetime(patient_data['sales_date'])
    print('Distinct drug count', patient_data.drug_id.nunique())
    print('No of days', patient_data.sales_date.nunique())
    cal_patient_weekly = calendar.loc[
        (pd.to_datetime(calendar['date']) >= patient_data.sales_date.min()) &
        (calendar['date'] <= patient_data.sales_date.max())]

    # removing the first week if it has less than 7 days
    min_year = cal_patient_weekly.year.min()
    x = cal_patient_weekly.loc[(cal_patient_weekly.year == min_year)]
    min_month = x.month.min()
    x = x.loc[(x.month == min_month)]
    min_week = x.week_of_year.min()
    if x.loc[x.week_of_year == min_week].shape[0] < 7:
        print('removing dates for', min_year, min_month, min_week)
        cal_patient_weekly = cal_patient_weekly.loc[
            ~((cal_patient_weekly.week_of_year == min_week) &
              (cal_patient_weekly.year == min_year))]

    # removing the latest week if it has less than 7 days
    max_year = cal_patient_weekly.year.max()
    x = cal_patient_weekly.loc[(cal_patient_weekly.year == max_year)]
    max_month = x.month.max()
    x = x.loc[(x.month == max_month)]
    max_week = x.week_of_year.max()
    if x.loc[x.week_of_year == max_week].shape[0] < 7:
        print('removing dates for', max_year, max_month, max_week)
        cal_patient_weekly = cal_patient_weekly.loc[
            ~((cal_patient_weekly.week_of_year == max_week) &
              (cal_patient_weekly.year == max_year))]

    # adding week begin date
    cal_patient_weekly['week_begin_dt'] = cal_patient_weekly.apply(
        lambda x: x['date'] - datetime.timedelta(x['day_of_week']), axis=1)

    drugs = patient_data[['drug_id']].drop_duplicates()
    drugs['key'] = 1

    cal_patient_weekly['key'] = 1
    cal_drug_w = drugs.merge(cal_patient_weekly, on='key', how='inner')
    cal_drug_w.drop('key', axis=1, inplace=True)
    cal_drug_patient_w = cal_drug_w.merge(
        patient_data, left_on=['drug_id', 'date'],
        right_on=['drug_id', 'sales_date'],
        how='left')
    cal_drug_patient_w.drop('sales_date', axis=1, inplace=True)
    cal_drug_patient_w.patient_count.fillna(0, inplace=True)

    # assertion test to check no of drugs * no of days equals total entries
    drug_count = cal_drug_patient_w.drug_id.nunique()
    day_count = cal_drug_patient_w.date.nunique()
    print('Distinct no of drugs', drug_count)
    print('Distinct dates', day_count)
    print('DF shape', cal_drug_patient_w.shape[0])
    # assert drug_count*day_count == cal_drug_sales.shape[0]

    # checking for history available and store opening date
    first_bill_query = """
        select min(date("created-at")) as bill_date 
        from "{schema}"."bills-1"
        where "store-id" in {0}
        """.format(store_id_list, schema=schema)
    first_bill_date = db.get_df(first_bill_query).values[0][0]
    print(first_bill_date)
    cal_drug_patient_w = cal_drug_patient_w.query(
        'date >= "{}"'.format(first_bill_date))

    cal_drug_patient_weekly = cal_drug_patient_w.groupby(
            ['drug_id', 'week_begin_dt', 'week_of_year']
        )['patient_count'].sum().reset_index()
    cal_drug_patient_weekly.rename(
        columns={'week_begin_dt': 'date'}, inplace=True)

    return cal_drug_patient_weekly
