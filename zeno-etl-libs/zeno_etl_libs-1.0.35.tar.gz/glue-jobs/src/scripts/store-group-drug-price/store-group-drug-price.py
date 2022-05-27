#!/usr/bin/env python
# coding: utf-8

# =============================================================================
# author: saurav.maskar@zeno.health
# purpose: to populate store-group-drug-price
# =============================================================================

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.logger import get_logger, send_logs_via_email
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz

import json
import datetime

import argparse
import pandas as pd
import numpy as np
import traceback

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-t', '--tolerance_percentage', default=20, type=int, required=False)
parser.add_argument('-ned', '--near_expiry_days', default=90, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
email_to = args.email_to
tolerance_percentage = args.tolerance_percentage
near_expiry_days = args.near_expiry_days

os.environ['env'] = env

logger = get_logger(level='INFO')

rs_db = DB()
rs_db.open_connection()

s3 = S3()
start_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("tolerance_percentage- " + str(tolerance_percentage))
logger.info("near_expiry_days- " + str(near_expiry_days))

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

status2 = False
if env == 'dev':
    logger.info('')
    logger.info('development env setting schema and table accordingly')
    schema2 = '`test-generico`'
    table2 = '`store-group-drug-price-data`'
    temp_sales_table = '`store-group-drug-price-data`'
elif env == 'stage':
    logger.info('')
    logger.info('staging env setting schema and table accordingly')
    schema2 = '`test-generico`'
    table2 = '`store-group-drug-price-data`'
    temp_sales_table = '`store-group-drug-price-data`'
elif env == 'prod':
    logger.info('')
    logger.info('prod env setting schema and table accordingly')
    schema2 = '`prod2-generico`'
    table2 = '`store-group-drug-price`'
    temp_sales_table = '`store-group-drug-price-copy`'

# =============================================================================
# Fetching Price - where Inventory is available
# =============================================================================

query_inv_price = """
    select
        b.*,
        case
            when b."max-per-deviation-from-max-mrp" > {tolerance_percentage} then b."weighted-mrp"
            else b."mrp"
        end as "final-mrp",
        case
            when b."max-per-deviation-from-max-mrp" > {tolerance_percentage} then b."weighted-selling-rate"
            else b."selling-rate"
        end as "final-selling-rate"
    from
        (
        select
            a.*,
            ROUND(sum(a."quantity" * a."mrp") over (partition by a."store-group-id" ,
        a."drug-id"
    order by
        a.mrp desc,
        a."selling-rate" desc
            rows between unbounded preceding and
                unbounded following)/ sum(a."quantity") over (partition by a."store-group-id" ,
        a."drug-id"
    order by
        a.mrp desc,
        a."selling-rate" desc
            rows between unbounded preceding and
                unbounded following), 2) as "weighted-mrp",
            ROUND(sum(a."quantity" * a."selling-rate") over (partition by a."store-group-id" ,
        a."drug-id"
    order by
        a.mrp desc,
        a."selling-rate" desc
            rows between unbounded preceding and
                unbounded following)/ sum(a."quantity") over (partition by a."store-group-id" ,
        a."drug-id"
    order by
        a.mrp desc,
        a."selling-rate" desc
            rows between unbounded preceding and
                unbounded following), 2) as "weighted-selling-rate",
            max(a."per-deviation-from-max-mrp") over (partition by a."store-group-id" ,
            a."drug-id"
        order by
            a.mrp desc,
            a."selling-rate" desc
            rows between unbounded preceding and
                unbounded following) as "max-per-deviation-from-max-mrp"
        from
            (
            select
                row_number() over (partition by s."store-group-id" ,
                i."drug-id"
            order by
                i.mrp desc,
                i."selling-rate" desc) as "row",
                s."store-group-id",
                i."drug-id",
                sum(i.quantity) as "quantity",
                i.mrp,
                i."selling-rate",
                case
                    when i.mrp = 0 then 100
                    else
        ROUND((1 - (i.mrp / (max(i.mrp) over (partition by s."store-group-id" ,
                    i."drug-id"
            order by
                    i.mrp desc,
                    i."selling-rate" desc
            rows between unbounded preceding and
                unbounded following))))* 100, 2)
                end as "per-deviation-from-max-mrp",
                case
                    when i."selling-rate" = 0 then 100
                    else 
                ROUND((1 - (i."selling-rate" / (max(i."selling-rate") over (partition by s."store-group-id" ,
                    i."drug-id"
            order by
                    i.mrp desc,
                    i."selling-rate" 
            rows between unbounded preceding and
                unbounded following))))* 100, 2)
                end as "per-deviation-from-max-selling-rate"
            from
                "prod2-generico"."inventory-1" i
            inner join "prod2-generico".stores s
                                    on
                i."store-id" = s.id
            inner join "prod2-generico".drugs d 
                    on
                i."drug-id" = d.id
            where
                i."franchisee-inventory" = 0
                and d.schedule != 'h1'
                and i.mrp >= i."selling-rate"
                and (i.quantity > 0 )
                and i."expiry" > dateadd(day,{near_expiry_days},getdate())
            group by
                s."store-group-id" ,
                i."drug-id" ,
                i.mrp ,
                i."selling-rate") a)b
        """.format(tolerance_percentage=tolerance_percentage,near_expiry_days=near_expiry_days)
inventory_combination = rs_db.get_df(query_inv_price)
logger.info('')
logger.info('Fetched current price data where inventory is available')

final_price_inventory = inventory_combination[inventory_combination['row']==1][['store-group-id','drug-id','final-mrp','final-selling-rate']]
final_price_inventory.rename(columns={'final-mrp':'mrp',
                                      'final-selling-rate':'selling-rate'},inplace = True)


# =============================================================================
# flagged cases analysis
# =============================================================================

inventory_combination['store-group-drug'] = inventory_combination['store-group-id'].astype(str) + '-' + inventory_combination['drug-id'].astype(str)

problematic_store_group_drug = inventory_combination[inventory_combination['max-per-deviation-from-max-mrp']>tolerance_percentage]['store-group-drug'].unique().tolist()
inventory_available_total_cases = len(inventory_combination['store-group-drug'].unique())
inventory_available_flagged_cases = len(problematic_store_group_drug)
flag_percentage =  round((inventory_available_flagged_cases/inventory_available_total_cases)*100,2)

logger.info('')
logger.info(f'total inventory_available case - Store-group + Drug Combinations - {inventory_available_total_cases}')
logger.info(f'Flagged inventory_available case - Store-group + Drug Combinations - {inventory_available_flagged_cases}')
logger.info(f'flagged percentage - {flag_percentage}%')

flagged_inventory_combination = inventory_combination[inventory_combination['store-group-drug'].isin(problematic_store_group_drug)]
del flagged_inventory_combination['store-group-drug']
# flagged_inventory_combination.to_csv('D:\Store drug composition group\price_test_3.csv')

# =============================================================================
# fetching data for store-group sold but no current inventory
# =============================================================================

query_store_group_sold_but_no_inv= """
   select
        concat(invsale."store-group-id", concat('-', invsale."drug-id")) as "store-group-drug"
    from
        (
        select
            sale."store-group-id",
            sale."drug-id" ,
            inv."store-group-inventory"
        from
            (
            select
                st."store-group-id" ,
                s."drug-id"
            from
                "prod2-generico"."prod2-generico".sales s
            left join "prod2-generico".stores st
            on
                s."store-id" = st.id
            where
                date(s."created-at") > date(dateadd(d,
                -30,
                current_date))
                and s."bill-flag" = 'gross'
                and st."store-group-id" != 2
            group by
                st."store-group-id" ,
                s."drug-id")sale
        left join (
            select
                i."drug-id" ,
                s."store-group-id" ,
                sum(i.quantity) as "store-group-inventory"
            from
                "prod2-generico"."prod2-generico"."inventory-1" i
            left join "prod2-generico".stores s 
                    on
                s.id = i."store-id"
            where
                s."store-group-id" != 2
                and i."expiry" > dateadd(day,{near_expiry_days},getdate())
            group by
                s."store-group-id" ,
                i."drug-id")inv
                        on
            sale."drug-id" = inv."drug-id"
            and sale."store-group-id" = inv."store-group-id")invsale
    where
        invsale."store-group-inventory" = 0
   """.format(near_expiry_days=near_expiry_days)
store_group_sale_but_no_inv = rs_db.get_df(query_store_group_sold_but_no_inv)
logger.info('')
logger.info('Fetched data for store-group sold but no current inventory')

store_group_drug = tuple(map(str,list(store_group_sale_but_no_inv['store-group-drug'].unique())))
logger.info(f'store-group sold but no current inventory cases - {len(store_group_drug)}')


# =============================================================================
# Fetching Price for store-group sold but no current inventory
# =============================================================================

query_sale_price = """
    select
        *
    from
        (
        select
            row_number() over (partition by s."store-group-id" ,
            i."drug-id"
        order by
            i.mrp desc,
            i."selling-rate" desc) as "row",
            s."store-group-id",
            i."drug-id",
            sum(i.quantity) as "quantity",
            i.mrp,
            i."selling-rate"
        from
            "prod2-generico"."inventory-1" i
        inner join "prod2-generico".stores s
                                        on
            i."store-id" = s.id
        inner join "prod2-generico".drugs d 
                        on
            i."drug-id" = d.id
        where
            i."franchisee-inventory" = 0
            and d.schedule != 'h1'
            and i.mrp >= i."selling-rate"
            -- and i."expiry" > dateadd(day,90,getdate())
            and concat( s."store-group-id", concat('-', i."drug-id")) in {store_group_drug}
        group by
            s."store-group-id" ,
            i."drug-id" ,
            i.mrp ,
            i."selling-rate")a
    where
        a."row" = 1
   """.format(store_group_drug=store_group_drug)
non_invenotory_combination = rs_db.get_df(query_sale_price)

logger.info('')
logger.info('Fetched current price data for no current inventory available cases')
logger.info(f'price to update for non-inventory combinations for - {len(non_invenotory_combination["store-group-id"])} cases')

# Difference analysis - Why prices are not to be updated for all sold but no inventory cases
# a = pd.DataFrame(store_group_sale_but_no_inv['store-group-drug'].unique(), columns=['total'])
# b=a['total'].str.split('-',expand=True)
# b.rename(columns={0:'store_group_id_total',
#                   1:'drug_id_total'},inplace=True)
# b['store_group_id_total'] = b['store_group_id_total'].astype(int)
# b['drug_id_total'] = b['drug_id_total'].astype(int)
# c = non_invenotory_combination[['store-group-id','drug-id']]
# c.rename(columns = {'store-group-id':'store_group_id_cal',
#                     'drug-id':'drug_id_cal'},inplace =True)
# b = b.merge(c,left_on=['store_group_id_total','drug_id_total'],right_on=['store_group_id_cal','drug_id_cal'],how='left')

del non_invenotory_combination['row']
del non_invenotory_combination['quantity']

union = pd.concat([final_price_inventory, non_invenotory_combination])

# =============================================================================
# Fetching store-group and cluster combination
# =============================================================================

qc = """
        select
            sg.id as "store-group-id",
            cluster."cluster-id",
            sg."is-active" as "sg-is-active"
        from
            "prod2-generico"."store-groups" sg
        left join 
               (
            select
                s."store-group-id" as "store-group-id",
                sc."cluster-id"
            from
                "prod2-generico".features f
            join "prod2-generico"."store-features" sf on
                f.id = sf."feature-id"
            join "prod2-generico"."store-clusters" sc on
                sc."store-id" = sf."store-id"
            join "prod2-generico".stores s 
               on
                sc."store-id" = s.id
            where
                sf."feature-id" = 69
                and sf."is-active" = 1
                and sc."is-active" = 1
            group by
                s."store-group-id",
                sc."cluster-id")cluster
               on
            sg.id = cluster."store-group-id"
      """
store_group_clusters = rs_db.get_df(qc)

store_group_clusters['cluster-id'] = store_group_clusters['cluster-id'].apply(pd.to_numeric,
                                                                              errors='ignore').astype('Int64')

store_group_clusters['store-group-id'] = store_group_clusters['store-group-id'].apply(pd.to_numeric,
                                                                                      errors='ignore').astype(
    'Int64')

logger.info('')
logger.info('Fetched total store-group and cluster combinations')

# =============================================================================
# Expanding store groups to clusters
# =============================================================================

# Note - Selling rate can be made 0 where cluster inventory is not available (Meaning Out of Stock)
# But those cases will be - inventory is available in store-group but not in cluster
# Final Decision is yet to be made on this, till that time Out of stock will be based on Store-group inventory

store_group_clusters_without_ndd = store_group_clusters[store_group_clusters['store-group-id']!=2]
store_group_clusters_without_ndd['cluster-id'].fillna(-987125,inplace = True)
store_group_without_cluster = pd.DataFrame(store_group_clusters_without_ndd['store-group-id'].unique(), columns = ['store-group-id'])
store_group_without_cluster['cluster-id'] = -987125
store_group_clusters_without_ndd = store_group_clusters_without_ndd.merge(store_group_without_cluster, on=['store-group-id','cluster-id'], how='outer')

union = union.merge(store_group_clusters_without_ndd[['store-group-id','cluster-id']], on='store-group-id',how='inner')
union['cluster-id'] = union['cluster-id'].replace(-987125, np.nan)

# union.to_csv('D:\Store drug composition group\price_test_5.csv')

# =============================================================================
# updating Temp table with current data for clusters
# =============================================================================

mysql_write = MySQL(read_only=False)
mysql_write.open_connection()

try:

    temp_table_name = '`store-group-drug-price-data-temp`'

    truncate_query = '''
                  DELETE FROM {schema2}.{temp_table_name}  '''.format(schema2=schema2,temp_table_name=temp_table_name)
    mysql_write.engine.execute(truncate_query)
    logger.info('Existing store-group-drug-price-data-temp table Truncated')

    union.to_sql(
        name='store-group-drug-price-data-temp', con=mysql_write.engine,
        if_exists='append',
        chunksize=500, method='multi', index=False)
    logger.info(' ')
    logger.info('store-group-drug-price-data-temp table appended to MySQL')

    # =============================================================================
    # Updating price where Mismatch in calculated and current table
    # =============================================================================

    logger.info(' ')
    logger.info('Updating for clusters')

    for store_groups in store_group_clusters['store-group-id'].unique():
        clusters = store_group_clusters[store_group_clusters['store-group-id']==store_groups]['cluster-id'].unique()
        if (len(clusters)==1 and pd.isna(clusters[0])) or store_groups==2:
            pass
        else:
            for cluster_id in sorted(clusters):
                logger.info('')
                logger.info('store group - {}, cluster {} - started '.format(store_groups,cluster_id))

                update1_query = """
                        UPDATE
                            {schema2}.{table2} sgdp
                        INNER JOIN {schema2}.{temp_table_name} sgdp2
                            ON
                            sgdp.`store-group-id` = sgdp2.`store-group-id`
                            and sgdp.`cluster-id` = {cluster_id}
                            and sgdp2.`cluster-id` = {cluster_id}
                            and sgdp.`drug-id` = sgdp2.`drug-id`
                        SET
                            sgdp.mrp = sgdp2.mrp,
                            sgdp.`selling-rate` = sgdp2.`selling-rate`
                        WHERE
                            sgdp.`store-group-id` != 2
                             and ( sgdp.mrp != sgdp2.mrp
                                OR sgdp.`selling-rate` != sgdp2.`selling-rate`)
                           """.format(cluster_id=cluster_id, schema2=schema2, table2=table2, temp_table_name=temp_table_name)

                mysql_write.engine.execute(update1_query)

                logger.info('')
                logger.info('store group - {} cluster {} - Update 1 MRP And Selling price '.format(store_groups, cluster_id))

                # =============================================================================
                # Updating selling rate to 0 where inventory is not present
                # =============================================================================

                update2_query = """
                        UPDATE
                            {schema2}.{table2} sgdp
                        LEFT JOIN {schema2}.{temp_table_name} sgdp2
                              ON
                              sgdp.`store-group-id` = sgdp2.`store-group-id`
                              and sgdp.`cluster-id` = {cluster_id}
                              and sgdp2.`cluster-id` = {cluster_id}
                              and sgdp.`drug-id` = sgdp2.`drug-id`
                        left join drugs d 
                                on d.id = sgdp.`drug-id`
                        SET
                                sgdp.`selling-rate` = 0
                        WHERE
                                sgdp.`store-group-id` != 2
                            and d.schedule != 'h1'
                            and sgdp.`selling-rate` != 0
                            and sgdp.`cluster-id` = {cluster_id}
                            and sgdp.`store-group-id` = {store_groups}
                            and sgdp2.id is NULL
                             """.format(cluster_id=cluster_id, schema2=schema2, table2=table2, store_groups=store_groups, temp_table_name=temp_table_name)

                mysql_write.engine.execute(update2_query)

                logger.info('')
                logger.info('store group - {} cluster {} - Update 2  Selling price=0'.format(store_groups,cluster_id))

                # =============================================================================
                # Inserting data where data is not present
                # =============================================================================

                insert_query = """
                        INSERT
                            Into
                            {schema2}.{table2} 
                        (
                        `store-group-id` ,
                            `drug-id` ,
                            `cluster-id` ,
                            mrp ,
                            `selling-rate` ,
                            `is-express` ,
                            `is-active`
                        )
                        (
                            SELECT
                                sgdpdt.`store-group-id` ,
                                sgdpdt.`drug-id` ,
                                sgdpdt.`cluster-id` ,
                                sgdpdt.mrp ,
                                sgdpdt.`selling-rate` ,
                                sgdpdt.`is-express` ,
                                sgdpdt.`is-active`
                            FROM
                                {schema2}.{temp_table_name} sgdpdt
                            left join {schema2}.{table2} sgdp
                          on
                                sgdpdt.`store-group-id` = sgdp.`store-group-id`
                                and sgdpdt.`cluster-id` = {cluster_id}
                                and sgdp.`cluster-id` = {cluster_id}
                                and sgdpdt.`drug-id` = sgdp.`drug-id`
                            WHERE
                                sgdp.id is NULL
                                and sgdpdt.`store-group-id`= {store_groups}
                                and sgdpdt.`cluster-id`= {cluster_id})
                         """.format(cluster_id=cluster_id, schema2=schema2, table2=table2, temp_table_name=temp_table_name, store_groups=store_groups)

                mysql_write.engine.execute(insert_query)

                logger.info('')
                logger.info('store group - {} cluster {} - Inserted data'.format(store_groups,cluster_id))

    # =============================================================================
    # Updating for Non clusters
    # Updating price where Mismatch in calculated and current table
    # =============================================================================

    logger.info(' ')
    logger.info('Updating for non clusters')

    for store_groups in store_group_clusters['store-group-id'].unique():

        if store_groups==2:
            pass
        else:
            logger.info(' ')
            logger.info('store group- {} started'.format(store_groups))

            nc_update1_query = """
                   UPDATE
                       {schema2}.{table2} sgdp
                   INNER JOIN {schema2}.{temp_table_name} sgdp2
                       ON
                       sgdp.`store-group-id` = {store_groups}
                       and sgdp2.`store-group-id` = {store_groups}
                       and sgdp.`cluster-id` is NULL 
                       and sgdp2.`cluster-id` is NULL
                       and sgdp.`drug-id` = sgdp2.`drug-id`
                   SET
                       sgdp.mrp = sgdp2.mrp,
                       sgdp.`selling-rate` = sgdp2.`selling-rate`
                   WHERE
                       sgdp.`store-group-id` != 2
                       and sgdp.`store-group-id` = {store_groups}
                        and ( sgdp.mrp != sgdp2.mrp
                           OR sgdp.`selling-rate` != sgdp2.`selling-rate`)
                      """.format(schema2=schema2, table2=table2, temp_table_name=temp_table_name, store_groups=store_groups)

            mysql_write.engine.execute(nc_update1_query)

            logger.info('')
            logger.info('store group - {} cluster Null - Update 1 MRP And Selling price '.format(store_groups))

            # =============================================================================
            # Updating selling rate to 0 where inventory is not present
            # =============================================================================

            nc_update2_query = """
                     UPDATE
                         {schema2}.{table2} sgdp
                     LEFT JOIN {schema2}.{temp_table_name} sgdp2
                           ON
                           sgdp.`store-group-id` = {store_groups}
                           and sgdp2.`store-group-id` = {store_groups}
                           and sgdp.`cluster-id` is NULL
                           and sgdp2.`cluster-id` is NULL
                           and sgdp.`drug-id` = sgdp2.`drug-id`
                     left join drugs d 
                            on d.id = sgdp.`drug-id`
                     SET
                             sgdp.`selling-rate` = 0
                     WHERE
                             sgdp.`store-group-id` != 2
                         and d.schedule != 'h1'
                         and sgdp.`selling-rate` != 0
                         and sgdp.`cluster-id` is NULL
                         and sgdp.`store-group-id` = {store_groups}
                         and sgdp2.id is NULL
                          """.format(schema2=schema2, table2=table2, store_groups=store_groups,
                                     temp_table_name=temp_table_name)

            mysql_write.engine.execute(nc_update2_query)

            logger.info('')
            logger.info('store group - {} cluster Null - Update 2  Selling price=0'.format(store_groups))

            # =============================================================================
            # Inserting data where data is not present
            # =============================================================================

            insert_query = """
                        INSERT
                            Into
                            {schema2}.{table2} 
                        (
                        `store-group-id` ,
                            `drug-id` ,
                            `cluster-id` ,
                            mrp ,
                            `selling-rate` ,
                            `is-express` ,
                            `is-active`
                        )
                        (
                            SELECT
                                sgdpdt.`store-group-id` ,
                                sgdpdt.`drug-id` ,
                                sgdpdt.`cluster-id` ,
                                sgdpdt.mrp ,
                                sgdpdt.`selling-rate` ,
                                sgdpdt.`is-express` ,
                                sgdpdt.`is-active`
                            FROM
                                {schema2}.{temp_table_name} sgdpdt
                            left join {schema2}.{table2} sgdp
                          on
                                sgdpdt.`store-group-id` = {store_groups}
                                and sgdp.`store-group-id` = {store_groups}
                                and sgdpdt.`cluster-id` is NULL
                                and sgdp.`cluster-id` is NULL
                                and sgdpdt.`drug-id` = sgdp.`drug-id`
                            WHERE
                                sgdpdt.`store-group-id`= {store_groups}
                                and sgdpdt.`cluster-id` is NULL
                                and sgdp.id is NULL)
                         """.format( schema2=schema2, table2=table2,
                                    temp_table_name=temp_table_name, store_groups=store_groups)

            mysql_write.engine.execute(insert_query)

            logger.info('')
            logger.info('store group - {} cluster NULL - Inserted data'.format(store_groups))

    # =============================================================================
    # This is used as safety Net, Can be scrapped in few days
    # =============================================================================

    logger.info('')
    logger.info('Start - Updating Selling price = 0 cases which are billed in last month, Temporary Solution')

    sell_temp_query = """
        update
            {schema2}.{table2} s1
        inner join {schema2}.{temp_sales_table} s2
        on
            s1.`store-group-id` = s2.`store-group-id`
            and s1.`cluster-id` <=> s2.`cluster-id`
            and s1.`drug-id` = s2.`drug-id`
        set
            s1.mrp = s2.mrp,
            s1.`selling-rate` = s2.`selling-rate`
        where
            s1.`selling-rate` = 0
            and s2.`selling-rate` != 0;
    """.format(schema2=schema2, table2=table2, temp_sales_table=temp_sales_table)
    mysql_write.engine.execute(sell_temp_query)

    logger.info('')
    logger.info('End - Updating Selling price = 0 cases which are billed in last month, Temporary Solution')

    status2 = True
except:
    status2 = False

# =============================================================================
# Sending mail
# =============================================================================
if status2 is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()
cur_date = datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()

flagged_inv = s3.save_df_to_s3(df=flagged_inventory_combination, file_name='flagged_cases_{}.csv'.format(cur_date))
raw_inventory = s3.save_df_to_s3(df=inventory_combination, file_name='raw_inventory_{}.csv'.format(cur_date))
raw_sale = s3.save_df_to_s3(df=non_invenotory_combination, file_name='raw_sold_but_no_inventory_{}.csv'.format(cur_date))


email.send_email_file(subject=f"{env}-{status} : {table2} table updated",
                      mail_body=f"{table2} table update {status}, Time for job completion - {min_to_complete} mins\n"
                                f"total inventory_available case - Store-group + Drug Combinations - {inventory_available_total_cases}\n"
                                f"Flagged inventory_available case - Store-group + Drug Combinations - {inventory_available_flagged_cases}\n"
                                f"flagged percentage - {flag_percentage}%\n"
                                f"store-group sold but no current inventory cases - {len(store_group_drug)}\n"
                                f"price to update for non-inventory combinations for - {len(non_invenotory_combination['store-group-id'])} cases\n"
                                f"parameter used - \n"
                                f"tolerance_percentage - {tolerance_percentage}\n"
                                f"near expiry days parameter - {near_expiry_days}\n",
                      to_emails=email_to, file_uris=[flagged_inv,raw_inventory,raw_sale])

# Closing the DB Connection
rs_db.close_connection()
mysql_write.close()