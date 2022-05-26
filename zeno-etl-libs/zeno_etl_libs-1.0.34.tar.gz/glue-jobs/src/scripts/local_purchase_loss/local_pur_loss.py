#!/usr/bin/env python
# coding: utf-8

# In[70]:


#!/usr/bin/env python
# coding: utf-8

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, PostGre
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper

import argparse
import pandas as pd
from datetime import date
from datetime import datetime
import dateutil.relativedelta
import numpy as np


# In[71]:


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="akshay.bhutada@zeno.health,vivek.sidagam@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to


# In[72]:


env = args.env
os.environ['env'] = env


# In[73]:


rs_db = DB()
s3=S3()


# In[74]:


rs_db.open_connection()


# In[75]:


q_aa='''
select
	a.id as "inventory-id",
	a."invoice-item-id" ,
	b.id as "invoice-item-id-1",
	a."batch-number" ,
	a.expiry ,
	b.vat ,
	c."invoice-date" ,
	d."type" ,
	d."drug-name" ,
	s."name" as "store-name",
	a."created-at" as "inventory-created-at" ,
	"barcode-reference" ,
	d.hsncode ,
	a."drug-id" ,
	c."invoice-number",
	AVG(a.quantity) as "quantity" ,
	AVG(a."locked-for-check") as "locked-for-check" ,
	AVG(a."transferred-out-quantity") as "transferred-out-quantity",
	AVG(a."transferred-in-quantity") as "transferred-in-quantity",
	AVG(a."locked-for-audit")  as "locked-for-audit",
	AVG(a."locked-for-return") as "locked-for-return" ,
	AVG(a."locked-for-transfer")  as  "locked-for-transfer",
	AVG(a.ptr )as "actual-fptr",
	AVG(b."actual-quantity") as "actual-quantity"  ,
	AVG(b."net-value") as "net-value" ,
	SUM(s2."net-quantity") as "net-quantity" ,
	AVG(s2.rate) as "selling-rate",
	AVG(s2."cgst-rate" +s2."sgst-rate" +s2."igst-rate") as "GST"
from
	"prod2-generico"."inventory-1" a
left join "prod2-generico"."invoices-1" c on
	a."franchisee-invoice-id" = c.id
left join "prod2-generico"."invoice-items-1" b on
	a."invoice-item-id" = b.id
left join "prod2-generico".drugs d on
	b."drug-id" = d.id
left join "prod2-generico".stores s on
	a."store-id" = s.id
left join "prod2-generico".sales s2 on a.id =s2."inventory-id" 
where
	c."invoice-reference" is null
group by
	a.id ,
	a."invoice-item-id" ,
	b.id ,
	a."batch-number" ,
	a.expiry ,
	b.vat ,
	c."invoice-date" ,
	d."type" ,
	d."drug-name" ,
	s."name",
	a."created-at" ,
	"barcode-reference" ,
	d.hsncode ,
	a."drug-id" ,
	c."invoice-number"
'''


# In[95]:


local_purchase_loss=rs_db.get_df(query=q_aa)


# In[96]:




# In[97]:


local_purchase_loss[['actual-fptr','vat','net-value','selling-rate','gst']]=local_purchase_loss[['actual-fptr','vat','net-value','selling-rate','gst']].apply(pd.to_numeric, errors='ignore').astype('float64')


# In[98]:


# In[99]:


# In[101]:


created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
local_purchase_loss['created-at']=datetime.strptime(created_at,"%Y-%m-%d %H:%M:%S")
updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
local_purchase_loss['updated-at']=datetime.strptime(updated_at,"%Y-%m-%d %H:%M:%S")
local_purchase_loss['created-by'] = 'etl-automation'
local_purchase_loss['updated-by'] = 'etl-automation'


# In[102]:


# In[103]:

local_purchase_loss['barcode-reference']=local_purchase_loss['barcode-reference'].fillna(0)
local_purchase_loss['barcode-reference']=local_purchase_loss['barcode-reference'].astype(str)
local_purchase_loss['barcode-reference'].replace(['0', '0.0'], '', inplace=True)


# In[104]:


local_purchase_loss[['invoice-item-id','invoice-item-id-1','actual-quantity','net-quantity']]=local_purchase_loss[['invoice-item-id','invoice-item-id-1','actual-quantity','net-quantity']].apply(pd.to_numeric, errors='ignore').astype('Int64')


# In[105]:


local_purchase_loss['invoice-date'] = pd.to_datetime(local_purchase_loss['invoice-date'], infer_datetime_format=True,errors = 'coerce')


# In[ ]:


schema = "prod2-generico"
table_name = "purchase-loss-accounts"
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)


# In[ ]:





# In[90]:
#Writing to table

s3.write_df_to_db(df=local_purchase_loss[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)


# In[ ]:
rs_db.close_connection()



