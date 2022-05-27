"""
Author:jnanansu.bisoi@zeno.health
Purpose: Comparing sales change between any two time periods
"""
#importing libraries
from datetime import datetime
import numpy as np
import pandas as pd
from decimal import Decimal
import xlsxwriter
import csv
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

pd.set_option('display.max_columns', None)
from warnings import filterwarnings
filterwarnings("ignore")
import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
from dateutil.tz import gettz


st_dt1 = (datetime.now()-timedelta(days = 2)).strftime("%Y-%m-%d")
ed_dt1 = (datetime.now()-timedelta(days = 2)).strftime("%Y-%m-%d")

st_dt2 = (datetime.now()-timedelta(days = 1)).strftime("%Y-%m-%d")
ed_dt2 = (datetime.now()-timedelta(days = 1)).strftime("%Y-%m-%d")


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="jnanansu.bisoi@zeno.health", type=str, required=False)
parser.add_argument('-sd1', '--start_date1', default=None, type= str, required=False)
parser.add_argument('-ed1', '--end_date1', default=None, type= str, required=False)
parser.add_argument('-sd2', '--start_date2', default=None, type= str, required=False)
parser.add_argument('-ed2', '--end_date2', default='', type= str, required=False)
parser.add_argument('-p', '--param',default= "old_new", type= str, required=False)
parser.add_argument('-pl', '--param_limit',default= 10, type= int, required=False )
parser.add_argument('-ml', '--max_level',default= 5, type= int, required=False )
parser.add_argument('-fr', '--full_run',default= 'yes', type= str, required=False )
parser.add_argument('-dt', '--data',default= 'summary', type= str, required=False )
parser.add_argument('-fc', '--filter_cutoff',default= 0.05, type= float, required=False )
parser.add_argument('-ad', '--additional_data',default= 'absolute_impact', type= str, required=False )
parser.add_argument('-tp', '--top_parameter',default= 5, type= int, required=False )
parser.add_argument('-ms', '--manual_sorting',default= 'no', type= str, required=False )
parser.add_argument('-dr', '--direction',default= 'same', type= str, required=False )


args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

# parameters
email_to = args.email_to
start_date1 = args.start_date1
end_date1 = args.end_date1
start_date2 = args.start_date2
end_date2 = args.end_date2
param = args.param
param_limit = args.param_limit
max_level = args.max_level
full_run = args.full_run
data = args.data
filter_cutoff = args.filter_cutoff
additional_data = args.additional_data
top_parameter = args.top_parameter
manual_sorting = args.manual_sorting
direction = args.direction

if start_date1 == None and end_date1 == None:
    start_date1 = st_dt1
    end_date1 = ed_dt1

if start_date2 == None and end_date2 == '':
    start_date2 = st_dt2
    end_date2 = ed_dt2

logger = get_logger()

logger.info(f"env: {env}")
logger.info(f"print the env again: {env}")


schema = 'prod2-generico'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

read_schema = 'prod2-generico'


# Query to fetch sales data
query1 = f"""
select
s."bill-id" ,
s."patient-id" ,
s."store-id" ,
s."drug-id" ,
s."drug-name" as drug ,
s."type" ,
s.category ,
(case when s.composition = '' then 'null_composition' else s.composition end) as "composition",
s.company ,
(case when s."bill-flag" = 'gross' then s.quantity
     when s."bill-flag" = 'return' then (-1*s.quantity)
     else 0
     end) as quantity,
date(s."created-at" ),
s.rate ,
s.ptr ,
s."substitution-status" ,
s."created-by" as "store-staff",
s."bill-flag" ,
s."old-new" ,
s."payment-method" ,
s."promo-code" ,
s."pc-type" ,
(case when s."pr-flag" = true then 'PR' else 'Non-PR' end) as "PR-flag" ,
(case when s."hd-flag" = true then 'HD' else 'Non-HD' end) as "HD-flag" ,
(case when s."ecom-flag" = true then 'Ecom' else 'store' end) as "Ecom-flag" ,
s."store-name" ,
s."line-manager" ,
s.city ,
s.abo ,
s."franchisee-id" ,
s."franchisee-name" ,
s."cluster-id" ,
s."cluster-name" ,
s."drug-grade" ,
s."doctor-id" ,
(case when s."bill-flag" = 'gross' then (s.rate * s.quantity)
     when s."bill-flag" = 'return' then (-1*(s.rate * s.quantity))
     else 0
     end) as sales
from
"{read_schema}".sales s 
where date(s."created-at" ) between '{start_date1}' and '{end_date1}';
"""

# sales data for period 1
query = query1
mos1 = rs_db.get_df(query = query)
mos1.columns = [c.replace('-', '_') for c in mos1.columns]

