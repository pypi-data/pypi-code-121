import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.db.db import DB, PostGre
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
import argparse
import pandas as pd
import datetime
import os
import re
from datetime import date
from datetime import datetime
import numpy as np
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="akshay.bhutada@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()

env = args.env
email_to = args.email_to

os.environ['env'] = env

currentMonth = datetime.now(tz=gettz('Asia/Kolkata')).month
currentYear = datetime.now(tz=gettz('Asia/Kolkata')).year
run_date = str(datetime.now(tz=gettz('Asia/Kolkata')).date())

rs_db = DB()
rs_db.open_connection()

s3=S3()


warehouse_drug_query = '''
select
	wssm."drug-id"  as "drug-id-dss",
	 'Yes' as "add-wh" 
from
"prod2-generico"."wh-sku-subs-master" wssm where wssm."add-wh" ='Yes'
'''

warehouse_drug = rs_db.get_df(query=warehouse_drug_query)





wh_prate_query = """
  select
	i.barcode as "drug-id-wh" ,
	i.prate as "fixed-purchase-rate"
from
	"prod2-generico".item i
where
	i.prate > 0
	and REGEXP_COUNT(i.barcode ,
	'^[0-9]+$')= 1
    """



wh_prate=rs_db.get_df(query=wh_prate_query)

wh_prate["drug-id-wh"] = pd.to_numeric(wh_prate["drug-id-wh"])



q_aa='''
select
	"year-created-at"  as "year",
	"month-created-at" as "month" ,
	  s."bill-flag" as "sales-type",
	 s."drug-id" ,
	 s."drug-name" ,
	 s."type" ,
	 s.category ,
	 s.company ,
	 d."available-in" ,
	 d.pack ,
	 d."pack-form" ,
	 d."release" ,
	 d."is-repeatable" ,
	 d."repeatability-index",
	 s."ecom-flag" ,
	 s.city  ,
	 COUNT(distinct s."bill-id") as "bill-count",
	 COUNT(distinct s."patient-id") as "patient-count",
	 SUM(s.mrp*s."net-quantity") as "net-mrp",
	 SUM(s.rate* s."net-quantity") as "net-revenue",
	 SUM(s.ptr*s."net-quantity") as "net-cogs-zp",
	 SUM(s."purchase-rate"*s."net-quantity") as "net-cogs-wc"
from
	"prod2-generico".sales s
left join "prod2-generico".drugs d on s."drug-id" =d.id 
where "year-created-at" ={currentYear} and "month-created-at" ={currentMonth}
group by 
"year-created-at" ,
	"month-created-at" ,
	  s."bill-flag",
	 s."drug-id" ,
	 s."drug-name" ,
	 s."type" ,
	 s.category ,
	 s.company ,
	 d."available-in" ,
	 d.pack ,
	 d."pack-form" ,
	 d."release" ,
	 d."is-repeatable" ,
	 d."repeatability-index",
	 s."ecom-flag" ,
	 s.city 
'''.format(currentYear=currentYear,currentMonth=currentMonth)



gross_and_returns = rs_db.get_df(query=q_aa)



conditions = [(gross_and_returns['repeatability-index'] >= 80 ),
               (gross_and_returns['repeatability-index'] >= 40) &  (gross_and_returns['category'] =='chronic'),
              (gross_and_returns['repeatability-index']<80) ]
choices = ['repeatable','repeatable', 'non-repeatable']
gross_and_returns['repeatable_flag'] = np.select(conditions, choices)



q_inventory='''
select
	i."drug-id",
	SUM(i.quantity + i."locked-for-check" + 
	i."locked-for-audit" + i."locked-for-return" + i."locked-for-transfer") as "current-inventory-qty",
	SUM((i.quantity + i."locked-for-check" + 
	i."locked-for-audit" + i."locked-for-return" + i."locked-for-transfer")* i.ptr) as "current-inventory-value",
	avg(srs."selling-rate") as "avg-fixed-selling-rate"
from
	"prod2-generico"."inventory-1" i
left join 	"prod2-generico"."selling-rate-settings" srs on
	i."drug-id" = srs."drug-id"
group by
	i."drug-id";
'''



df_inventory = rs_db.get_df(query=q_inventory)


gross_and_returns_inventory = pd.merge(left=gross_and_returns,
                                          right=df_inventory,
                                how='left', on=['drug-id'])


gross_and_returns_inventory['run_date'] = run_date



gross_and_returns_inventory = pd.merge(gross_and_returns_inventory, wh_prate,
                                 how='left', left_on='drug-id',
                                 right_on='drug-id-wh')
