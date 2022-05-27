# !pip install zeno_etl_libs==1.0.27

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: To generate forecast and replenishment figures for Warehouse
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import norm
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

from zeno_etl_libs.utils.warehouse.data_prep.wh_data_prep import wh_data_prep
from zeno_etl_libs.utils.warehouse.forecast.forecast_main import wh_forecast
from zeno_etl_libs.utils.warehouse.safety_stock.wh_safety_stock import \
    wh_safety_stock_calc
from zeno_etl_libs.utils.ipc.doid_update_ss import doid_update
from zeno_etl_libs.helper.parameter.job_parameter import parameter

# runtime variables
job_params = parameter.get_params(job_id=4)
ss_runtime_var = {'lead_time_mean': job_params['lead_time_mean'],
                  'lead_time_std': job_params['lead_time_std'],
                  'service_level': job_params['service_level'],
                  'ordering_freq': job_params['ordering_freq'],
                  'max_review_period': job_params['max_review_period'],
                  'z': round(norm.ppf(job_params['service_level']), 2),
                  'for_next_month': job_params['for_next_month'],
                  'cap_ss_days': job_params['cap_ss_days']}
env = job_params['env']
os.environ['env'] = env
email_to = job_params['email_to']
debug_mode = job_params['debug_mode']
err_msg = ''
df_uri = ''
schema = job_params['schema']
reset = job_params['reset']
wh_id = job_params['wh_id']
nso_history_days = job_params['nso_history_days']
status = False

logger = get_logger()
logger.info("Scripts begins")
logger.info("Run time variables --> " + str(ss_runtime_var))

# getting run date for the script
reset_date = str(datetime.now(tz=gettz('Asia/Kolkata')).date())
current_month_date = (
        datetime.now(tz=gettz('Asia/Kolkata')).date() -
        timedelta(days=datetime.now(tz=gettz('Asia/Kolkata')).day - 1))

if ss_runtime_var['for_next_month'] == 'Y':
    forecast_date = str(
        datetime(current_month_date.year +
                 int(current_month_date.month / 12),
                 ((current_month_date.month % 12) + 1), 1).date())
else:
    forecast_date = str(current_month_date)