# for period 2
query2 = f"""
select
s."bill-id" ,
s."patient-id" ,
s."store-id" ,
s."drug-id" ,
s."drug-name" as drug,
s."type" ,
s.category ,
(case when s.composition = '' then 'null_composition' else s.composition end) as "composition",
s.company ,
(case when s."bill-flag" = 'gross' then s.quantity
     when s."bill-flag" = 'return' then (-1*s.quantity)
     else 0
     end) as quantity,
date(s."created-at" ),
s.rate ,
s.ptr ,
s."substitution-status" ,
s."created-by" as "store-staff",
s."bill-flag" ,
s."old-new" ,
s."payment-method" ,
s."promo-code" ,
s."pc-type" ,
(case when s."pr-flag" = true then 'PR' else 'Non-PR' end) as "PR-flag" ,
(case when s."hd-flag" = true then 'HD' else 'Non-HD' end) as "HD-flag" ,
(case when s."ecom-flag" = true then 'Ecom' else 'store' end) as "Ecom-flag" ,
s."store-name" ,
s."line-manager" ,
s.city ,
s.abo ,
s."franchisee-id" ,
s."franchisee-name" ,
s."cluster-id" ,
s."cluster-name" ,
s."drug-grade" ,
s."doctor-id" ,
(case when s."bill-flag" = 'gross' then (s.rate * s.quantity)
     when s."bill-flag" = 'return' then (-1*(s.rate * s.quantity))
     else 0
     end) as sales
from
"{read_schema}".sales s 
where date(s."created-at" ) between '{start_date2}' and '{end_date2}';
"""

# sales data for period 2
mos2 = rs_db.get_df(query=query2)
mos2.columns = [c.replace('-', '_') for c in mos2.columns]


# defining change fuction
def change(A,B):
    if A is None:
        return float(np.round(B,2))
    elif B is None:
        return float(np.round((-1*A),2))
    elif A is None and B is None:
        return float(0)
    else:
        return float(np.round((B-A),2))


# Defining function to calculate percentage change
def per_change(A, B):
    if (A == 0):
        return float((B - A))
    elif (A == B):
        return float((B - A))
    else:
        return float(((B - A) / A) * 100)


# The function takes the bills-1 table and the period as 'period1' or 'period2'
def sale(table):
    return float(table['sales'].sum())

def break_sale(table, sale_type):
    if sale_type == 'gross':
        mos_gs_local = table[table['bill_flag'] == 'gross']
        return mos_gs_local
    if sale_type == 'return':
        mos_ret_local = table[table['bill_flag'] == 'return']
        mos_ret_local['sales'] = np.where(mos_ret_local['sales'] <= 0, -1 * mos_ret_local['sales'],
                                          mos_ret_local['sales'])
        mos_ret_local['quantity'] = np.where(mos_ret_local['quantity'] <= 0, -1 * mos_ret_local['quantity'],
                                             mos_ret_local['quantity'])
        return mos_ret_local

# Defining functions for all required metrics
def num_cust(table):
    num = table.patient_id.nunique()
    return float(num)

def avg_gs_per_customer(table):
    gs = sale(table)
    num = num_cust(table)
    return (gs / num) if (num) != 0 else 0

def num_bills(table):
    num = table.bill_id.nunique()
    return float(num)

def avg_gs_per_bill(table):
    gs = sale(table)
    num = num_bills(table)
    return (gs / num) if (num) != 0 else 0

def num_drugs(table):
    num = table.drug_id.nunique()
    return float(num)

def avg_gs_per_drug(table):
    gs = sale(table)
    num = num_drugs(table)
    return (gs / num) if (num) != 0 else 0

def num_quantity(table):
    num = table['quantity'].sum()
    return float(num)

def rate(table):
    gs = sale(table)
    num = num_quantity(table)
    return (gs / num) if (num) != 0 else 0

def num_bills_per_customer(table):
    num1 = num_bills(table)
    num2 = num_cust(table)
    return (num1 / num2) if (num2) != 0 else 0

def num_quantity_per_bill(table):
    num1 = num_quantity(table)
    num2 = num_bills(table)
    return (num1 / num2) if (num2) != 0 else 0

# taking num of unique drug-bill combination
def num_bills_drugs(table):
    num = len(table[['bill_id', 'drug_id']].drop_duplicates())
    return float(num)

def num_drugs_per_bill(table):
    num1 = num_bills_drugs(table)
    num2 = num_bills(table)
    return (num1 / num2) if (num2) != 0 else 0

def num_quantity_per_drug(table):
    num1 = num_quantity(table)
    num2 = num_drugs(table)
    return (num1 / num2) if (num2) != 0 else 0

def avg_gs_per_drug_per_bill(table):
    gs = sale(table)
    num = num_bills_drugs(table)
    return (gs / num) if (num) != 0 else 0

