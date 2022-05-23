# Script for System Inventory  #

import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.db.db import MSSql
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

# Store Inventory

q_1='''
select
	i."store-id" as "entity-id",
	s.name as "entity-name",
	'store' as "entity-type",
	d."type" as "drug-type" ,
	(case
		when d."company-id" = 6984 then 'true'
		else 'false'
	end) as "goodaid-flag",
	s."franchisee-id" as "franchise-id",
	'physical' as "inventory-type",
	(case
		when date(i.expiry) <= current_date then 'expired'
		when 
		(DATEDIFF('days',
		current_date,
		date(i.expiry))<= 90 and  DATEDIFF('days',
		current_date,
		date(i.expiry)) >0)  then 'near-expiry'
		else 'others'
	end) as "inventory-sub-type-1",
	'' as "inventory-sub-type-2",
	'' as "inventory-sub-type-3",
	SUM(i.quantity + i."locked-for-check" + i."locked-for-audit" + i."locked-for-transfer" + i."locked-for-return") as "quantity",
	 SUM((i.ptr / (1 + ii.vat / 100)) * (i.quantity + i."locked-for-check" + i."locked-for-audit" + i."locked-for-transfer" + i."locked-for-return")) as "value-without-tax",
	 SUM(i.ptr * (i.quantity + i."locked-for-check" + i."locked-for-audit" + i."locked-for-transfer" + i."locked-for-return")) as "value-with-tax"
from
	"prod2-generico"."inventory-1" i
left join "prod2-generico"."invoice-items-1" ii on
	i."invoice-item-id" = ii.id
left join "prod2-generico".stores s on
	i."store-id" = s.id
left join "prod2-generico".drugs d on 
	i."drug-id" = d.id
where
	(i.quantity>0
		or i."locked-for-check">0
		or i."locked-for-audit">0
		or i."locked-for-return">0
		or i."locked-for-transfer" >0)
	and 
        s.category != 'dc'
group by
	i."store-id",
	s."name" ,
	d."type",
	"goodaid-flag" ,
	s."franchisee-id",
	"inventory-sub-type-1" ;
'''



stores=rs_db.get_df(query=q_1)


# DC To be dispatched Inventory

to_be_dispatched='''
SELECT
s3.id as "entity-id",
s3.name as "entity-name",
'dc/warehouse' as "entity-type",
d."type" as "drug-type" ,
(case when d."company-id" =6984 then 'true'
	else 'false'  end) as "goodaid-flag",
s."franchisee-id" as "franchise-id",
'to_be_dispatched' as  "inventory-type",
'' as "inventory-sub-type-1",
'' as "inventory-sub-type-2",
'' as "inventory-sub-type-3",
SUM(i."locked-quantity") as "quantity",
SUM(i."locked-quantity" * ((i."purchase-rate")/(1+ii.vat/100)))  as "value-without-tax",
SUM(i."locked-quantity" * ((i."purchase-rate")))  as "value-with-tax"
FROM
    "prod2-generico".inventory i 
LEFT JOIN "prod2-generico".invoices i2 ON
    i2.id =i."invoice-id" 
LEFT JOIN "prod2-generico".stores s ON
    i2."store-id" =s.id 
LEFT JOIN "prod2-generico"."invoice-items" ii  ON
    i."invoice-item-id" =ii.id
LEFT JOIN "prod2-generico".stores s3 ON
    s3.id =i2."dc-id"
left join "prod2-generico".drugs d on ii."drug-id" =d.id 
WHERE
    (i."locked-quantity" >0 and i2."dispatch-status" ='dispatch-status-na')  
GROUP BY s3.id ,s3."name" ,d."type","goodaid-flag",s."franchisee-id" ;

'''


to_be_dispatched=rs_db.get_df(query=to_be_dispatched)

# DC/Warehouse Returns


