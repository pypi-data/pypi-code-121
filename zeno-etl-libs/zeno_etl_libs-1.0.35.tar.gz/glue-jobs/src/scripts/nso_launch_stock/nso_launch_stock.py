#Script NSO Launch Stock
#Importing the Libraries

import os
import sys
import numpy as np

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger

import argparse
import pandas as pd
from datetime import datetime
from dateutil.tz import gettz


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="akshay.bhutada@zeno.health", type=str, required=False)
parser.add_argument('-ns', '--new_store_id_list', default="", type=str, required=False)
parser.add_argument('-pr', '--proxy_store_list', default="", type=str, required=False)
args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env

logger = get_logger()

new_store_id_list = args.new_store_id_list
proxy_store_list = args.proxy_store_list
email_to = args.email_to



email = Email()




if new_store_id_list and type(new_store_id_list) == str:
    new_store_id_list = int(new_store_id_list)
else:
    email.send_email_file(subject="nso_launch_stock_failed",
                          mail_body="please insert the new_store_id",
                          to_emails=email_to)
    mssg = "wrong input parameters passed as store id list is {} and type of list " \
           "is {}".format(new_store_id_list, type(new_store_id_list))
    raise Exception(mssg)



if proxy_store_list and type(proxy_store_list) == str:
    proxy_store_list = tuple([int(x) for x in proxy_store_list.split(",")])
else:
    email.send_email_file(subject="nso_launch_stock_failed",
                          mail_body="please insert at-least two proxy_stores",
                          to_emails=email_to)
    mssg = "wrong input parameters passed as proxy store list  is {} and type of list " \
           "is {}".format(proxy_store_list, type(proxy_store_list))
    raise Exception(mssg)




rs_db = DB()

rs_db.open_connection()


s3 = S3()



# Current Date

run_date = str(datetime.now(tz=gettz('Asia/Kolkata')).now())



# Proxy stores sales history available in last 90 days

proxy = '''
select
sa."store-id", (max(date(sa."created-at"))-min(date(sa."created-at"))) as days
from
"prod2-generico".sales as sa
where
sa."store-id" In {store_id}
and date(sa."created-at") 
between date(trunc(GETDATE()) -interval '91 days') 
and date(trunc(GETDATE()) -interval '1 days')
group by sa."store-id" '''.format(store_id=proxy_store_list)


proxy=rs_db.get_df(query=proxy)


# Base Logic
# Sales data in last 90 days

q_sales_data = '''select
                "drug-id","store-id" ,SUM("net-quantity") as "net-quantity"
                from
                "prod2-generico".sales sa
                where
                sa."store-id" In {store_id}
                and date(sa."created-at") between date(trunc(GETDATE()) -interval '91 days') 
                and date(trunc(GETDATE()) -interval '1 days')
                group by "drug-id","store-id" '''.format(store_id=proxy_store_list)


sales_data=rs_db.get_df(query=q_sales_data)


# PR Loss in last 90 days

pr_loss_query = '''
select
	cpr."drug-id",
	cpr."store-id" ,
	sum(cpr."loss-quantity") as "loss-quantity"
from
	"prod2-generico"."cfr-patient-request" cpr
where
	cpr."store-id" in {store_id}
	and date(cpr."shortbook-date") between date(current_date -interval '91 days') and date(current_date -interval '1 days')
	and cpr."drug-id" <> -1
	and cpr."loss-quantity" > 0
group by
	cpr."drug-id",
	cpr."store-id"
'''.format(store_id=proxy_store_list)


pr_loss=rs_db.get_df(query=pr_loss_query)

pr_loss.columns = [c.replace('_', '-') for c in pr_loss.columns]

merge_demand = pd.merge(sales_data, pr_loss, on=['store-id', 'drug-id'], how='outer')

merge_demand['net-quantity'].fillna(0, inplace=True)

merge_demand['loss-quantity'].fillna(0, inplace=True)

merge_demand['loss-quantity']=merge_demand['loss-quantity'].astype(np.float64)