def num_quantity_per_drug_per_bill(table):
    num1 = num_quantity(table)
    num2 = num_bills_drugs(table)
    return (num1 / num2) if (num2) != 0 else 0


#Defining function to find cont factor of metrics
def metric_factor(gs2_sim,ret_per2,gs2_local,ns2_local,ns2_global):
    ret2_sim = float(gs2_sim) * float(ret_per2)
    ns2_sim = float(gs2_local) - float(ret2_sim)
    metric_fact = np.divide((ns2_local - ns2_sim),ns2_global)*100
    return float(metric_fact)

# Function to store metric values in dictionary
def metric(t1, t2, ns2_local, gs1_local, gs2_local, ret_per1, ret_per2, ns2_global):
    # defining dictionary to store the metrics
    d = {}

    # No. of customers
    nc1 = num_cust(t1)
    nc2 = num_cust(t2)
    # Avg gs per customer:
    agpc1 = avg_gs_per_customer(t1)
    agpc2 = avg_gs_per_customer(t2)
    # Cont of Num of cust
    gs2_sim = float(agpc2) * float(nc1)
    d['nc'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)
    # Cont of ACV
    gs2_sim = float(agpc1) * float(nc2)
    d['ACV'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)

    # No. of bills per customer
    nbpc1 = num_bills_per_customer(t1)
    nbpc2 = num_bills_per_customer(t2)
    # avg_gs_per_bill
    agpb1 = avg_gs_per_bill(t1)
    agpb2 = avg_gs_per_bill(t2)
    # cont of number of bills
    agpc2_sim = float(nbpc1) * float(agpb2)
    gs2_sim = agpc2_sim * float(nc2)
    d['nbpc'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)
    # cont. of ABV
    agpc2_sim = float(nbpc2) * float(agpb1)
    gs2_sim = agpc2_sim * float(nc2)
    d['ABV'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)

    # num of drugs per bill
    ndpb1 = num_drugs_per_bill(t1)
    ndpb2 = num_drugs_per_bill(t2)
    # avg gs per drug per bill
    agpdpb1 = avg_gs_per_drug_per_bill(t1)
    agpdpb2 = avg_gs_per_drug_per_bill(t2)
    # cont of num of drugs per bill
    agpb2_sim = float(ndpb1) * float(agpdpb2)
    agpc2_sim = agpb2_sim * float(nbpc2)
    gs2_sim = agpc2_sim * float(nc2)
    d['ndpb'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)
    # cont. of avg gs per drug per bill
    agpb2_sim = float(ndpb2) * float(agpdpb1)
    agpc2_sim = agpb2_sim * float(nbpc2)
    gs2_sim = agpc2_sim * float(nc2)
    d['agpdpb'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)

    # number of quantities per drug per bill
    nqpdpb1 = num_quantity_per_drug_per_bill(t1)
    nqpdpb2 = num_quantity_per_drug_per_bill(t2)
    # Avg gs per quantity
    agpq1 = rate(t1)
    agpq2 = rate(t2)
    # cont by number of quantities per drug per bill
    agpdpb2_sim = float(nqpdpb1) * float(agpq2)
    agpb2_sim = float(ndpb2) * agpdpb2_sim
    agpc2_sim = agpb2_sim * float(nbpc2)
    gs2_sim = agpc2_sim * float(nc2)
    d['nqpdpb'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)
    # cont by Avg gs per quantity
    agpdpb2_sim = float(nqpdpb2) * float(agpq1)
    agpb2_sim = float(ndpb2) * agpdpb2_sim
    agpc2_sim = agpb2_sim * float(nbpc2)
    gs2_sim = agpc2_sim * float(nc2)
    d['rate'] = metric_factor(gs2_sim, ret_per2, gs2_local, ns2_local, ns2_global)

    # returing the dictionary containing all metric values
    return d

# Function to store the metric in a dataFrame
def store_table(df, d, ret_fact, ns2_global):
    # gross sale
    # level 1
    df['Return%'] = ret_fact
    # level 2
    df['Number_cust'] = d['nc']
    df['ACV'] = d['ACV']
    # Level 3
    df['Nob_per_cust'] = d['nbpc']
    df['ABV'] = d['ABV']
    # Level 4
    df['Drugs_per_bill'] = d['ndpb']
    # df['Avg. spend per drug per bill'] = d['agpdpb']
    # Level 5
    df['Quantity_per_drug'] = d['nqpdpb']
    df['Avg_rate_per_quantity'] = d['rate']

    return df

#Function to calculate change factor of any parameter
def factor_param(d1, d2, ns1, ns2, calc_type):
    ns1_param = sale(d1)
    ns2_param = sale(d2)
    if calc_type == 'per':
        ns1_param_fact = ns1_param / ns1
        ns2_sim_param = ns2 * ns1_param_fact
    elif calc_type == 'abs':
        ns2_sim_param = ns1_param
    ch_ns2_param = ns2_param - ns2_sim_param
    ns_factor_param = (ch_ns2_param / ns2) * 100
    return ns_factor_param