del gross_and_returns_inventory["drug-id-wh"]


gross_and_returns_inventory = pd.merge(gross_and_returns_inventory,
                                           warehouse_drug, how='left',
                                           left_on='drug-id',
                                           right_on='drug-id-dss')



gross_and_returns_inventory['add-wh'].fillna('No', inplace=True)
del gross_and_returns_inventory["drug-id-dss"]


consumer_dump = gross_and_returns_inventory

#Supply Dump
#Purchase data

q_invoices='''
SELECT
    	date_part(year,i."received-at") AS "year",
    	date_part(month,i."received-at") AS "month",
    	ii."drug-id" ,
        d."drug-name" ,
    	d."type" ,
    	d.category ,
    	d.composition ,
    	d.company ,
    	d."available-in" ,
    	d.pack ,
    	d."pack-form" ,
        d."release" ,
    	i."distributor-id" ,
    	di."name" as "distributor-name",
        cty.name as "city-name",
    	COUNT(DISTINCT si."short-book-id") AS "order-count",
    	SUM(si."po-quantity") AS "po-quantity",
    	SUM(ii."actual-quantity") AS "purchase-quantity",
    	SUM(ii."net-value") AS "puchase-value",
    	AVG(ii."net-value" /ii."actual-quantity") AS "avg-purchase-rate",
    	AVG(n."selling-rate") AS "avg-selling-rate",
    	AVG(ii.mrp) AS "avg-mrp",
       AVG(srs."selling-rate") as "avg-fixed-selling-rate"
    FROM
    	"prod2-generico"."invoice-items" ii 
    left JOIN "prod2-generico".invoices i on i.id =ii."invoice-id" 
    left JOIN "prod2-generico".distributors di on di.id = i."distributor-id" 
    left JOIN "prod2-generico"."short-book-invoice-items" si ON si."invoice-item-id" = ii.id
    left JOIN "prod2-generico".drugs d ON d.id = ii."drug-id" 
    left JOIN "prod2-generico"."invoice-items-1" it ON it."invoice-item-reference" = ii.id 
    left JOIN "prod2-generico"."inventory-1" n ON n."invoice-item-id" = it.id 
    LEFT JOIN "prod2-generico"."selling-rate-settings" srs  on ii."drug-id" =srs."drug-id" 
    LEFT JOIN (
        select
        	s.id,
        	zc.name
        from
        	"prod2-generico".stores s 
        left join "prod2-generico"."zeno-city" zc on
        	zc.id =s."city-id" 
        ) as cty on cty.id = i."store-id" 
    WHERE
    	date_part(year,i."received-at") ={currentYear}
    	 and date_part(month ,i."received-at")= {currentMonth}
    GROUP BY
    	date_part(year,i."received-at") ,
    	date_part(month,i."received-at") ,
    	ii."drug-id" ,
    	 d."drug-name" ,
    	d."type" ,
    	d.category ,
    	d.composition ,
    	d.company ,
    	d."available-in" ,
    	d.pack ,
    	d."pack-form" ,
        d."release" ,
    	i."distributor-id" ,
    	di."name" ,
        cty.name '''.format(currentYear=currentYear,currentMonth=currentMonth)


df_invoices = rs_db.get_df(query=q_invoices)


df_invoices['run-date'] = run_date




df_invoices = pd.merge(df_invoices, wh_prate,
                         how='left', left_on='drug-id',
                         right_on='drug-id-wh')
del df_invoices["drug-id-wh"]

# adding add_wh column
df_invoices = pd.merge(df_invoices, warehouse_drug,
                         how='left', left_on='drug-id',
                         right_on='drug-id-dss')
df_invoices['add-wh'].fillna('No', inplace=True)
del df_invoices["drug-id-dss"]




supply_dump = df_invoices


consumer_data_dump = 'cat_data_dump/consumer_data_dump_{}.csv'.format(run_date)
supply_data_dump = 'cat_data_dump/supply_data_dump_{}.csv'.format(run_date)





# Uploading File to S3

consumer_dump_uri = s3.save_df_to_s3(df=consumer_dump, file_name=consumer_data_dump)
supply_dump_uri= s3.save_df_to_s3(df=supply_dump, file_name=supply_data_dump)


#Sending the email

#email = Email()

#email.send_email_file(subject=f"Category Data Dump {run_date}",
                      #mail_body="category supply data ",
                      #to_emails=email_to, file_uris=[supply_dump_uri])




#email.send_email_file(subject=f"Category Data Dump {run_date}",
                      #mail_body="category consumer  data ",
                      #git to_emails=email_to, file_uris=[consumer_dump_uri])

rs_db.close_connection()