merge_demand['total_demand'] = (merge_demand['net-quantity'] + merge_demand['loss-quantity'])

merge_demand = merge_demand.drop(["net-quantity", "loss-quantity"], axis=1)

merge_demand.columns = [c.replace('_', '-') for c in merge_demand.columns]

base_logic = pd.merge(merge_demand, proxy, how='left', on='store-id')

base_logic['avg_per_month'] = (base_logic['total-demand'] / base_logic['days']) * 30

base_logic = base_logic.groupby(['drug-id']).sum()

base_logic = base_logic.drop(['store-id', 'total-demand', 'days'], axis=1)

avg_net_quan = base_logic[['avg_per_month']] / (len(proxy_store_list))

avg_net_quan = avg_net_quan[avg_net_quan['avg_per_month'] > 0.8]

base_logic = pd.merge(base_logic, avg_net_quan, left_index=True, right_index=True)


# Other Category

# Top 80 % other category drugs by quantity sold in last 90 days across the network

q_other_cat = '''
select
    "drug-id" ,
    "drug-name" ,
    "type" ,
    composition ,
    SUM("net-quantity") as "net-quantity"
from
    "prod2-generico".sales sa
where
    sa."type" not in ('ethical', 'generic')
    and date(sa."created-at") between date(trunc(GETDATE()) -interval '91 days') and date(trunc(GETDATE()) -interval '1 days')
group by
    "drug-id",
    "drug-name",
    "type",
    composition
order by SUM("net-quantity") desc
'''


other_cat=rs_db.get_df(query=q_other_cat)

a = other_cat['net-quantity'].sum() * 0.8

other_cat = other_cat[other_cat['net-quantity'].cumsum() < a]


# Generic Adjustment

# Warehouse generic Portfolio

q_generic_wh_portfolio = '''
select
    composition,
    "drug-id" as "drug-id"
from
    (
    select
        d.composition,
        wssm."drug-id",
        d."drug-name" ,
        SUM(sh."net-quantity"),
        rank() over (partition by d.composition
    order by
        SUM(sh."net-quantity") desc) as rn
    from
        "prod2-generico"."wh-sku-subs-master" wssm
    left join "prod2-generico".drugs d  on wssm."drug-id" =d.id
    left join "prod2-generico".sales sh on
        wssm."drug-id" =sh."drug-id" 
    where
        wssm."add-wh" = 'Yes'
        and d."type" ='generic'
    group by
        d.composition ,
        wssm."drug-id" ,
        d."drug-name") a
where
    a.rn = 1;
'''

# All the drugs in warehouse generic portfolio

q_all_generic_portfolio = '''
select
     distinct d.composition,
     wssm."drug-id" as "drug-id"
from
   "prod2-generico"."wh-sku-subs-master" wssm
 left join "prod2-generico".drugs d on wssm."drug-id" =d.id 
where
    d."type" ='generic'
and wssm."add-wh" = 'Yes'  
'''

generic_wh_portfolio =rs_db.get_df(query=q_generic_wh_portfolio)


generic_wh_all_portfolio=rs_db.get_df(query=q_all_generic_portfolio)

# common_drug_adjustment

#  Drug sold in 80 % of stores

t_1 = '''
select COUNT(a."store-id") from 
(select
    sa."store-id", (max(date(sa."created-at"))-min(date(sa."created-at"))) as days
from
    "prod2-generico".sales as sa
where
 date(sa."created-at") between date(trunc(GETDATE()) -interval '91 days') and date(trunc(GETDATE()) -interval '1 days')
group by sa."store-id" ) a
where
    a.days >= 90;
'''

sales_90_days=rs_db.get_df(query=t_1)
total_stores = int(sales_90_days.iloc[0])

# 80 % of stores

total_stores_perc = round(0.8 * total_stores)