# Function to control level of output columns i.e level of decomposition
def level(table, max_level, local_list):
    if max_level == 1:
        df = table.loc[:,local_list[0:2]]
        return df
    if max_level == 2:
        df = table.loc[:,local_list[0:4]]
        return df
    if max_level == 3:
        df = table.loc[:,local_list[0:6]]
        return df
    if max_level == 4:
        df = table.loc[:,local_list[0:7]]
        return df
    if max_level == 5:
        df = table.loc[:,local_list[0:9]]
        return df

#Function which returns the final table containing the metric contributions of total change of net sale
def decomposition(table1, table2, df, ns2_global):
    # period1 net sale
    ns1_local = sale(table1)
    # period2 net sale
    ns2_local = sale(table2)

    # defining gross sale metrics
    mos1_gs_local = break_sale(table1, 'gross')
    mos2_gs_local = break_sale(table2, 'gross')
    gs1_local = sale(mos1_gs_local)
    gs2_local = sale(mos2_gs_local)

    # defining return metrics
    mos1_ret_local = break_sale(table1, 'return')
    mos2_ret_local = break_sale(table2, 'return')
    ret1_local = sale(mos1_ret_local)
    ret2_local = sale(mos2_ret_local)

    # return to be calculate as return %
    ret_per1 = np.divide(ret1_local,gs1_local)
    ret_per2 = np.divide(ret2_local ,gs2_local)
    ret2_sim = ret_per1 * gs2_local
    ns2_sim = gs2_local - ret2_sim
    ret_fact = np.divide((ns2_local - ns2_sim),ns2_global) * 100

    # calling metrics
    d = metric(mos1_gs_local, mos2_gs_local, ns2_local, gs1_local, gs2_local, ret_per1, ret_per2, ns2_global)

    # final data frame
    df_final = store_table(df, d, ret_fact, ns2_global)
    return df_final

# Its like the final main function to call the decomposition function with given parameter and limit
def my_func(param, param_limit, max_level):
    # period1 net sale
    ns1 = sale(mos1)
    # period2 net sale
    ns2 = sale(mos2)
    ns2_global = ns2

    # Abs list
    abs_list = ['drug', 'composition', 'store_staff', 'store_name', 'line_manager', 'city', 'abo', 'franchisee_name',
                'cluster_name', 'old_new']
    pct_list = ['type', 'category', 'company', 'payment_method', 'promo_code', 'pr_flag', 'hd_flag', 'ecom_flag']

    # If parameters are set
    # sorting the parameter values in descending order of change of net sale from period1 to period2
    df1_sort = mos1.groupby(param)['sales'].sum().reset_index()
    df2 = pd.DataFrame()
    df2[param] = df1_sort[param]
    df3 = pd.DataFrame()
    df3['sales'] = df1_sort['sales']
    df3 = df3.applymap(lambda x: np.float(x))
    df1_sort = pd.concat([df2, df3], axis=1)
    df1_sort['fraction'] = (df1_sort['sales'] / ns1) * 100

    df2_sort = mos2.groupby(param)['sales'].sum().reset_index()
    df4 = pd.DataFrame()
    df4[param] = df2_sort[param]
    df5 = pd.DataFrame()
    df5['sales'] = df2_sort['sales']
    df5 = df5.applymap(lambda x: np.float(x))
    df2_sort = pd.concat([df4, df5], axis=1)
    df2_sort['fraction'] = (df2_sort['sales'] / ns2) * 100
    df_sort = pd.merge(df1_sort, df2_sort, on=param, how='outer')
    df_sort.fillna(0, inplace=True)
    # sales diff
    df_sort['s_diff'] = df_sort['sales_y'] - df_sort['sales_x']
    # fraction diff
    df_sort['f_diff'] = df_sort['fraction_y'] - df_sort['fraction_x']

    # sorting absolute values
    df_sort1 = df_sort[param]
    df_sort2 = df_sort[['sales_x', 'fraction_x', 'sales_y', 'fraction_y', 's_diff', 'f_diff']]
    df_sort2 = np.abs(df_sort2)
    df_sort3 = pd.concat([df_sort1, df_sort2], axis=1)
    df_sort3

    # sorting
    if param in abs_list:
        df_sort = df_sort3.sort_values('s_diff', ascending=False)
    elif param in pct_list:
        df_sort = df_sort3.sort_values('f_diff', ascending=False)

    # listing the sorted parameters
    sort_list = list(df_sort[param])

    # choosing the parameter values from set limit
    if len(sort_list) <= param_limit:
        param_list = sort_list
    else:
        param_list = sort_list[0:param_limit]

    # creating dataframe with rows as parameter values
    df_temp = pd.DataFrame()

    # Iterating through each parameter value
    for c in param_list:

        # Filtering base table based on set parameter
        p1 = mos1[mos1[param] == c]
        p2 = mos2[mos2[param] == c]

        # calculating contribution factor by calling the factor_param function
        if param in abs_list:
            ns_factor_param = factor_param(p1, p2, ns1, ns2, 'abs')

        elif param in pct_list:
            ns_factor_param = factor_param(p1, p2, ns1, ns2, 'per')

        # printing the contribution of parameters in total change of net sale
        df_op = pd.DataFrame(index=[c])
        df_op['Net sale'] = ns_factor_param

        # Calling the decomposition funtion for set parameters and level
        df2 = decomposition(p1, p2, df_op, ns2_global)
        df_final = pd.concat([df_temp, df2])
        df_temp = df_final

    # Arranging column names in a relevant way
    local_list = ['Net sale', 'Return%',
                  'Number_cust', 'ACV',
                  'Nob_per_cust', 'ABV',
                  'Drugs_per_bill',
                  'Quantity_per_drug', 'Avg_rate_per_quantity']

    # return final df
    return level(df_final, max_level, local_list)