return_query='''
SELECT 
    s2.id as "entity-id",
    s2.name as  "entity-name",
    'dc/warehouse' as "entity-type",
    d."type"  as "drug-type",
    (case when d."company-id" =6984 then 'true'
	else 'false'  end) as "goodaid-flag",
    s2."franchisee-id" as "franchise-id",
    'return' as  "inventory-type",
    CASE when ri."return-reason" IN ('reason-not-ordered',
 'reason-to-be-returned',
 'reason-wrong-product',
 'reason-product-short',
 'reason-softcopy-excess',
 'reason-already-returned',
 'reason-short-from-dc',
 'reason-customer-refused',
 'reason-wrongly-ordered',
 'reason-excess-supplied',
 'reason-non-moving',
 'reason-wrong-mrp',
 'reason-wrong-expiry',
 'reason-excess-or-not-ordered',
 'reason-late-supply',
 'reason-wrong-pack-size',
 'reason-excess-order') 
    Then 'Saleable'
    When ri."return-reason" IN ('reason-product-expired', 'reason-over-expiry', 'reason-npi-non-saleable') Then 'Non saleable'
    WHen ri. "return-reason" IN ('reason-product-damaged', 'reason-near-expiry') AND (DATEDIFF('days',rtd2."created-at" , i2."invoice-date")> 30) THEN
    'Non saleable'
    WHen ri."return-reason" IN ('reason-product-damaged', 'reason-near-expiry') AND (DATEDIFF('days',rtd2."created-at" , i2."invoice-date")<= 30) THEN
    'Saleable'
    Else 'Saleable'
    end
     as "inventory-sub-type-1",
    ri.status as "inventory-sub-type-2",
    dn.status as "inventory-sub-type-3" ,
    SUM(ri."returned-quantity") as "quantity" ,
    SUM(ri.taxable) as "value-without-tax",
    SUM(ri.net) as "value-with-tax"
FROM
    "prod2-generico"."return-items" ri              
LEFT JOIN "prod2-generico"."debit-note-items" dni 
ON
    ri.id = dni."item-id" 
    AND dni."is-active" != 0
LEFT JOIN "prod2-generico"."debit-notes" dn 
ON
    dni."debit-note-id" = dn.id 
 LEFT JOIN "prod2-generico"."inventory-1" i ON
    ri."inventory-id" =i.id
 LEFT JOIN "prod2-generico"."returns-to-dc" rtd3  ON 
    ri."return-id" =rtd3.id 
LEFT JOIN "prod2-generico"."return-items-1" ri2  ON ri."return-item-reference" =ri2.id 
LEFT JOIN "prod2-generico"."returns-to-dc-1" rtd2 ON ri2."return-id" =rtd2.id 
LEFT JOIN "prod2-generico".invoices i2 On (i2.id =i."invoice-id" )
LEFT JOIN "prod2-generico".stores s2 ON (ri."return-dc-id" =s2.id) 
left join "prod2-generico".drugs d  on i."drug-id" =d.id 
WHERE  (ri.status ='saved' OR ri.status ='approved') and ri."returned-quantity" >0
Group By s2.id,s2.name,s2."franchisee-id" ,d."type","goodaid-flag" ,"inventory-sub-type-1", ri.status,dn.status;
'''



return_query=rs_db.get_df(query=return_query)


#  Intransit

in_transit='''
select
	s3.id as "entity-id" ,
	s3.name as "entity-name",
    'dc/warehouse' as "entity-type",
	d."type" as "drug-type",
     (case when d."company-id" =6984 then 'true'
	else 'false'  end) as "goodaid-flag",
	s."franchisee-id" as "franchise-id",
	'in-transit' as "inventory-type",
	'' as "inventory-sub-type-1",
	'' as "inventory-sub-type-2",
	'' as "inventory-sub-type-3",
	SUM(i."locked-quantity") as "quantity" ,
	SUM(i."locked-quantity" * (i."purchase-rate")/(1 + ii.vat / 100)) as "value-without-tax",
	SUM(i."locked-quantity" * (i."purchase-rate")) as "value-with-tax"
from
	"prod2-generico"."inventory-1" i 
left join "prod2-generico".stores s on
	s.id=i."store-id" 
left join "prod2-generico".invoices i2 on
	i."invoice-id" =i2.id
left join "prod2-generico"."invoice-items-1" ii on
	i."invoice-item-id" =ii.id 
left join "prod2-generico".stores s3 on
	i2."dc-id" =s3.id 
left join "prod2-generico".drugs d on i."drug-id" =d.id 
where
	(i."locked-quantity" >0)
group by
	s3.id,
	s3.name,
	d."type",
    "goodaid-flag",
	s."franchisee-id" ;
'''



in_transit=rs_db.get_df(query=in_transit)


#drug info


drug_info='''
	
select
	d.id as "drug-id",
	d."type" as "drug-type" ,
	(case when d."company-id" =6984 then 'true'
	else 'false'  end) as "goodaid-flag"
from
	"prod2-generico".drugs d 
'''



drug_info=rs_db.get_df(query=drug_info)


#Warehouse Barcoded Query


mssql = MSSql(connect_via_tunnel=False)

cnxn = mssql.open_connection()

cursor = cnxn.cursor()