q_common_drug = '''

select
    *
from
    (
    select
        sa."drug-id",
        COUNT(distinct sa."store-id") as "store-count"
    from
        "prod2-generico".sales as sa
    where
         date(sa."created-at") between date(trunc(GETDATE()) -interval '91 days') and date(trunc(GETDATE()) -interval '1 days') 
        and 
        sa."store-id"	
        in (
select a."store-id" from 
(select
    sa."store-id", (max(date(sa."created-at"))-min(date(sa."created-at"))) as days
from
    "prod2-generico".sales as sa
where
 date(sa."created-at") between date(trunc(GETDATE()) -interval '91 days') and date(trunc(GETDATE()) -interval '1 days')
group by sa."store-id" ) a
where
    a.days >= 90)
    group by
        sa."drug-id" ) b
'''
rs_db.execute(query=q_common_drug, params=None)

common_drug: pd.DataFrame = rs_db.cursor.fetch_dataframe()

common_drug = common_drug[common_drug['store-count'] > total_stores_perc]

q_goodaid = '''select
	composition,
	"drug-id" as "drug-id"
from
	(
	select
		d.composition,
		wssm."drug-id",
		d."drug-name"
	from
		 "prod2-generico"."wh-sku-subs-master" wssm
	left join "prod2-generico".drugs d on wssm."drug-id"=d.id
	where
		wssm."add-wh" = 'Yes'
		and d."company-id" = 6984
	group by
		d.composition ,
		wssm."drug-id",
		d."drug-name") a'''

goodaid_wh_portfolio=rs_db.get_df(query=q_goodaid)


# CFR-1 part-1

# Drug Search repeated in last four month  in proxy stores

q_cfr_1 = '''
            select
"drug-id" as "drug-id"
from
	(
	select
		"drug-id",
		"drug-name-y" ,
		Count(distinct month_year) as m_y
	from
		(
		select
			to_char(cs."search-date", 'YYYY-MM') as month_year ,
			cs."drug-id" ,
			cs."drug-name-y"
		from
			"prod2-generico"."cfr-searches-v2" cs
		where
			date(cs."search-date") between date(date_trunc('month', current_date -interval '4 month')) and date(date_trunc('month', current_date)- interval '1 day')
			and cs."store-id" in {store_id}
			and cs."final-lost-sales" >0
		group by
			month_year ,
			cs."drug-id",
			cs."drug-name-y") a
	group by
		a."drug-id",
		a."drug-name-y"
	having
		Count(distinct month_year)= 4) a     
                '''.format(store_id=proxy_store_list)

cfr_search_1 = rs_db.execute(query=q_cfr_1, params=None)
cfr_search_1: pd.DataFrame = rs_db.cursor.fetch_dataframe()

#cfr_search_1=rs_db.get_df(query=q_cfr_1)



# CFR Logic-1 part-2

# Drug search repeated  in 3-month (Rolling) (last four months CFR history considered)

q_cfr_2 = '''select
	"drug-id" as "drug-id"
from
	(
	select
		a."drug-id", 
		MONTHS_BETWEEN (date(date_trunc('month', max("search-date"))) , date(date_trunc('month', min("search-date")))) as diff,
		date(date_trunc('month', max("search-date"))),date(date_trunc('month', min("search-date"))),
		Count(distinct month_year) as m_y
	from
		(
		select
			cs."search-date",
			to_char(cs."search-date", 'YYYY-MM') as month_year ,
			cs."drug-id" ,
			cs."drug-name-y"
		from
			"prod2-generico"."prod2-generico"."cfr-searches-v2"  cs
		where
			date(cs."search-date") between date(date_trunc('month', current_date -interval '4 month')) and date(date_trunc('month', current_date)- interval '1 day')
			and cs."store-id" in {store_id}
			and cs."final-lost-sales" >0 
		group by
			cs."search-date",
			month_year ,
			cs."drug-id",
			cs."drug-name-y") a
	group by
		a."drug-id"
	having
		Count(distinct month_year)= 3) b
where
	b.diff = 2
            '''.format(store_id=proxy_store_list)

#cfr_search_2=rs_db.get_df(query=q_cfr_2)