#Function to store output for all param in the list
def all_param(param_list,param_limit, max_level ):
    df_param_dict = {}
    for param in param_list:
        df_local = my_func(param , param_limit, max_level)
        df_local['params'] = param
        df_param_dict[param] = df_local
    return df_param_dict

#Sorting param on the basis of contribution to change
def sort_param(df_param_dict):
    params = []
    cont_value = []
    for key in df_param_dict:
        params.append(key)
        cont_value.append(abs(np.abs(df_param_dict[key]['Net sale']).sum()))
    df_local = pd.DataFrame(data = {'param' :params , 'contribution':cont_value} )
    df_sorted = df_local.sort_values('contribution', ascending = False)
    sorted_param_list = list(df_sorted['param'])
    return sorted_param_list

#Concating all stores dataframe in descending order of contribution
def concat(sorted_param_list, df_param_dict):
    p = 0
    df_final = pd.DataFrame()
    for param in sorted_param_list:
        df_temp = df_param_dict[param]
        df_final = pd.concat([df_final, df_temp])
        p = p + 1
    index = list(df_final.index)
    df_final.set_index(['params', index], inplace=True)
    return df_final

#Function to filter data based on larger contribution
def filtered(df , upper_value = 0.95, lower_value= 0.05):
    uv = np.quantile(df, upper_value)
    lv = np.quantile(df, lower_value)
    df = df.applymap(lambda x: np.nan if x <= uv and x>= lv else x)
    df = df.applymap(lambda x: np.round(x,2))
    df = df.dropna(axis = 0, how ='all')
    df = df.dropna(axis = 1, how ='all')
    return df

#Defining funstion to calculate absolute changes
def difference(p, pv, metric):
    local_df1 = mos1[mos1[p] == pv]
    local_df2 = mos2[mos2[p] == pv]

    if metric == 'Net sale':
        ns_local1 = sale(local_df1)
        ns_local2 = sale(local_df2)
        abs_ch = change(ns_local1, ns_local2)

    elif metric == 'Return%':

        mos1_gs_local = break_sale(local_df1, 'gross')
        mos2_gs_local = break_sale(local_df2, 'gross')
        gs1_local = sale(mos1_gs_local)
        gs2_local = sale(mos2_gs_local)

        mos1_ret_local = break_sale(local_df1, 'return')
        mos2_ret_local = break_sale(local_df2, 'return')
        ret1_local = sale(mos1_ret_local)
        ret2_local = sale(mos2_ret_local)

        ret_per1 = np.divide(ret1_local, gs1_local) * 100
        ret_per2 = np.divide(ret2_local , gs2_local) * 100
        abs_ch = change(ret_per1, ret_per2)

    elif metric == 'Number_cust':
        nc1 = num_cust(local_df1)
        nc2 = num_cust(local_df2)
        abs_ch = change(nc1, nc2)

    elif metric == 'ACV':
        agpc1 = avg_gs_per_customer(local_df1)
        agpc2 = avg_gs_per_customer(local_df2)
        abs_ch = change(agpc1, agpc2)

    elif metric == 'Nob_per_cust':
        nbpc1 = num_bills_per_customer(local_df1)
        nbpc2 = num_bills_per_customer(local_df2)
        abs_ch = change(nbpc1, nbpc2)

    elif metric == 'ABV':
        agpb1 = avg_gs_per_bill(local_df1)
        agpb2 = avg_gs_per_bill(local_df2)
        abs_ch = change(agpb1, agpb2)

    elif metric == 'Drugs_per_bill':
        ndpb1 = num_drugs_per_bill(local_df1)
        ndpb2 = num_drugs_per_bill(local_df2)
        abs_ch = change(ndpb1, ndpb2)

    elif metric == 'Quantity_per_drug':
        nqpdpb1 = num_quantity_per_drug_per_bill(local_df1)
        nqpdpb2 = num_quantity_per_drug_per_bill(local_df2)
        abs_ch = change(nqpdpb1, nqpdpb2)

    elif metric == 'Avg_rate_per_quantity':
        agpq1 = rate(local_df1)
        agpq2 = rate(local_df2)
        abs_ch = change(agpq1, agpq2)

    return abs_ch

