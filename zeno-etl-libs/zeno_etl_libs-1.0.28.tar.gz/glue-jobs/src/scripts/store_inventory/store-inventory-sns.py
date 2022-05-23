
import sys
import os

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
import numpy as np
import json
import os
import re
from datetime import date
from datetime import datetime
import dateutil.relativedelta
import numpy as np
from dateutil.tz import gettz



parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="akshay.bhutada@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to

env = args.env
os.environ['env'] = env


logger = get_logger()
logger.info(f"env: {env}")


logger.info('Script Manager Initialized')

rs_db = DB()

s3 = S3()

rs_db.open_connection()

snapshot_date = datetime.now().date()



inv_query='''
select 
a."store-id" ,
a."franchisee-id",
	a."store-name" as "store-name",
	a."type" ,
	a.category ,
	a."drug-grade" ,
	sum(case when a."inventory-oh" <> 0 then 1 else 0 end) as "drug-count",
	SUM(a."inventory-oh") as "inventory-oh"  ,
	SUM(a."inventory-value-oh") as "inventory-value-oh",
	SUM(a."min-inv-value") as "min-inv-value",
	SUM(a."ss-inv-value") as "ss-inv-value",
	SUM(a."max-inv-value") as "max-inv-value"
FROM
(select
	inv."store-id" ,
	str."franchisee-id" ,
	str."name" as "store-name",
	d."type" ,
	d.category ,
	di."drug-grade" ,
	inv."drug-id",
	(CASE
	WHEN
	str."franchisee-id"=1 then sum(inv.quantity + inv."locked-for-return" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" + inv."locked-quantity")
	WHEN str."franchisee-id"!=1 then SUM(inv."locked-quantity")
	END) as "inventory-oh",
	(CASE
	WHEN
	str."franchisee-id"=1 then sum(inv.ptr * (inv.quantity + inv."locked-for-return" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" + inv."locked-quantity"))
	WHEN str."franchisee-id"!=1 then sum(inv.ptr * ( inv."locked-quantity"))
	END) as "inventory-value-oh",
	coalesce(avg(di."min") * avg(inv.ptr), 0) as "min-inv-value",
	coalesce(avg(di."safe-stock") * avg(inv.ptr), 0) as "ss-inv-value",
	coalesce(avg(di."max") * avg(inv.ptr), 0) as "max-inv-value"
from
	"prod2-generico"."prod2-generico"."inventory-1" inv
left join "prod2-generico"."prod2-generico"."invoice-items-1" ii  on
	inv."invoice-item-id" = ii.id
left join "prod2-generico".drugs d
        on
	inv."drug-id" = d.id
left join "prod2-generico"."prod2-generico"."drug-order-info" di
        on
	inv."drug-id" = di."drug-id" 
	and inv."store-id" = di."store-id" 
left join "prod2-generico".stores str
        on
	inv."store-id" = str.id
group by
	inv."store-id" ,
	str."name" ,
	str."franchisee-id" ,
	d."type" ,
	d.category ,
	di."drug-grade",inv."drug-id")  a
group by  a."store-id" ,
	a."store-name" ,
	a."franchisee-id",
	a."type" ,
	a.category ,
	a."drug-grade"
'''
stores=rs_db.get_df(query=inv_query)


stores[['inventory-value-oh', 'min-inv-value',
       'ss-inv-value', 'max-inv-value']]=stores[['inventory-value-oh', 'min-inv-value',
       'ss-inv-value', 'max-inv-value']].astype(np.float64)

stores['snapshot-date'] = snapshot_date

created_at = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
stores['created-at']=datetime.strptime(created_at,"%Y-%m-%d %H:%M:%S")
updated_at = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
stores['updated-at']=datetime.strptime(updated_at,"%Y-%m-%d %H:%M:%S")
stores['created-by'] = 'etl-automation'
stores['updated-by'] = 'etl-automation'

#Truncate the Query
logger.info('Delete for current date ')


truncate_query = '''
       delete from "prod2-generico"."store-inventory-sns" 
       where date("snapshot-date") = '{snapshot_date}'
       '''.format(snapshot_date=snapshot_date)

rs_db.execute(truncate_query)


stores.columns = [c.replace('_', '-') for c in stores.columns]

schema = "prod2-generico"
table_name = "store-inventory-sns"
table_info = helper.get_table_info(db=rs_db
                                   , table_name=table_name, schema=schema)


logger.info('Writing to table')

s3.write_df_to_db(df=stores[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)

status=True


if status==True:
    script_status="Success"
else:
    script_status="Failed"




email = Email()

email.send_email_file(subject=f"store_inventory {snapshot_date} {script_status}",
                      mail_body=f"store inventory job status: {script_status} ",
                      to_emails=email_to)

rs_db.close_connection()



