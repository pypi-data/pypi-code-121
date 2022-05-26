# !/usr/bin/env python
# coding: utf-8
import os
import sys
import argparse
from datetime import datetime

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, PostGreWrite, MySQL
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.utils.general_funcs import nearest_store, month_diff

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str,
                    required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to

logger = get_logger()

logger.info(f"env: {env}")

""" DB connections """
pg_db = PostGreWrite()
pg_db.open_connection()

ms_db = MySQL()
ms_db.open_connection()

run_date = datetime.today().strftime("%Y-%m-%b")

stores_q = """
        SELECT 
            st.id AS 'store_id',
            st.name AS 'store',
            sa.`name` as `line_manager`,
            abo.name AS 'abo',
            sm.name AS 'store_manager',
            st.category AS 'store_type',
            DATE(`opened-at`) AS 'opened_at',
            CAST(st.`lat` AS DECIMAL(10,6)) AS `latitude`,
            CAST(st.`lon` AS DECIMAL(10,6)) AS `longitude`,
            st.`contact-number-1` AS `store-contact-1`,
            st.`contact-number-2` AS `store-contact-2`,
            st.`address` AS `store-address`,
            sg.name as `city`,
            case when lower(SUBSTRING(st.name, 1, 3))='b2b' then 'B2B' else 'Store' end as `store_b2b`,
            st.`franchisee-id` as franchisee_id,
            fc.`name` as `franchisee_name`
        FROM
            stores st
        LEFT JOIN
        (
            SELECT 
                us.`store-id`, u.`name`, MAX(u.`created-at`) AS `date`
            FROM
                `users-stores` AS us
            LEFT JOIN `users` AS u ON u.`id` = us.`user-id`
            WHERE
                `type` = 'area-business-owner'
            GROUP BY us.`store-id`
        ) AS abo
        ON abo.`store-id` = st.id
        LEFT JOIN
        (
            SELECT 
                us.`store-id`, 
                u.`name`, 
                MAX(u.`created-at`) AS `date`
            FROM
                `users-stores` AS us
            LEFT JOIN `users` AS u ON u.`id` = us.`user-id`
            WHERE
                `type` = 'store-manager'
            GROUP BY us.`store-id`
        ) AS sm
        ON sm.`store-id` = st.id
         LEFT JOIN
        (
            SELECT 
                us.`store-id`, 
                u.`name`, 
                MAX(u.`created-at`) AS `date`
            FROM
                `users-stores` AS us
            LEFT JOIN `users` AS u ON u.`id` = us.`user-id`
            WHERE
                `type` = 'line-manager'
            GROUP BY us.`store-id`
        ) AS sa
        ON sa.`store-id` = st.id  
        LEFT JOIN `store-groups` sg 
        on st.`store-group-id` =sg.id  
        LEFT JOIN `franchisees` fc
        on st.`franchisee-id` = fc.`id`
    """

data = pd.read_sql_query(stores_q, ms_db.connection)

# data['opened_at'] = pd.to_datetime(data['opened_at'], errors='coerce')

data['run_date'] = pd.to_datetime(run_date)

# data['date_diff'] = (data['run_date'] - data['opened_at']).dt.days

# Month diff
# data['month_diff'] = month_diff(data['run_date'], data['opened_at'])
# Filling Null values in lat lon
data['latitude'] = data['latitude'].fillna(0)
data['longitude'] = data['longitude'].fillna(0)

# Nearest store calc
data['nearest_store'] = data['store_id'].apply(lambda x: nearest_store(x,
                                                                       data,
                                                                       lat_lon_col_name=['latitude', 'longitude'],
                                                                       from_distance=5)[1:])
# data['nearest_store'] = data['nearest_store'].apply(lambda x: str(x.tolist()))
data['nearest_store'] = data['nearest_store'].apply(lambda x: x.tolist(), 1)
data['line_store'] = data['store_id']
data['line'] = "NA"
data['landmark'] = "NA"

truncate_q = """ DELETE FROM stores_master """
pg_db.engine.execute(truncate_q)

# Data type correction
data['nearest_store'] = data['nearest_store'].apply(lambda x: str(x).replace("[", "{").replace("]", "}"))

for d in tuple(data[['store_id', 'nearest_store']].values):
    query = f"""
    INSERT INTO stores_master (store_id, nearest_store) VALUES ('%s', '%s')
    """ % tuple(d)
    pg_db.engine.execute(query)

# old method
# data.to_sql(name='stores_master', con=pg_db.engine, if_exists='append', index=False, method='multi', chunksize=500)
pg_db.close_connection()
ms_db.close()