try:
    rs_db = DB()
    rs_db.open_connection()
    logger.info('reading input file to get expected_nso')
    params_table_query = """
            select
                "month-begin-dt" as month_begin_dt,
                value as expected_nso
            from
                "prod2-generico"."wh-forecast-repln-input"
            where
                "param-name" = 'expected_nso'
        """
    params_table = rs_db.get_df(params_table_query)
    logger.info('expected_nso parameter read')
    params_table = params_table.apply(pd.to_numeric, errors='ignore')

    params_table['month_begin_dt'] = params_table['month_begin_dt'].astype(str)

    try:
        expected_nso = int(params_table[
                               params_table[
                                   'month_begin_dt'] == forecast_date][
                               'expected_nso'])
    except Exception as error:
        expected_nso = 0

    store_query = '''
        select
            "id",
            name,
            "opened-at" as opened_at
        from
            "prod2-generico".stores
        where
            "name" <> 'Zippin Central'
            and "is-active" = 1
            and "opened-at" != '0101-01-01 00:00:00'
            and id not in (92, 52)
    '''
    stores = rs_db.get_df(store_query)
    store_id_list = list(stores['id'])

    new_drug_entries = pd.DataFrame()
    missed_entries = pd.DataFrame()

    # CONSIDERING DRUG TYPES FOR DATA LOAD
    type_list = rs_db.get_df(
        'select distinct type from "prod2-generico".drugs')
    type_list = tuple(type_list[
                          ~type_list.type.isin(
                              ['', 'banned', 'discontinued-products'])][
                          'type'])

    # RUNNING DATA PREPARATION
    drug_sales_monthly, wh_drug_list, drug_history = wh_data_prep(
        store_id_list, current_month_date, reset_date, type_list, rs_db, logger,
        ss_runtime_var, schema)
    drug_sales_monthly = drug_sales_monthly.astype(int, errors='ignore')
    drug_history = drug_history.astype(int, errors='ignore')
    drug_sales_monthly['reset_date'] = reset_date

    # FORECASTING
    train, train_error, predict, wh_train, wh_train_error, wh_predict = wh_forecast(
        drug_sales_monthly, wh_drug_list, drug_history, logger)

    train['wh_id'] = wh_id
    train_error['wh_id'] = wh_id
    predict['wh_id'] = wh_id
    wh_train['wh_id'] = wh_id
    wh_train_error['wh_id'] = wh_id
    wh_predict['wh_id'] = wh_id
    train['forecast_date'] = forecast_date
    train_error['forecast_date'] = forecast_date
    predict['forecast_date'] = forecast_date
    wh_train['forecast_date'] = forecast_date
    wh_train_error['forecast_date'] = forecast_date
    wh_predict['forecast_date'] = forecast_date

    # SAFETY STOCK CALCULATIONS
    last_actual_month = drug_sales_monthly['month_begin_dt'].max()
    last_month_sales = drug_sales_monthly[
        drug_sales_monthly['month_begin_dt'] == str(last_actual_month)]
    last_month_sales = last_month_sales[['drug_id', 'net_sales_quantity']]
    last_month_sales.rename(
        columns={'net_sales_quantity': 'last_month_sales'}, inplace=True)
    wh_safety_stock_df = wh_safety_stock_calc(
        ss_runtime_var, wh_drug_list, wh_predict, last_month_sales,
        logger, expected_nso, nso_history_days, rs_db)
    wh_safety_stock_df['wh_id'] = wh_id
    wh_safety_stock_df['reset_date'] = str(reset_date)
    rs_db.close_connection()

    # WRITING TO POSTGRES
    s3 = S3()
    rs_db_write = DB()
    rs_db_write.open_connection()

    created_at = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    if debug_mode == 'N' and reset == 'Y':
        # drug_sales_monthly
        drug_sales_monthly['created-at'] = created_at
        drug_sales_monthly['created-by'] = 'etl-automation'
        drug_sales_monthly['updated-at'] = created_at
        drug_sales_monthly['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=drug_sales_monthly, table_name='wh-drug-sales-monthly', db=rs_db_write,
                          schema='prod2-generico')

        # train
        train['type'] = 'separate'
        train['created-at'] = created_at
        train['created-by'] = 'etl-automation'
        train['updated-at'] = created_at
        train['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=train, table_name='wh-train', db=rs_db_write, schema='prod2-generico')

        # wh_train
        wh_train['type'] = 'ensemble'
        wh_train['created-at'] = created_at
        wh_train['created-by'] = 'etl-automation'
        wh_train['updated-at'] = created_at
        wh_train['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=wh_train, table_name='wh-train', db=rs_db_write, schema='prod2-generico')

        # train_error
        train_error['type'] = 'separate'
        train_error['created-at'] = created_at
        train_error['created-by'] = 'etl-automation'
        train_error['updated-at'] = created_at
        train_error['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=train_error, table_name='wh-train-error', db=rs_db_write, schema='prod2-generico')

        # wh_train_error
        wh_train_error['type'] = 'ensemble'
        wh_train_error['created-at'] = created_at
        wh_train_error['created-by'] = 'etl-automation'
        wh_train_error['updated-at'] = created_at
        wh_train_error['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=wh_train_error[train_error.columns], table_name='wh-train-error', db=rs_db_write,
                          schema='prod2-generico')

        # predict
        predict['type'] = 'separate'
        predict['created-at'] = created_at
        predict['created-by'] = 'etl-automation'
        predict['updated-at'] = created_at
        predict['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=predict, table_name='wh-predict', db=rs_db_write, schema='prod2-generico')

        # wh_predict
        wh_predict['type'] = 'ensemble'
        wh_predict['created-at'] = created_at
        wh_predict['created-by'] = 'etl-automation'
        wh_predict['updated-at'] = created_at
        wh_predict['updated-by'] = 'etl-automation'
        s3.write_df_to_db(df=wh_predict, table_name='wh-predict', db=rs_db_write, schema='prod2-generico')

        # wh_safety_stock_df
        wh_safety_stock_df['ptr'] = ''
        wh_safety_stock_df['fcst'] = wh_safety_stock_df['fcst'].astype(int)
        wh_safety_stock_df['safety_stock'] = wh_safety_stock_df['safety_stock'].fillna(0).astype(int)
        wh_safety_stock_df['month'] = wh_safety_stock_df['month'].astype(int)
        wh_safety_stock_df['year'] = wh_safety_stock_df['year'].astype(int)
        wh_safety_stock_df['ss_wo_cap'] = wh_safety_stock_df['ss_wo_cap'].astype(int)
        wh_safety_stock_df['reorder_point'] = wh_safety_stock_df['reorder_point'].astype(int)
        wh_safety_stock_df['order_upto_point'] = wh_safety_stock_df['order_upto_point'].astype(int)
        wh_safety_stock_df['shelf_min'] = wh_safety_stock_df['shelf_min'].fillna(0).astype(int)
        wh_safety_stock_df['shelf_max'] = wh_safety_stock_df['shelf_max'].fillna(0).astype(int)
        wh_safety_stock_df['rop_without_nso'] = wh_safety_stock_df['rop_without_nso'].astype(int)
        wh_safety_stock_df['oup_without_nso'] = wh_safety_stock_df['oup_without_nso'].astype(int)
        wh_safety_stock_df['created_at'] = created_at
        wh_safety_stock_df['created_by'] = 'etl-automation'
        wh_safety_stock_df['updated_at'] = created_at
        wh_safety_stock_df['updated_by'] = 'etl-automation'
        columns = [c.replace('-', '_') for c in ['drug-id', 'drug-name', 'type', 'category', 'company', 'ptr', 'bucket',
                                                 'history-bucket', 'fcst', 'final-fcst', 'forecast-type', 'model',
                                                 'month', 'month-begin-dt', 'std', 'year', 'wh-id', 'forecast-date',
                                                 'lead-time-mean', 'lead-time-std', 'max-review-period',
                                                 'ordering-freq',
                                                 'service-level', 'z-value', 'demand-daily', 'demand-daily-deviation',
                                                 'safety-stock', 'launch-stock-per-store', 'expected-nso',
                                                 'rop-without-nso', 'reorder-point', 'oup-without-nso',
                                                 'order-upto-point', 'shelf-min', 'shelf-max', 'last-month-sales',
                                                 'safety-stock-days',
                                                 'reorder-point-days', 'order-upto-days', 'reset-date','created-at',
                                                 'created-by', 'updated-at', 'updated-by', 'cap_ss_days', 'ss_wo_cap']]
        wh_safety_stock_df = wh_safety_stock_df[columns]
        s3.write_df_to_db(df=wh_safety_stock_df, table_name='wh-safety-stock', db=rs_db_write,
                          schema='prod2-generico')

        # UPLOADING SAFETY STOCK NUMBERS IN DRUG-ORDER-INFO
        ss_data_upload = wh_safety_stock_df.query('order_upto_point > 0')[
            ['wh_id', 'drug_id', 'safety_stock', 'reorder_point',
             'order_upto_point']]
        ss_data_upload.columns = [
            'store_id', 'drug_id', 'corr_min', 'corr_ss', 'corr_max']
        new_drug_entries, missed_entries = doid_update(
            ss_data_upload, type_list, rs_db_write, schema, logger)
        logger.info('DOI updated as per request')
        logger.info('missed entries --> ' + str(missed_entries))
        logger.info('new_drug_entries entries --> ' + str(new_drug_entries))
    else:
        logger.info('DOID did not update as per request')

    rs_db_write.close_connection()
    df_uri = s3.save_df_to_s3(df=wh_safety_stock_df,
                              file_name='wh_safety_stock_{date}.csv'.format(date=str(forecast_date)))
    status = True

except Exception as error:
    err_msg = str(error)
    logger.info(str(error))
    raise error

email = Email()
if status:
    result = 'Success'
    email.send_email_file(subject=f"Warehouse forecast & replenishment ({env}): {result}",
                          mail_body=f"Run time: {datetime.now()} {err_msg}",
                          to_emails=email_to, file_uris=[df_uri])
else:
    result = 'Failed'
    email.send_email_file(subject=f"Warehouse forecast & replenishment ({env}): {result}",
                          mail_body=f"Run time: {datetime.now()} {err_msg}",
                          to_emails=email_to, file_uris=[])

# DDLs for tables
"""
create table "prod2-generico"."wh-forecast-repln-input" ( 
	"param-name" text ENCODE lzo,
	"month-begin-dt" date ENCODE az64,
	value text ENCODE lzo,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);

ALTER TABLE "prod2-generico"."wh-forecast-repln-input" owner to "admin";

CREATE TABLE "prod2-generico"."wh-safety-stock" (
	"drug-id" int8 ENCODE az64,
	"drug-name" text ENCODE lzo,
	"type" text ENCODE lzo,
	category text ENCODE lzo,
	company text ENCODE lzo,
	ptr float8 ENCODE zstd,
	bucket text ENCODE lzo,
	"history-bucket" text ENCODE lzo,
	fcst float8 ENCODE zstd,
	"final-fcst" text ENCODE lzo,
	"forecast-type" text ENCODE lzo,
	model text ENCODE lzo,
	"month" int8 ENCODE az64,
	"month-begin-dt" date ENCODE az64,
	std float8 ENCODE zstd,
	"year" int8 ENCODE az64,
	"wh-id" int8 ENCODE az64,
	"forecast-date" text ENCODE lzo,
	"lead-time-mean" int8 ENCODE az64,
	"lead-time-std" int8 ENCODE az64,
	"max-review-period" int8 ENCODE az64,
	"ordering-freq" int8 ENCODE az64,
	"service-level" float8 ENCODE zstd,
	"z-value" float8 ENCODE zstd,
	"demand-daily" float8 ENCODE zstd,
	"demand-daily-deviation" float8 ENCODE zstd,
	"safety-stock" float8 ENCODE zstd,
	"reorder-point" float8 ENCODE zstd,
	"order-upto-point" float8 ENCODE zstd,
	"shelf-min" float8 ENCODE zstd,
	"shelf-max" float8 ENCODE zstd,
	"last-month-sales" float8 ENCODE zstd,
	"safety-stock-days" float8 ENCODE zstd,
	"reorder-point-days" float8 ENCODE zstd,
	"order-upto-days" float8 ENCODE zstd,
	"reset-date" text ENCODE lzo,
	"uploaded-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"rop-without-nso" int8 ENCODE az64,
	"launch-stock-per-store" float8 ENCODE zstd,
	"expected-nso" int8 ENCODE az64,
	"oup-without-nso" int8 ENCODE az64,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);

ALTER TABLE "prod2-generico"."wh-safety-stock" owner to "admin";

CREATE TABLE "prod2-generico"."wh-drug-sales-monthly" (
	"drug-id" int8 encode az64,
	"month-begin-dt" timestamp without time zone ENCODE az64,
	"year" int8 encode az64,
	"month" int8 encode az64,
	"net-sales-quantity" float8 encode zstd,
	"first-bill-date" timestamp without time zone ENCODE az64,
	"bill-month" date ENCODE az64,
	"reset-date" text encode lzo,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);

ALTER TABLE "prod2-generico"."wh-drug-sales-monthly" owner to "admin";

create table "prod2-generico"."wh-train" ( 
	"drug-id" int8 encode az64,
	"month-begin-dt" text encode lzo,
	"year" int8 encode az64,
	"month" int8 encode az64,
	fcst float8 encode zstd,
	std float8 encode zstd,
	actual float8 encode zstd,
	ape float8 encode zstd,
	ae float8 encode zstd,
	model text encode lzo,
	"history-bucket" text encode lzo,
	"hyper-params" text encode lzo,
	"forecast-type" text encode lzo,
	"final-fcst" text encode lzo,
	"wh-id" int8 encode az64,
	"forecast-date" text encode lzo,
	"type" text encode lzo,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);

ALTER TABLE "prod2-generico"."wh-train" owner to "admin";

CREATE TABLE "prod2-generico"."wh-train-error" (
	"drug-id" int8 encode az64,
	mae float8 encode zstd,
	mape float8 encode zstd,
	model text encode lzo,
	"history-bucket" text encode lzo,
	"forecast-type" text encode lzo,
	"final-fcst" text encode lzo,
	"wh-id" int8 encode az64,
	"forecast-date" text encode lzo,
	"type" text encode lzo,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);

ALTER TABLE "prod2-generico"."wh-train-error" owner to "admin";

CREATE TABLE "prod2-generico"."wh-predict" (
	"drug-id" int8 encode az64,
	"month-begin-dt" text encode lzo,
	"year" int8 encode az64,
	"month" int8 encode az64,
	fcst float8 encode zstd,
	std float8 encode zstd,
	model text encode lzo,
	"history-bucket" text encode lzo,
	"forecast-type" text encode lzo,
	"final-fcst" text encode lzo,
	"wh-id" int8 encode az64,
	"forecast-date" text encode lzo,
	"type" text encode lzo,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);
ALTER TABLE "prod2-generico"."wh-predict" owner to "admin";

CREATE TABLE "prod2-generico"."wh-safety-stock" (
	"drug-id" int8 encode az64,
	"drug-name" text encode lzo,
	"type" text encode lzo,
	category text encode lzo,
	company text encode lzo,
	ptr float8 encode zstd,
	bucket text encode lzo,
	"history-bucket" text encode lzo,
	fcst int8 encode az64,
	"final-fcst" text encode lzo,
	"forecast-type" text encode lzo,
	model text encode lzo,
	"month" int8 encode az64,
	"month-begin-dt" date encode az64,
	std float8 encode zstd,
	"year" int8 encode az64,
	"wh-id" int8 encode az64,
	"forecast-date" date encode az64,
	"lead-time-mean" float8 encode zstd,
	"lead-time-std" float8 encode zstd,
	"max-review-period" float8 encode zstd,
	"ordering-freq" float8 encode zstd,
	"service-level" float8 encode zstd,
	"z-value" float8 encode zstd,
	"demand-daily" float8 encode zstd,
	"demand-daily-deviation" float8 encode zstd,
	"safety-stock" int8 encode az64,
	"launch-stock-per-store" float8 encode zstd,
	"expected-nso" float8 encode zstd,
	"rop-without-nso" int8 encode az64,
	"reorder-point" int8 encode az64,
	"oup-without-nso" int8 encode az64,
	"order-upto-point" int8 encode az64,
	"shelf-min" int8 encode az64,
	"shelf-max" int8 encode az64,
	"last-month-sales" int8 encode az64,
	"safety-stock-days" float8 encode zstd,
	"reorder-point-days" float8 encode zstd,
	"order-upto-days" float8 encode zstd,
	"reset-date" date encode az64,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);
ALTER TABLE "prod2-generico"."wh-safety-stock" owner to "admin";
"""