# Final run function
def run(param='old_new', param_limit=10, max_level=5, full_run='yes', data='summary', filter_cutoff=0.05):
    if full_run == 'no':
        param = param
        param_limit = param_limit
        max_level = max_level
        df_local = my_func(param, param_limit, max_level)
        if data == 'full':
            df_local = df_local.applymap(lambda x: np.round(x, 2))
            df_local.reset_index(inplace=True)
            df_local.rename(columns={'level_1': 'parameter value'}, inplace=True)
            return df_local
        elif data == 'summary':
            df_local = df_local.fillna(0)
            df_local = filtered(df_local, (1 - filter_cutoff), filter_cutoff)
            df_local.reset_index(inplace=True)
            df_local.rename(columns={'level_1': 'parameter value'}, inplace=True)
            return df_local

    if full_run == 'yes':
        param_limit = 5
        max_level = 5
        param_list = ['drug', 'type', 'category', 'composition', 'company', 'store_staff', 'old_new', 'payment_method',
                      'promo_code', 'pr_flag', 'hd_flag', 'ecom_flag', 'store_name', 'line_manager', 'city', 'abo',
                      'franchisee_name', 'cluster_name']
        df_param_dict = all_param(param_list, param_limit, max_level)
        sorted_param_list = sort_param(df_param_dict)
        df_required = concat(sorted_param_list, df_param_dict)
        df_pr = df_required.copy()
        if data == 'full':
            df_pr = df_pr.applymap(lambda x: np.round(x, 2))
            df_pr.reset_index(inplace=True)
            df_pr.rename(columns={'level_1': 'parameter value'}, inplace=True)
            return df_pr

        elif data == 'summary':
            # df_pr  = df_pr.applymap(lambda x: 0 if x == np.nan else x)
            df_pr = df_pr.fillna(0)
            df = filtered(df_pr, (1 - filter_cutoff), filter_cutoff)
            df.reset_index(inplace=True)
            df.rename(columns={'level_1': 'parameter value'}, inplace=True)
            return df


# Running final function to get output
df_final = run(param = 'store_name',param_limit = 10, max_level = 5, full_run = 'yes', data = 'summary',filter_cutoff = 0.05)

# percent change in net sale from p1 to p2
ns1 = sale(mos1)
ns2 = sale(mos2)
ch_ns = change(ns1,ns2)
pc_ns = np.round(per_change(ns1,ns2),2)