cfr_search_2 = rs_db.execute(query=q_cfr_2, params=None)
cfr_search_2: pd.DataFrame = rs_db.cursor.fetch_dataframe()


# CFR Logic-2

# Drug search repeated in last two month throughout the proxy stores.

q_cfr_3 = '''select
	"drug-id" as "drug-id"
from
	(
	select
		"drug-id",
		"drug-name-y" ,
		Count(distinct month_year) as m_y,
		Count(distinct "store-id") as stores
	from
		(
		select
			to_char(cs."search-date", 'YYYY-MM') as month_year,
			cs."store-id" ,
			cs."drug-id" ,
			cs."drug-name-y"
		from
			"prod2-generico"."cfr-searches-v2" cs
		where
			date(cs."search-date") between date(date_trunc('month', current_date -interval '2 month')) and date(date_trunc('month', current_date)- interval '1 day')
			and cs."store-id" in {store_id}
			and cs."final-lost-sales" >0
		group by
			month_year ,
			cs."store-id",
			cs."drug-id",
			cs."drug-name-y") a
	group by
		a."drug-id",
		a."drug-name-y"
	having
		Count(distinct month_year)= 2
		and Count(distinct "store-id")= {proxy_store}) b '''.format(store_id=proxy_store_list,proxy_store=len(proxy_store_list))



#cfr_search_3=rs_db.get_df(query=q_cfr_3)

cfr_search_3 = rs_db.execute(query=q_cfr_3, params=None)
cfr_search_3: pd.DataFrame = rs_db.cursor.fetch_dataframe()

if cfr_search_1 is None:
    cfr_search_1=pd.DataFrame()
    cfr_search_1['drug-id']='drug-id'
    cfr_search_1.to_csv(r"D:\NSO\cfr.csv")
else:
   cfr_search_1=cfr_search_1

if cfr_search_2 is None:
    cfr_search_2=pd.DataFrame()
    cfr_search_2['drug-id']='drug-id'
else:
   cfr_search_2=cfr_search_2

if cfr_search_3 is None:
    cfr_search_3=pd.DataFrame()
    cfr_search_3['drug-id']='drug-id'
else:
   cfr_search_3=cfr_search_3

drug_info = '''
select
    d.id as "drug-id" ,
    d."drug-name" as "drug-name",
    d."type" as "drug-type" ,
    d."company-id" as "company-id",
    d.company as company,
    d.category as "drug-category",
    d.composition as composition
from
    "prod2-generico".drugs d
'''


drug_info=rs_db.get_df(drug_info)


# ptr-info


ptr_info = '''
select
 i2."drug-id" ,avg(ptr) as "avg-ptr"
from
    "prod2-generico"."inventory-1" i2 
where
     date(i2."created-at") between date(trunc(GETDATE()) -interval '366 days') and date(trunc(GETDATE()) -interval '1 days')
group by
    i2."drug-id" 
'''


avg_ptr=rs_db.get_df(query=ptr_info)

base_logic = base_logic.drop(["avg_per_month_x", "avg_per_month_y"], axis=1)

other_cat = other_cat.drop(["drug-name", "type", "composition", "net-quantity"], axis=1)

generic_wh_portfolio = generic_wh_portfolio.drop(['composition'], axis=1)

common_drug = common_drug.drop(['store-count'], axis=1)

goodaid_wh_portfolio = goodaid_wh_portfolio.drop(['composition'], axis=1)


# Merging with drug info

base_logic_new = pd.merge(base_logic, drug_info,
                          how='left', on=['drug-id'])
other_cat_new = pd.merge(other_cat, drug_info, how='left', on=['drug-id'])
generic_wh_portfolio_new = pd.merge(generic_wh_portfolio, drug_info, how='left', on=['drug-id'])
common_drug_new = pd.merge(common_drug, drug_info, how='left', on=['drug-id'])
goodaid_wh_portfolio_new = pd.merge(goodaid_wh_portfolio, drug_info, how='left', on=['drug-id'])