q_5 = '''
   select
	199 as "entity-id",
	'bhiwandi-warehouse' as "entity-name",
	'warehouse' as "entity-type",
	'' as "franchise-id",
	b.Barcode as "drug-id",
	'barcoded' as "inventory-type",
	(case
		when (b.Compcode = 465
		or b.Compcode = 459)
		and a.Acno != 59353 then 'goodaid'
		when (a.Acno = 59353) then 'npi'
		else 'non-goodaid'
	end) as "inventory-sub-type-1",
	'' as "inventory-sub-type-2",
	'' as "inventory-sub-type-3",
	sum(case when a.Vno < 0 then 0 else coalesce(a.bqty, 0) end) as "quantity",
	sum(case when a.Vno < 0 then 0 else coalesce(a.bqty * a.Cost , 0) end) as "value-without-tax",
	sum(case when a.vno<0 then 0 else coalesce((a.bqty * a.Cost *(1 + coalesce((sp.CGST + sp.SGST + sp.IGST), 0)/ 100)), 0) end) as "value-with-tax"
from
	fifo a
left join item b on
	a.itemc = b.code
left join SalePurchase2 sp on
	(a.Pbillno = sp.Pbillno
		and a.Psrlno = sp.Psrlno
		and a.Itemc = sp.Itemc
		and sp.Vdt = a.Vdt)
where
	b.code > 0
	 and isnumeric(b.Barcode) = 1
	and b.Barcode not like '%[^0-9]%'
	and a.BQty >0
	and a.Psrlno in (
	select
		Psrlno
	from
		SalePurchase2 sp)
group by
	b.Barcode,
	(case
		when (b.Compcode = 465
			or b.Compcode = 459)
		and a.Acno != 59353 then 'goodaid'
		when (a.Acno = 59353) then 'npi'
		else 'non-goodaid'
	end)
        '''

barcoded = pd.read_sql(q_5,cnxn)


# Warehouse Non Barcoded


q_6 = '''
   select
                199 as "entity-id",
                'bhiwandi-warehouse' as "entity-name",
                'warehouse' as "entity-type",
                '' as "franchise-id",
                b.Barcode as "drug-id",
                'non-barcoded' as "inventory-type",
                (Case
                when (b.Compcode = 465
                or b.Compcode = 459)
                and a.Acno != 59353 then 'goodaid'
                when (a.Acno = 59353) then 'npi'
                Else 'non-goodaid'
                end) as "inventory-sub-type-1",
                '' as "inventory-sub-type-2",
                '' as "inventory-sub-type-3",
                sum(case when a.Vno > 0 then 0 else coalesce(a.TQty , 0) end) as "quantity",
                sum(case when a.Vno > 0 then 0 else coalesce(a.TQty * a.Cost , 0) end) as "value-without-tax",
                sum(case when a.vno > 0 then 0 else coalesce((a.TQty * a.Cost *(1 +COALESCE((sp.CGST + sp.SGST + sp.IGST),0)/ 100)), 0) end) as "value-with-tax"
                from
                fifo a
                left join item b on
                a.itemc = b.code
                left join SalePurchase2 sp on
                (a.Pbillno = sp.Pbillno
                and a.Psrlno = sp.Psrlno
                and a.Itemc = sp.Itemc and sp.Vdt = a.Vdt)
                where
                b.code > 0
                  and isnumeric(b.Barcode) = 1
                and b.Barcode not like '%[^0-9]%'
                and a.TQty >0 and a.vno<0 and a.Psrlno in (
                select
                Psrlno
                from
                SalePurchase2 sp)
                group by
                b.Barcode,
                (Case
                when (b.Compcode = 465
                    or b.Compcode = 459)
                and a.Acno != 59353 then 'goodaid'
                when (a.Acno = 59353) then 'npi'
                Else 'non-goodaid'
                end)	
        '''

non_barcoded = pd.read_sql(q_6,cnxn)


#Wh to distributor