if full_run == 'yes':
    if manual_sorting == 'no':
        hidden_param_value = ['acute', 'store', 'cash', 'ZIPPIN PHARMA PVT. LTD', 'MAH-MUM']
        hidden_param = ['abo', 'line_manager', 'cluster_name', 'store_staff']
        df1 = df_final.iloc[:, :2]
        df2 = df_final.iloc[:, 2:]
        if ch_ns >0:
            df3 = df2.applymap(lambda x: np.nan if x < 0 else x)
            df4 = pd.concat([df1, df3], axis=1)
            df_sorted = df4.sort_values('Net sale', ascending= False)
        else:
            df3 = df2.applymap(lambda x: np.nan if x > 0 else x)
            df4 = pd.concat([df1, df3], axis=1)
            df_sorted = df4.sort_values('Net sale', ascending= True)
        df_filtered = df_sorted[~(df_sorted['parameter value'].isin(hidden_param_value))]
        df_filtered = df_filtered[~(df_filtered['params'].isin(hidden_param))]
        # dropping null rows and columns
        df_filtered = df_filtered.dropna(axis=0, how='all')
        df_filtered = df_filtered.dropna(axis=1, how='all')
        if top_parameter is not None:
            df_filtered = df_filtered.iloc[0:top_parameter, :]

    elif manual_sorting == 'yes':
        # taking the sorted parameters into a list
        param_dupl = list(df_final['params'].values)
        sort_param = []
        for p in param_dupl:
            if p not in sort_param:
                sort_param.append(p)
        # Manual sorting of parameters
        cust_list = ['old_new']
        drug_list = ['drug', 'type', 'category', 'company', 'composition']
        flag_list = ['pr_flag', 'hd_flag', 'ecom_flag']
        pay_list = ['payment_method', 'promo_code']
        area_list = ['city', 'franchisee_name', 'cluster_name']
        store_list = ['store_name']
        person_list = ['store_staff', 'abo', 'line_manager']
        # empty lists to store sorted params
        cust = []
        drug = []
        flag = []
        pay = []
        area = []
        store = []
        person = []
        # storing sorted params
        for p in sort_param:
            if p in cust_list:
                cust.append(p)
            elif p in drug_list:
                drug.append(p)
            elif p in flag_list:
                flag.append(p)
            elif p in store_list:
                store.append(p)
            elif p in pay_list:
                pay.append(p)
            elif p in area_list:
                area.append(p)
            elif p in person_list:
                person.append(p)
        # sorting by sorted param
        list_serial = [cust,flag,pay,area,store,drug,person]
        df_concat = pd.DataFrame()
        for lst in list_serial:
            for c in lst:
                df_temp = df_final[df_final['params'] == c]
                df_concat = pd.concat([df_concat, df_temp])
        df_final = df_concat
        # defining hidden parameter values
        #hidden_param = ['acute','Non-HD','Non-PR','store','cash','ZIPPIN PHARMA PVT. LTD','MAH-MUM']
        hidden_param_value = ['acute', 'store', 'cash', 'ZIPPIN PHARMA PVT. LTD', 'MAH-MUM']
        hidden_param = ['abo', 'line_manager', 'cluster_name', 'store_staff']
        # filtering out hidden parameter values
        df_filtered = df_final[~(df_final['parameter value'].isin(hidden_param_value))]
        df_filtered = df_filtered[~(df_filtered['params'].isin(hidden_param))]

        if direction == 'same':
            df1 = df_filtered.iloc[:, :2]
            df2 = df_filtered.iloc[:, 2:]
            if ch_ns > 0:
                df3 = df2.applymap(lambda x: np.nan if x < 0 else x)
                df_filtered = pd.concat([df1, df3], axis=1)
            else:
                df3 = df2.applymap(lambda x: np.nan if x > 0 else x)
                df_filtered  = pd.concat([df1, df3], axis=1)
            df_index = df_filtered.set_index(['params', 'parameter value'])
            df_filtered = df_index.dropna(axis=0, how='all')
            df_filtered = df_filtered.dropna(axis=1, how='all')
            df_filtered.reset_index(inplace=True)
        if top_parameter is not None:
            param_list = list(df_filtered['params'].values)
            sort_param_list = []
            for p in param_list:
                if p not in sort_param_list:
                    sort_param_list.append(p)
            sort_param_list = sort_param_list[0:top_parameter]
            df_filtered = df_filtered[(df_filtered['params'].isin(sort_param_list))]
            df_index = df_filtered.set_index(['params', 'parameter value'])
            df_filtered = df_index.dropna(axis=0, how='all')
            df_filtered = df_filtered.dropna(axis=1, how='all')
            df_filtered.reset_index(inplace=True)

        #dropping null rows and columns
        df_index = df_filtered.set_index(['params', 'parameter value'])
        df_filtered  = df_index.dropna(axis = 0, how ='all')
        df_filtered  = df_filtered.dropna(axis = 1, how ='all')
        df_filtered.reset_index(inplace=True)

    # Additional data
    if additional_data == 'difference' or additional_data == 'both':
        # Absolute changes
        df_diff = df_filtered.copy()
        params_list = list(df_diff['params'])
        param_value_list = list(df_diff['parameter value'])
        column_list = list(df_diff.columns)[2:]
        # Iterating through all the entries in the final dataframe
        for c in column_list:
            for (p,pv) in zip(params_list,  param_value_list):
                df_diff[c] = np.where((df_diff['params'] == p) & (df_diff['parameter value'] == pv), difference(p,pv,c), df_diff[c])

        # reverse of absolute dataframe
        df_diff.rename(columns={'parameter value':''}, inplace = True)
        df_diff_rev = df_diff.T
        df_diff_rev.to_csv('/tmp/final_output_diff.csv', index = True, header = False)

    if additional_data == 'absolute_impact' or additional_data == 'both':
        df1 = df_filtered.iloc[:, :2]
        df2 = df_filtered.iloc[:, 2:]
        df3 = df2.applymap(lambda x: round(np.divide((x * ns2),100) ,2) if x != np.nan else x)
        df_abs = pd.concat([df1, df3], axis=1)
        # reverse of absolute dataframe
        df_abs.rename(columns={'parameter value': ''}, inplace=True)
        df_abs_rev = df_abs.T
        df_abs_rev.to_csv('/tmp/final_output_abs.csv', index=True, header=False)

    # saving reverese dataframes
    df_filtered.rename(columns={'parameter value': ''}, inplace=True)
    df_rev = df_filtered.T
    df_rev.to_csv('/tmp/final_output.csv', index=True, header=False)