cfr_search_1_new = pd.merge(cfr_search_1, drug_info, how='left', on=['drug-id'])
cfr_search_2_new = pd.merge(cfr_search_2, drug_info, how='left', on=['drug-id'])
cfr_search_3_new = pd.merge(cfr_search_3, drug_info, how='left', on=['drug-id'])

rs_db.close_connection()


# Dropping the duplicated (if any)

base_logic_new = base_logic_new.drop_duplicates()
other_cat_new = other_cat_new.drop_duplicates()
generic_wh_portfolio_new = generic_wh_portfolio_new.drop_duplicates()
common_drug_new = common_drug_new.drop_duplicates()
goodaid_wh_portfolio_new = goodaid_wh_portfolio_new.drop_duplicates()
cfr_search_1_new = cfr_search_1_new.drop_duplicates()
cfr_search_2_new = cfr_search_2_new.drop_duplicates()
cfr_search_3_new = cfr_search_3_new.drop_duplicates()

base_logic_new['source'] = 'proxy_stores_base_logic'
other_cat_new['source'] = 'network_other_category'
generic_wh_portfolio_new['source'] = 'wh_generic'
common_drug_new['source'] = 'network_common_drugs'
goodaid_wh_portfolio_new['source'] = 'wh_goodaid'
cfr_search_1_new['source'] = 'CFR-1'
cfr_search_2_new['source'] = 'CFR-1'
cfr_search_3_new['source'] = 'CFR-2'

# merging base logic and other category Adjustment-1
merge_1 = pd.merge(base_logic_new, other_cat_new, how='outer',
                   left_on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                            'drug-category', 'composition'],
                   right_on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                             'drug-category', 'composition'])

merge_1['source_x'] = merge_1['source_x'].fillna('network_other_category')
merge_1 = merge_1.drop(['source_y'], axis=1)
merge_1 = merge_1.rename(columns={"source_x": "source"})


# Dropping Duplicates

merge_1 = merge_1.drop_duplicates(subset=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                                          'drug-category', 'composition'])

# Generic Adjustment

generic = merge_1[merge_1['drug-type'] == 'generic']
non_generic = merge_1[merge_1['drug-type'] != 'generic']

# Generic Composition

generic_composition = generic[["composition"]]

# Unique Generic Composition
generic_composition_unique = generic_composition.drop_duplicates()
# Warehouse Generic Portfolio
generic_portfolio = generic_wh_portfolio_new[["composition"]]
# Compoistions not part of base logic
portfolio_extra = generic_portfolio[
    ~generic_portfolio['composition'].isin(generic_composition_unique['composition'])]

generic_1 = pd.merge(generic_composition, generic, how='left', on=['composition'])
generic_1 = generic_1.drop_duplicates()
portfolio_extra_1 = pd.merge(portfolio_extra, generic_wh_portfolio_new, how='left', on=['composition'])
portfolio_extra_1 = portfolio_extra_1.drop_duplicates()
# Merging portfolio extra drugs and  base logic generics
merge_2 = pd.concat([generic_1, portfolio_extra_1])

# Generic Adjustment-2

generic = merge_2[merge_2['drug-type'] == 'generic']
generic_drugs = generic[['drug-id']]
generic_drugs_composition = generic[['drug-id', 'composition']]

# All generic drugs in warehouse portfolio
generic_wh_all_portfolio_drug = generic_wh_all_portfolio[['drug-id']]

# Generic drugs not in the portfolio
generic_drug_not_in_portfolio = generic_drugs[~generic_drugs['drug-id'].isin(generic_wh_all_portfolio['drug-id'])]

# Generic drugs  in the portfolio
generic_drug_in_portfolio = generic_drugs[generic_drugs['drug-id'].isin(generic_wh_all_portfolio['drug-id'])]

# Merging the generic drug in portfolio
generic_drug_in_portfolio = pd.merge(generic_drug_in_portfolio, generic, how='left', on='drug-id')

generic_drug_not_in_portfolio_composition = pd.merge(generic_drug_not_in_portfolio, generic_drugs_composition,
                                                     how='left', on='drug-id')
