# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 17:20:59 2022

@author: vivek.sidagam@zeno.health

Purpose: To send consolidated PR FF and OOS numbers
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import datetime

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.helper.parameter.job_parameter import parameter

job_params = parameter.get_params(job_id=7)

parser = argparse.ArgumentParser(
    description="To send consolidated PR FF and OOS numbers.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
email_to = job_params['email_to']



logger = get_logger()
logger.info("Script begins")

status = False

try:
    # RS Connection
    rs_db = DB()
    rs_db.open_connection()

    query = """
    SELECT 
        a."patient-id" as "patient-id",
        (a."month-created-at") as "month",
        (a."year-created-at") as "year",
        CURRENT_TIMESTAMP AS "refreshed_at",
        a."store-name" AS "store-name",
        a."drug-name" AS "drug-name",
        case 
            when date_part(hour, a."created-at") <= '14' then '1stR'
            else '2ndR'
        end as "Round",
        case 
        when DATE(a."invoiced-at") is null then
            'Pending'
            when date_part(hour, a."created-at") <= '14'
            AND DATEDIFF(day, a."created-at", a."invoiced-at") = 0
                    AND date_part(hour, a."invoiced-at") <= '21' then 
                'ontime'
                when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                        AND date_part(hour, a."created-at") > '23'
                        AND DATEDIFF(day, a."created-at", a."invoiced-at") = 0 then
                    'ontime'
                    when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                            AND date_part(hour, a."created-at") > '23'
                            AND DATEDIFF(day, a."created-at", a."invoiced-at") = 1
                            AND date_part(hour, a."invoiced-at") <= '21' then
                        'ontime'
                        when date_part(hour, a."created-at") > '14'
                                AND DATEDIFF(day, a."created-at", a."invoiced-at") = 0 then
                            'ontime'
                            when date_part(hour, a."created-at") > '14'
                                    AND DATEDIFF(day, a."created-at", a."invoiced-at") = 1
                                    AND date_part(hour, a."invoiced-at") <= '16' then
                                'ontime'
                                when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                        AND date_part(hour, a."created-at") <= '14'
                                        AND DATEDIFF(day, a."created-at", a."invoiced-at") = 0
                                        AND date_part(hour, a."invoiced-at") <= '21' then
                                    'ontime'
                                    when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                            AND date_part(hour, a."created-at") > '14'
                                            AND DATEDIFF(day, a."created-at", a."invoiced-at") <= 1 then
                                        'ontime'
                                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                AND date_part(hour, a."created-at") > '14'
                                                AND DATEDIFF(day, a."created-at", a."invoiced-at") = 2
                                                AND date_part(hour, a."invoiced-at") <= '16' then
                                            'ontime'
                                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                    AND DATEDIFF(day, a."created-at", a."invoiced-at") <= 1 then
                                                'ontime'
                                                when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                        AND DATEDIFF(day, a."created-at", a."invoiced-at") = 2
                                                        AND date_part(hour, a."invoiced-at") <= '16' then
                                                    'ontime'
                                                        else
                                                    'delayed' end AS "fullfilment on invoice",
        Case
        when DATE(a."dispatched-at") is null then
            'Pending'
            when date_part(hour, a."created-at") <= '14'
                    AND DATEDIFF(day, a."created-at", a."dispatched-at") = 0 then
                'ontime'
                when date_part(hour, a."created-at") <= '14'
                        AND DATEDIFF(day, a."created-at", a."dispatched-at") = 1
                        AND date_part(hour, a."dispatched-at") <= '10' then
                    'ontime'
                    when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                            AND date_part(hour, a."created-at") > '23'
                            AND DATEDIFF(day, a."created-at", a."dispatched-at") = 0 then
                        'ontime'
                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                                AND date_part(hour, a."created-at") > '23'
                                AND DATEDIFF(day, a."created-at", a."dispatched-at") = 1 then
                            'ontime'
                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                                    AND date_part(hour, a."created-at") > '23'
                                    AND DATEDIFF(day, a."created-at", a."dispatched-at") = 2
                                    AND date_part(hour, a."dispatched-at") <= '10' then
                                'ontime'
                                when date_part(hour, a."created-at") > '14'
                                        AND DATEDIFF(day, a."created-at", a."dispatched-at") = 0 then
                                    'ontime'
                                    when date_part(hour, a."created-at") > '14'
                                            AND DATEDIFF(day, a."created-at", a."dispatched-at") = 1
                                            AND date_part(hour, a."dispatched-at") <= '17' then
                                        'ontime'
                                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                AND date_part(hour, a."created-at") <= '14'
                                                AND DATEDIFF(day, a."created-at", a."dispatched-at") = 0 then
                                            'ontime'
                                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                    AND date_part(hour, a."created-at") <= '14'
                                                    AND DATEDIFF(day, a."created-at", a."dispatched-at") = 1
                                                    AND date_part(hour, a."dispatched-at") <= '10' then
                                                'ontime'
                                                when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                        AND date_part(hour, a."created-at") > '14'
                                                        AND DATEDIFF(day, a."created-at", a."dispatched-at") <= 1 then
                                                    'ontime'
                                                    when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                            AND date_part(hour, a."created-at") > '14'
                                                            AND DATEDIFF(day, a."created-at", a."dispatched-at") = 2
                                                            AND date_part(hour, a."dispatched-at") <= '17' then
                                                        'ontime'
                                                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                                AND DATEDIFF(day, a."created-at", a."dispatched-at") <= 1 then
                                                            'ontime'
                                                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                                    AND DATEDIFF(day, a."created-at", a."dispatched-at") = 2
                                                                    AND date_part(hour, a."dispatched-at") <= '17' then
                                                                'ontime' else
                                                                'delayed' end AS "fullfilment on dispatch",
        case when DATE(a."store-delivered-at") is null then
            'Pending'
            when date_part(hour, a."created-at") <= '14'
                    AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 0 then
                'ontime'
                when date_part(hour, a."created-at") <= '14'
                        AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 1
                        AND date_part(hour, a."store-delivered-at") <= '11' then
                    'ontime'
                    when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                            AND date_part(hour, a."created-at") > '23'
                            AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 0 then
                        'ontime'
                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                                AND date_part(hour, a."created-at") > '23'
                                AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 1 then
                            'ontime'
                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                                    AND date_part(hour, a."created-at") > '23'
                                    AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 2
                                    AND date_part(hour, a."store-delivered-at") <= '11' then
                                'ontime'
                                when date_part(hour, a."created-at") > '14'
                                        AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 0 then
                                    'ontime'
                                    when date_part(hour, a."created-at") > '14'
                                            AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 1
                                            AND date_part(hour, a."store-delivered-at") <= '19' then
                                        'ontime'
                                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                AND date_part(hour, a."created-at") <= '14'
                                                AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 0 then
                                            'ontime'
                                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                    AND date_part(hour, a."created-at") <= '14'
                                                    AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 1
                                                    AND date_part(hour, a."store-delivered-at") <= '12' then
                                                'ontime'
                                                when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                        AND date_part(hour, a."created-at") > '14'
                                                        AND DATEDIFF(day, a."created-at", a."store-delivered-at") <= 1 then
                                                    'ontime'
                                                    when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                            AND date_part(hour, a."created-at") > '14'
                                                            AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 2
                                                            AND date_part(hour, a."store-delivered-at") <= '19' then
                                                        'ontime'
                                                        when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                                AND DATEDIFF(day, a."created-at", a."store-delivered-at") <= 1 then
                                                            'ontime'
                                                            when (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                                    AND DATEDIFF(day, a."created-at", a."store-delivered-at") = 2
                                                                    AND date_part(hour, a."store-delivered-at") <= '19'then
                                                                'ontime' else
                                                                'delayed' end AS "fullfilment on delivery",
        case when DATE(a."ordered-at") is not null
                AND date_part(hour, a."created-at") <= '14'
                AND DATEDIFF(day, a."created-at", a."ordered-at") = 0
                AND date_part(hour, a."ordered-at") <= '15' then
            'ontime'
            when DATE(a."ordered-at") is not null
                    AND (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Saturday' , 'Sunday')
                    AND date_part(hour, a."created-at") > '23'
                    AND DATEDIFF(day, a."created-at", a."ordered-at") = 0 then
                'ontime'
                when DATE(a."ordered-at") is not null
                        AND (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Saturday' , 'Sunday')
                        AND date_part(hour, a."created-at") > '23'
                        AND DATEDIFF(day, a."created-at", a."ordered-at") = 1
                        AND date_part(hour, a."ordered-at") <= '15' then
                    'ontime'
                    when DATE(a."ordered-at") is not null
                            AND date_part(hour, a."created-at") > '14'
                            AND DATEDIFF(day, a."created-at", a."ordered-at") = 0 then
                        'ontime'
                        when DATE(a."ordered-at") is not null
                                AND date_part(hour, a."created-at") > '14'
                                AND DATEDIFF(day, a."created-at", a."ordered-at") = 1
                                AND date_part(hour, a."ordered-at") <= '01' then
                            'ontime'
                            when DATE(a."ordered-at") is not null
                                    AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                    AND date_part(hour, a."created-at") <= '14'
                                    AND DATEDIFF(day, a."created-at", a."ordered-at") = 0
                                    AND date_part(hour, a."ordered-at") <= '15' then
                                'ontime'
                                when DATE(a."ordered-at") is not null
                                        AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                        AND date_part(hour, a."created-at") > '14'
                                        AND DATEDIFF(day, a."created-at", a."ordered-at") = 0 then
                                    'ontime'
                                    when DATE(a."ordered-at") is not null
                                            AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                            AND date_part(hour, a."created-at") > '14'
                                            AND DATEDIFF(day, a."created-at", a."ordered-at") = 1 then
                                        'ontime'
                                        when DATE(a."ordered-at") is not null
                                                AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                                AND date_part(hour, a."created-at") > '14'
                                                AND DATEDIFF(day, a."created-at", a."ordered-at") = 2
                                                AND date_part(hour, a."ordered-at") <= '01' then
                                            'ontime'
                                            when DATE(a."ordered-at") is not null
                                                    AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                    AND DATEDIFF(day, a."created-at", a."ordered-at") = 0 then
                                                'ontime'
                                                when DATE(a."ordered-at") is not null
                                                        AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                        AND DATEDIFF(day, a."created-at", a."ordered-at") = 1
                                                        AND date_part(hour, a."ordered-at") <= '01' then
                                                    'ontime'
                                                    when DATE(a."ordered-at") is null then
                                                        'not ordered' else
                                                        'delayed' end AS "ordered timing",
        case when DATE(a."invoiced-at") is null
                AND DATE(a."completed-at") is null
                AND date_part(hour, a."created-at") <= '14'
                AND DATEDIFF(day, a."created-at", a."completed-at") = 0
                AND (date_part(hour, a."completed-at")) <= '21' then 
            'completed-early'
            when DATE(a."invoiced-at") is null
                    AND DATE(a."completed-at") is not null
                    AND (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                    AND date_part(hour, a."created-at") > '23'
                    AND DATEDIFF(day, a."created-at", a."completed-at") = 0 then
                'completed-early'
                when DATE(a."invoiced-at") is null
                        AND DATE(a."completed-at") is not null
                        AND (trim(' ' FROM to_char(a."created-at", 'Day'))) NOT IN ('Sunday' , 'Saturday')
                        AND date_part(hour, a."created-at") > '23'
                        AND DATEDIFF(day, a."created-at", a."completed-at") = 1
                        AND (date_part(hour, a."completed-at")) <= '21' then
                    'completed-early'
                    when DATE(a."invoiced-at") is null
                            AND DATE(a."completed-at") is not null
                            AND date_part(hour, a."created-at") > '14'
                            AND DATEDIFF(day, a."created-at", a."completed-at") = 0 then
                        'completed-early'
                        when DATE(a."invoiced-at") is null
                                AND DATE(a."completed-at") is not null
                                AND date_part(hour, a."created-at") > '14'
                                AND DATEDIFF(day, a."created-at", a."completed-at") = 1
                                AND (date_part(hour, a."completed-at")) <= '16' then 
                            'completed-early'
                            when DATE(a."invoiced-at") is null
                                    AND DATE(a."completed-at") is not null
                                    AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                    AND DATEDIFF(day, a."created-at", a."completed-at") = 0
                                    AND date_part(hour, a."created-at") <= '14'
                                    AND (date_part(hour, a."completed-at")) <= '21' then
                                'completed-early'
                                when DATE(a."invoiced-at") is null
                                        AND DATE(a."completed-at") is not null
                                        AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                        AND date_part(hour, a."created-at") > '14'
                                        AND DATEDIFF(day, a."created-at", a."completed-at") <= 1 then
                                    'completed-early'
                                    when DATE(a."invoiced-at") is null
                                            AND DATE(a."completed-at") is not null
                                            AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Saturday'
                                            AND date_part(hour, a."created-at") > '14'
                                            AND DATEDIFF(day, a."created-at", a."completed-at") = 2
                                            AND (date_part(hour, a."completed-at")) <= '16' then
                                        'completed-early'
                                        when DATE(a."invoiced-at") is null
                                                AND DATE(a."completed-at") is not null
                                                AND (trim(' ' FROM to_char(a."created-at", 'Day'))) = 'Sunday'
                                                AND DATEDIFF(day, a."completed-at", a."created-at") <= 1 then
                                            'completed-early'
                                            when DATE(a."invoiced-at") is null
                                                    AND DATE(a."completed-at") is not null
                                                    AND DATEDIFF(day, a."created-at", a."completed-at") = 2
                                                    AND (date_part(hour, a."completed-at")) <= '16' then
                                                'completed-early'
                                                    else
                                                'no issue' end AS "completed issues",
        a."sb-status" AS "status",
        a."pso-requested-quantity" AS "requested-quantity",
        a."quantity" AS "quantity",
        a."required-quantity" AS "required-quantity",
        DATE(a."created-at") AS "created-at",
        DATE(a."ordered-at") AS "ordered-at",
        DATE(a."invoiced-at") AS "invoiced-at",
        DATE(a."dispatched-at") AS "dispatched-at",
        DATE(a."received-at") AS "received-at",
        DATE(a."completed-at") AS "completed-at",
        DATE(dtm."delivered-at") AS "delivered-at" ,
        a."created-at" AS "created-time",
        a."ordered-at" AS "ordered-time",
        a."invoiced-at" AS "invoiced-time",
        a."dispatched-at" AS "dispatch-time",
        dtm."delivered-at" AS "delivered-time",
        a."completed-at" AS "completed-time",
        a."decline-reason" AS "decline reason",
        a."type",
        a."store-id",
        a."drug-id",
        a."company",
        a."franchisee-short-book",
        e."drug-grade",
        f."name" AS "received distributor",
        case when a."store-id" >= 146 then  'new' else 'old' end AS "store-type",
        j."forward-dc-id",
        ss."name" AS "dc_name",
        a."store-delivered-at",
        case when p."patient-category" !='others' then 1 else 0 end as premium_flag
    FROM
       "prod2-generico"."patient-requests-metadata" a
            LEFT JOIN
        "prod2-generico"."drug-order-info" e ON e."store-id" = a."store-id"
            AND e."drug-id" = a."drug-id"
            LEFT JOIN
        "prod2-generico"."distributors" f ON NVL(a."ordered-distributor-id",0) = f."id"
            LEFT JOIN
        (SELECT 
            *
        FROM
            "prod2-generico"."store-dc-mapping"
        WHERE
            "drug-type" = 'ethical') j ON j."store-id" = a."store-id"
            LEFT JOIN
        "prod2-generico"."stores" ss ON ss."id" = j."forward-dc-id"
            left join 
        "prod2-generico"."delivery-tracking-metadata" dtm
            on dtm.id=a.id
            left join 
        "prod2-generico"."patients" p
            on a."patient-id" =p.id
    WHERE
        DATE(a."created-at") >= case when extract(day from current_date) >= 7 then (current_date - extract(day from current_date) + 1) else  current_date - 7 end
           and a."quantity" > 0
            AND a."sb-status" NOT IN ('deleted')
    """
    raw = rs_db.get_df(query)
    logger.info("data pulled from RS")

    pr = raw.copy()

    # OOS query
    oos_network_q = """
    select
        "closing-date",
        avg("oos-count")* 100 as oos_perc_network
    from
        "prod2-generico"."out-of-shelf-drug-level" oosdl
    where
        "closing-date" >= CURRENT_DATE - interval '7 day'
        and "max-set" = 'Y'
    group by
        "closing-date"
    """

    oos_premium_q = """
    select
        "closing-date",
        avg("oos-count")* 100 as oos_perc_premium
    from
        "prod2-generico"."out-of-shelf-drug-level" oosdl
    where
        "closing-date" >= CURRENT_DATE - interval '7 day'
        and "customer-type" = 'Premium'
        and "max-set" = 'Y'
    group by
        "closing-date"
    """

    oos_net = rs_db.get_df(oos_network_q)
    oos_pre = rs_db.get_df(oos_premium_q)

    pr.columns = [c.replace('-', '_') for c in pr.columns]
    oos_net.columns = [c.replace('-', '_') for c in oos_net.columns]
    oos_pre.columns = [c.replace('-', '_') for c in oos_pre.columns]

    rs_db.connection.close()
    pr = pr[pr['completed issues'] == 'no issue']
    pr = pr[['store_name', 'created_at', 'fullfilment on delivery',
             'quantity']]
    pr = pr.groupby(['store_name', 'created_at',
                     'fullfilment on delivery']).sum()
    pr.reset_index(inplace=True)

    #store level calculations
    pr_pivot_store_lvl = pr.pivot_table(index=['store_name','created_at'],
                           values='quantity',
                           columns = 'fullfilment on delivery',
                           aggfunc='sum', fill_value=0)
    pr_pivot_store_lvl['total_quantity'] = pr_pivot_store_lvl[
        'ontime'] + pr_pivot_store_lvl[
            'delayed'] + pr_pivot_store_lvl['Pending']
    pr_pivot_store_lvl['ff%'] = pr_pivot_store_lvl[
        'ontime']/pr_pivot_store_lvl['total_quantity'] * 100
    pr_pivot_store_lvl['ff%'] = pr_pivot_store_lvl['ff%'].round(1)
    pr_pivot_store_lvl['below_80'] = np.where(pr_pivot_store_lvl[
        'ff%']<80, 1, 0)
    pr_pivot_store_lvl.reset_index(inplace=True)
    pr_pivot_store_lvl_80 = pr_pivot_store_lvl[['created_at', 'below_80']]
    pr_pivot_store_lvl_80 = pr_pivot_store_lvl_80.groupby([
        'created_at']).sum()
    total_stores = pr_pivot_store_lvl.pivot_table(index='created_at',
                                                  values = 'store_name',
                                                  aggfunc='count')
    total_stores.rename(columns={'store_name':'total_stores'},
                        inplace=True)
    pr_pivot_day_lvl = pr.pivot_table(index='created_at',
                           values='quantity',
                           columns = 'fullfilment on delivery',
                           aggfunc='sum', fill_value=0)
    pr_pivot_day_lvl['total_quantity'] = pr_pivot_day_lvl[
        'ontime'] + pr_pivot_day_lvl[
            'delayed'] + pr_pivot_day_lvl['Pending']
    pr_pivot_day_lvl['ff%'] = pr_pivot_day_lvl[
        'ontime']/pr_pivot_day_lvl['total_quantity'] * 100
    pr_pivot_day_lvl['ff%'] = pr_pivot_day_lvl['ff%'].round(0)
    pr_pivot_day_lvl.reset_index(inplace=True)
    pr_pivot_day_lvl = pr_pivot_day_lvl[['created_at', 'ff%']]

    final_pr = pr_pivot_day_lvl.merge(pr_pivot_store_lvl_80,
                                      on='created_at', how='left')
    final_pr = final_pr.merge(total_stores, on='created_at', how='left')
    final_pr.reset_index(inplace=True)
    final_pr = final_pr[['created_at', 'ff%', 'below_80', 'total_stores']]
    ff = pd.DataFrame()
    ff['created_at'] = final_pr['created_at']
    ff['ff%'] = final_pr['ff%']
    ff['below_80'] = final_pr['below_80']
    ff['total_stores'] = final_pr['total_stores']

    #OOS pre-processing
    oos_net['oos_perc_network'] = oos_net['oos_perc_network'].round(2)
    oos_pre['oos_perc_premium'] = oos_pre['oos_perc_premium'].round(2)
    status = True

except Exception as e:
    logger.info('pr_oos_automailer job failed')
    logger.exception(e)

# Sending email
email = Email()

run_date = str(datetime.datetime.now().strftime("%Y-%m-%d"))

subject = "PR Day-wise Fullfillment MTD / OOS Network & Premium"

if status is True:
    mail_body = f"""PR Fulfillment : \n {ff} \n\n 
    OOS NETWORK : \n {oos_net} \n\n
    OOS Premium : \n {oos_pre}""".format(ff=ff.to_string(index=False),
                                         oos_net=oos_net.to_string(index=False),
                                         oos_pre=oos_pre.to_string(index=False))
else:
    mail_body = f"pr_ff_automailer ({env}) unsuccessful: {datetime.datetime.now()}"

email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=[])

logger.info("Script ended")