q_7='''
select
	199 as "entity-id",
	'bhiwandi-warehouse' as "entity-name",
	'warehouse' as "entity-type",
	'' as "franchise-id",
	item.Barcode as "drug-id",
	'wh-to-distributor-return' as "inventory-type",
	(case
		when (item.Compcode = 465
		or item.Compcode = 459) then 'goodaid'
		else 'non-goodaid'
	end) as "inventory-sub-type-1",
	'' as "inventory-sub-type-2",
	'' as "inventory-sub-type-3",
	SUM(s2.qty) as "quantity",
	SUM(s2.ftrate * (s2.qty + s2.fqty)) as "value-without-tax",
	SUM((1 + (s2.IGST + s2.CGST + s2.SGST)/ 100) * s2.ftrate * (s2.qty + s2.fqty)) as "value-with-tax"
from
	salepurchase1 s1
inner join salepurchase2 s2 on
	s2.vtype = s1.vtyp
	and s2.vno = s1.vno
	and s2.vdt = s1.vdt
	and s1.Trntype = s2.Trntype
inner join item on
	item.code = s2.itemc
inner join acm on
	s1.acno = acm.code
inner join FIFO f on
	f.Psrlno = s2.Psrlno
left join (
	select
		Pbillno,
		Vdt,
		Acno,
		Psrlno
	from
		salePurchase2 sp
	where
		Trntype = 'PB') as spx on
	spx.Acno = s2.Acno
	and spx.Psrlno = s2.Psrlno
left join (
	select
		vno,
		avtype
	from
	Adjstmnt
	where
		vtype = 'PR') as sttl on
	sttl.vno = s1.Vno
where
	(s1.status is null
		or s1.status <> 'C')
	and s1.trntype in ('PR')
	and sttl.avtype is null
	and s2.Ftrate>0
group by
	item.Barcode,
	(case
		when (item.Compcode = 465
			or item.Compcode = 459) then 'goodaid'
		else 'non-goodaid'
	end);
'''


wh_returns= pd.read_sql(q_7,cnxn)
mssql.close_connection()

# Concatenating the barcoded, non barcoded and wh_returns

warehouse_all=pd.concat([barcoded,non_barcoded,wh_returns],sort=False,ignore_index=False)

warehouse_all[['entity-id', 'franchise-id', 'drug-id']]= warehouse_all[['entity-id','franchise-id','drug-id']].apply(pd.to_numeric, errors='ignore').astype('Int64')

warehouse_merge=pd.merge(warehouse_all,drug_info,how='left',on='drug-id')



warehouse_merge[['drug-type', 'goodaid-flag']]=warehouse_merge[['drug-type', 'goodaid-flag']].fillna('NA')

warehouse_merge=warehouse_merge.drop(['drug-id'],axis=1)

warehouse_merge[['quantity']]=warehouse_merge[['quantity']].astype(np.int64)


warehouse_merge=warehouse_merge.groupby([ 'entity-name', 'entity-type','inventory-type',
                                        'inventory-sub-type-1','inventory-sub-type-2','inventory-sub-type-3','drug-type', 'goodaid-flag']).sum()



warehouse_merge=warehouse_merge.reset_index()



warehouse_merge[['entity-id']]=warehouse_merge[['entity-id']].replace(0, np.nan)



warehouse_merge[['franchise-id']]=warehouse_merge[['franchise-id']].replace(0, np.nan)



warehouse_merge=warehouse_merge[['entity-id', 'entity-name', 'entity-type', 'drug-type', 'goodaid-flag',
       'franchise-id', 'inventory-type', 'inventory-sub-type-1',
       'inventory-sub-type-2', 'inventory-sub-type-3', 'quantity',
       'value-without-tax', 'value-with-tax']]


system_inv = pd.concat([stores,to_be_dispatched,in_transit,return_query,warehouse_merge],sort=False,ignore_index=True)



system_inv[['entity-id', 'franchise-id']]= system_inv[['entity-id','franchise-id']].apply(pd.to_numeric, errors='ignore').astype('Int64')



system_inv[['quantity','value-without-tax', 'value-with-tax']]=system_inv[['quantity','value-without-tax', 'value-with-tax']].fillna(0)


system_inv[['quantity']]=system_inv[['quantity']].astype(np.int64)


system_inv[['value-without-tax', 'value-with-tax']]=system_inv[['value-without-tax', 'value-with-tax']].astype(np.float64)

system_inv['snapshot-date'] = snapshot_date


created_at = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
system_inv['created-at']=datetime.strptime(created_at,"%Y-%m-%d %H:%M:%S")
updated_at = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
system_inv['updated-at']=datetime.strptime(updated_at,"%Y-%m-%d %H:%M:%S")
system_inv['created-by'] = 'etl-automation'
system_inv['updated-by'] = 'etl-automation'


#Truncate the Query

truncate_query = '''
       delete from "prod2-generico"."system-inventory"
       where date("snapshot-date") = '{snapshot_date}'
       '''.format(snapshot_date=snapshot_date)

rs_db.execute(truncate_query)


system_inv.columns = [c.replace('_', '-') for c in system_inv.columns]



schema = "prod2-generico"
table_name = "system-inventory"
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)


s3.write_df_to_db(df=system_inv[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)

status=True


if status==True:
    script_status="Success"
else:
    script_status="Failed"



email = Email()
email.send_email_file(subject=f"system_inventory {snapshot_date} {script_status}",
                      mail_body=f"system inventory job status: {script_status} ",
                      to_emails=email_to)

# closing the DB connection in the end
rs_db.close_connection()