# replaced the drugs with highest selling drugs in that composition from warehouse portfolio
generic_adjustment_2 = pd.merge(generic_drug_not_in_portfolio_composition['composition'], generic_wh_portfolio_new,
                                how='inner',
                                on='composition')
# dropping duplicates
generic_adjustment_2 = generic_adjustment_2.drop_duplicates()

generic_adjustment_2 = generic_adjustment_2[
    ['drug-id', 'composition', 'drug-name', 'drug-type', 'company-id', 'company', 'drug-category', 'source']]
generic_composition_not_in_generic_portfolio = generic_drug_not_in_portfolio_composition[
    ~generic_drug_not_in_portfolio_composition['composition'].isin(generic_wh_portfolio_new['composition'])]
generic_composition_not_in_generic_portfolio = pd.merge(generic_composition_not_in_generic_portfolio, generic,
                                                        how='left', on=['drug-id', 'composition'])

merge_2 = pd.concat(
    [generic_composition_not_in_generic_portfolio, generic_adjustment_2, generic_drug_in_portfolio])

merge_2 = merge_2.drop_duplicates(subset=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                                          'drug-category', 'composition'])
merge_2 = merge_2[
    ['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
     'drug-category', 'composition', 'source']]

# merging the non-generic and generic drug after generic adjustment-2

merge_3 = pd.concat([non_generic, merge_2])

# Common Drug Adjustment

# Merging the with common drug adjustment

merge_4 = pd.merge(merge_3, common_drug_new, how='outer',
                   left_on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                            'drug-category', 'composition'],
                   right_on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                             'drug-category', 'composition'])

merge_4['source_x'] = merge_4['source_x'].fillna('network_common_drugs')
merge_4 = merge_4.drop(['source_y'], axis=1)
merge_4 = merge_4.rename(columns={"source_x": "source"})

merge_4 = merge_4.drop_duplicates(subset=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                                          'drug-category', 'composition'])

# Goodaid Adjustment

generic_2 = merge_4[merge_4['drug-type'] == 'generic']
non_generic_2 = merge_4[merge_4['drug-type'] != 'generic']
generic_composition_2 = generic_2[["composition"]]

# Goodaid composition

goodaid_composition = goodaid_wh_portfolio_new[['composition']]

# Composition which is part of goodaid portfolio
generic_removal = generic_composition_2[generic_composition_2['composition'].isin(goodaid_composition['composition'])]

# Composition not part of goodaid portfolio

generic_without_GA = generic_2[~generic_2['composition'].isin(generic_removal['composition'])]
df_goodaid = pd.merge(generic_removal, goodaid_wh_portfolio_new, how='left', on=['composition'])
df_goodaid = df_goodaid.drop_duplicates()
df_goodaid['source'] = 'wh_goodaid'
df_goodaid = df_goodaid[
    ['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
     'drug-category', 'composition', 'source']]
merge_5 = pd.concat([generic_without_GA, df_goodaid])
merge_5 = pd.concat([non_generic_2, merge_5])

# CFR-Search
merge_6 = pd.merge(merge_5, cfr_search_1_new, how='outer',
                   on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                       'drug-category', 'composition'])

merge_6['source_x'] = merge_6['source_x'].fillna('CFR-1')
merge_6 = merge_6.drop(['source_y'], axis=1)
merge_6 = merge_6.rename(columns={"source_x": "source"})

merge_7 = pd.merge(merge_6, cfr_search_2_new, how='outer',
                   on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                       'drug-category', 'composition'])

merge_7['source_x'] = merge_7['source_x'].fillna('CFR-1')
merge_7 = merge_7.drop(['source_y'], axis=1)
merge_7 = merge_7.rename(columns={"source_x": "source"})

merge_8 = pd.merge(merge_7, cfr_search_3_new, how='outer',
                   on=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                       'drug-category', 'composition'])

merge_8['source_x'] = merge_8['source_x'].fillna('CFR-2')
merge_8 = merge_8.drop(['source_y'], axis=1)
merge_8 = merge_8.rename(columns={"source_x": "source"})

