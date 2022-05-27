# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: To populate table purchase_margin
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime
import numpy as np

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MSSql
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from dateutil.tz import gettz

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Populates table purchase_margin")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to', default="vivek.sidagam@zeno.health",
                        type=str, required=False)
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    email_to = args.email_to

    err_msg = ''

    logger = get_logger()
    logger.info("Script begins")

    cur_date = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    status = False

    try:
        # MSSql connection
        mssql = MSSql(connect_via_tunnel=False)
        mssql_connection = mssql.open_connection()
        # RS Connection
        rs_db = DB()
        rs_db.open_connection()
        q1 = """
            select
                'warehouse' as source,
                cast(b.Barcode as int) as drug_id,
                cast(a.Vdt as date) as purchase_date
                c.Altercode as distributor_id,
                -- d.name as distributor_name,
                a.Qty as quantity,
                b.Mrp as mrp,
                (a.NetAmt + a.Taxamt)/ qty as purchase_rate,
                cast(Vno as varchar) + cast('-' as varchar) + cast(Itemc as varchar) + cast('-' as varchar) + cast(Psrlno as varchar) as id,
                199 as store_id
                /*
                s.name as store_name,
                zc.name as city_name,
                f.name as franchisee_name,
                s."opened-at" as store_opened_at,
                drg."drug-name" as drug_name,
                drg."type",
                drg.company,
                drg.category,
                drg."available-in",
                drg."sub-type",
                drg."category-drug-type",
                current_timestamp as run_time
                */
            from
                SalePurchase2 a
            left join Item b on
                b.code = a.Itemc
            left join acm c on
                c.code = a.Acno
            left join Master m on
                m.code = b.ItemCat
            /*
            left join distributors d on
                d.id = c.Altercode
            left join stores s on
                s.id = 199
            left join "zeno-city" zc on
                zc.id = s."city-id"
            left join franchisees f on
                f.id = s."franchisee-id"
            left join drugs drg on
                drg.id = b.Barcode
            */
            where
                b.Barcode not like '%[^0-9]%'
                and c.Altercode not like '%[^0-9]%'
                and a.Vtype in (N'PB')
                and a.Qty > 0
                and a.Vno > 0
                and a.Vdt >= cast(DATEADD(month, -6, GETDATE()) - day(GETDATE()) + 1 as date)
        """
        logger.info("getting data from WMS tables")
        wh = pd.read_sql(q1, mssql_connection)
        logger.info("Data pulled from WMS tables")

        q2 = """
            select
                'dc' as source,
                ii."drug-id" as drug_id,
                date(i."approved-at") as purchase_date,
                cast(i."distributor-id" as varchar) as distributor_id,
                -- d.name as distributor_name,
                ii."actual-quantity" as quantity,
                ii.mrp,
                (ii."net-value" / ii."actual-quantity") as purchase_rate,
                cast(ii.id as varchar) as id,
                i."store-id" as store_id
                /*
                s.name as store_name,
                zc.name as city_name,
                f.name as franchisee_name,
                s."opened-at" as store_opened_at,
                drg."drug-name" as drug_name,
                drg."type",
                drg.company,
                drg.category,
                drg."available-in" as available_in,
                drg."sub-type" as sub_type,
                drg."category-drug-type" as category_drug_type,
                current_timestamp as run_time
                */
            from
                "prod2-generico".invoices i
            left join "prod2-generico"."invoice-items" ii on
                ii."invoice-id" = i.id
            /*	
            left join "prod2-generico".distributors d on d.id = i."distributor-id"
            left join "prod2-generico".stores s on s.id = i."store-id"
            left join "prod2-generico"."zeno-city" zc on zc.id = s."city-id"
            left join "prod2-generico".franchisees f on f.id = s."franchisee-id"
            left join "prod2-generico".drugs drg on drg.id = ii."drug-id"
            */
            where
                i."approved-at" >= date_trunc('month', current_date) - interval '6 month'
                and "distributor-id" <> 8105
                and ii."drug-id" is not null
        """
        logger.info("Getting data from RS")
        dc = rs_db.get_df(q2)
        logger.info("Data pulled from RS")

        drugs = rs_db.get_df("""  
            select
                drg.id as drug_id,
                drg."drug-name" as drug_name,
                drg."type",
                drg.company,
                drg.category,
                drg."available-in" as available_in,
                drg."sub-type" as sub_type,
                drg."category-drug-type" as category_drug_type
            from
                "prod2-generico".drugs drg
        """)

        stores = rs_db.get_df("""
            select
                sm.id as store_id,
                sm.store as store_name,
                sm.city as city_name,
                sm."franchisee-name" as franchisee_name,
                sm."opened-at" as store_opened_at
            from
                "prod2-generico"."stores-master" sm
        """)

        distributors = rs_db.get_df("""
            select
                id as distributor_id,
                d."name" as distributor_name
            from
                "prod2-generico".distributors d
        """)

        df = pd.concat([dc, wh])

        df = df.merge(drugs, on='drug_id', how='left')
        df = df.merge(stores, on='store_id', how='left')
        df['distributor_id'] = np.where(df['distributor_id'] == '', 0, df['distributor_id'])
        df['distributor_id'] = df['distributor_id'].astype(int)
        df = df.merge(distributors, on='distributor_id', how='left')

        created_at = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
        df['created-at'] = created_at
        df['created-by'] = 'etl-automation'
        df['updated-at'] = created_at
        df['updated-by'] = 'etl-automation'

        df['quantity'] = df['quantity'].astype(int)

        #writing to RS
        rs_db.execute(""" delete from "prod2-generico"."purchase-margin" """)
        s3 = S3()
        s3.write_df_to_db(df=df, table_name='purchase-margin', db=rs_db, schema='prod2-generico')

        status = True

    except Exception as e:
        err_msg = str(e)
        logger.info('purchase_margin job failed')
        logger.exception(e)

    # Sending email
    email = Email()
    if status:
        result = 'Success'
        email.send_email_file(subject=f"purchase_margin ({env}): {result}",
                              mail_body=f"Run time: {cur_date}",
                              to_emails=email_to, file_uris=[])
    else:
        result = 'Failed'
        email.send_email_file(subject=f"purchase_margin ({env}): {result}",
                              mail_body=f"Run time: {cur_date}  {err_msg}",
                              to_emails=email_to, file_uris=[])

    logger.info("Script ended")

#DDL for table
"""
create table "prod2-generico"."purchase-margin" ( "source" text,
	"drug_id" int,
	"created_at" date,
	"distributor_id" int,
	"quantity" int,
	"mrp" float,
	"purchase_rate" float,
	"id" text,
	"store_id" int,
	"drug_name" text,
	"type" text,
	"company" text,
	"category" text,
	"available_in" text,
	"sub_type" text,
	"category_drug_type" text,
	"store_name" text,
	"city_name" text,
	"franchisee_name" text,
	"store_opened_at" date,
	"distributor_name" text,
	"created-at" TIMESTAMP without TIME zone default getdate(),
	"created-by" VARCHAR default 'etl-automation',
	"updated-at" TIMESTAMP without TIME zone default getdate(),
	"updated-by" VARCHAR default 'etl-automation'
);

alter table "prod2-generico"."purchase-margin" owner to admin;
"""