else:
    df_rev = df_final.T
    df_rev.to_csv('/tmp/final_output.csv', index=True, header=False)

# Formatting Excel
path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/"
if not os.path.exists(path):
    os.mkdir(path, 0o777)

file_name = "sales_decomposition.xlsx"
local_file_full_path = path + file_name

# wrting to excel
book = xlsxwriter.Workbook(local_file_full_path, {'strings_to_numbers': True})
ws = book.add_worksheet("SD")
bold = book.add_format({'bold': True})
cell_format_bg_yl = book.add_format({'bold': True})
cell_format_bg_yl.set_bg_color('yellow')
cell_format_bg_gr = book.add_format()
cell_format_bg_gr.set_bg_color('green')
cell_format_bg_rd = book.add_format()
cell_format_bg_rd.set_bg_color('red')
ws.write(0,0,"Sales Decomposition", cell_format_bg_yl)
ws.write(1, 5, "Period 1")
ws.write(2, 5, "Period 2")
ws.write(0, 6, "Start Date")
ws.write(0, 7, "End Date")
ws.write(1, 6, start_date1)
ws.write(1, 7, end_date1)
ws.write(2, 6, start_date2)
ws.write(2, 7, end_date2)
ws.write(1,8,"Net Sale1")
ws.write(1,9,ns1)
ws.write(2,8,"Net Sale2")
ws.write(2,9,ns2)
ws.write(4,5,"Net Sale Change ")
if ch_ns > 0:
    ws.write(4,6,ch_ns,cell_format_bg_gr)
elif ch_ns < 0:
    ws.write(4,6,ch_ns,cell_format_bg_rd)
ws.write(5,5,"Net Sale Ch% ")
if pc_ns > 0:
    ws.write(5,6,pc_ns,cell_format_bg_gr)
elif pc_ns < 0:
    ws.write(5,6,pc_ns,cell_format_bg_rd)
# Adding csv data to excel
# Adding csv data to excel
ws.write(7, 0, "Percentage Impact", cell_format_bg_yl)
limit2 = df_rev.shape[1] + 1
row_index = 8
with open("/tmp/final_output.csv") as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        for l in range(limit2):
            if l == 0:
                ws.write(row_index, l, row[l], bold)
            else:
                ws.write(row_index, l, row[l])
        row_index += 1

ws.conditional_format('B10:DX19', {'type': '3_color_scale'})

if additional_data == 'difference':
# adding difference data
    ws.write(20, 0, "Difference", cell_format_bg_yl)
    limit3 = df_diff_rev.shape[1] + 1
    row_index = 21
    with open("/tmp/final_output_diff.csv") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            for l in range(limit3):
                if l == 0:
                    ws.write(row_index, l, row[l], bold)
                else:
                    ws.write(row_index, l, row[l])
            row_index += 1

    ws.conditional_format('B23:DX36', {'type': '3_color_scale'})

if additional_data == 'absolute_impact':
# adding absolute change data
    ws.write(20, 0, "Absolute Impact", cell_format_bg_yl)
    limit4 = df_abs_rev.shape[1] + 1
    row_index = 21
    with open("/tmp/final_output_abs.csv") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            for l in range(limit4):
                if l == 0:
                    ws.write(row_index, l, row[l], bold)
                else:
                    ws.write(row_index, l, row[l])
            row_index += 1

    ws.conditional_format('B23:DX36', {'type': '3_color_scale'})

if additional_data == 'both':
    # adding adifference data
    ws.write(20, 0, "Difference", cell_format_bg_yl)
    limit3 = df_diff_rev.shape[1] + 1
    row_index = 21
    with open("/tmp/final_output_diff.csv") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            for l in range(limit3):
                if l == 0:
                    ws.write(row_index, l, row[l], bold)
                else:
                    ws.write(row_index, l, row[l])
            row_index += 1

    ws.conditional_format('B23:DX36', {'type': '3_color_scale'})


    # adding absolute change data
    ws.write(32, 0, "Absolute Impact", cell_format_bg_yl)
    limit4 = df_abs_rev.shape[1] + 1
    row_index = 33
    with open("/tmp/final_output_abs.csv") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            for l in range(limit4):
                if l == 0:
                    ws.write(row_index, l, row[l], bold)
                else:
                    ws.write(row_index, l, row[l])
            row_index += 1

    ws.conditional_format('B35:DX48', {'type': '3_color_scale'})

# changing width of column
if limit2 >= 12:
    limit = limit2
else:
    limit = 12
for l in range(limit):
    ws.set_column(0, l, 15)

book.close()

#uploading to s3
s3.s3_client.upload_file(
            Filename=local_file_full_path,
            Bucket=s3.bucket_name,
            Key='Stores-projects/76/sales_decomposition.xlsx'
        )
# closing the connection
rs_db.close_connection()