merge_8 = merge_8.drop_duplicates(subset=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                                          'drug-category', 'composition'])

# CFR Adjustment-1 (Generic)

generic_wh_all_portfolio_drug = generic_wh_all_portfolio[['drug-id']]

generic_3 = merge_8[merge_8['drug-type'] == 'generic']

generic_drugs_3 = generic_3[['drug-id']]

non_generic_3 = merge_8[merge_8['drug-type'] != 'generic']

generic_drug_in_portfolio_3 = generic_drugs_3[generic_drugs_3['drug-id'].isin(generic_wh_all_portfolio_drug['drug-id'])]

generic_drug_not_in_portfolio_3 = generic_drugs_3[
    ~generic_drugs_3['drug-id'].isin(generic_wh_all_portfolio_drug['drug-id'])]

df_generic_drugs_in_portfolio = pd.merge(generic_drug_in_portfolio_3, generic_3,
                                         how='left', on='drug-id')

merge_9 = pd.concat([non_generic_3, df_generic_drugs_in_portfolio])

# CFR Adjustment-2 (Goodaid)

goodaid_composition = goodaid_wh_portfolio_new[['composition']]

generic_4 = merge_9[merge_9['drug-type'] == 'generic']
non_generic_4 = merge_9[merge_9['drug-type'] != 'generic']
generic_4_composition = generic_4[['composition']]

generic_composition_goodaid = generic_4_composition[
    generic_4_composition['composition'].isin(goodaid_composition['composition'])]
generic_composition_non_goodaid = generic_4_composition[
    ~generic_4_composition['composition'].isin(goodaid_composition['composition'])]
generic_composition_goodaid = pd.merge(generic_composition_goodaid, generic_4, how='left',
                                       left_index=True, right_index=True, on='composition')

generic_composition_goodaid = generic_composition_goodaid[
    generic_composition_goodaid['company'] == 'GOODAID']
non_goodaid = pd.merge(generic_composition_non_goodaid, generic_4, how='left', left_index=True,
                       right_index=True, on='composition')
non_goodaid = non_goodaid[
    ['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
     'drug-category', 'composition', 'source']]
goodaid = generic_composition_goodaid[
    ['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
     'drug-category', 'composition', 'source']]
merge_10 = pd.concat([non_generic_4, non_goodaid, goodaid])

# Removing the banned products

merge_10 = merge_10[merge_10['drug-type'] != 'banned']

# removing the discontinued products

merge_10 = merge_10[merge_10['drug-type'] != 'discontinued-products']

merge_10 = merge_10.drop_duplicates(subset=['drug-id', 'drug-name', 'drug-type', 'company-id', 'company',
                                            'drug-category', 'composition'])

merge_10 = pd.merge(merge_10, avg_net_quan, how='left', on='drug-id')

merge_10 = pd.merge(merge_10, avg_ptr, how='left', on='drug-id')

merge_10['avg_per_month'] = merge_10['avg_per_month'].fillna(1)

merge_10['avg_per_month'] = merge_10['avg_per_month'].round(0).astype(int)

merge_10 = merge_10.rename(columns={'avg_per_month': 'monthly_avg_quantity'})

merge_10['active'] = 1

merge_10['proxy_stores'] = str(proxy_store_list)

merge_10['new_store_id'] = new_store_id_list

merge_10['run_date'] = run_date

merge_10.columns = [c.replace('_', '-') for c in merge_10.columns]



nso_assortment_file_name = 'nso_assortment/nso_launch_stock_store_id_{}.csv'.format(new_store_id_list)


# Uploading File to S3
nso_assortment_uri = s3.save_df_to_s3(df=merge_10, file_name=nso_assortment_file_name)




email.send_email_file(subject=f"nso assortment for new_store_id {new_store_id_list}",
                      mail_body=f"nso assortment for new_store_id {new_store_id_list} proxy store list is {proxy_store_list}",
                      to_emails=email_to, file_uris=[nso_assortment_uri])

rs_db.close_connection()
