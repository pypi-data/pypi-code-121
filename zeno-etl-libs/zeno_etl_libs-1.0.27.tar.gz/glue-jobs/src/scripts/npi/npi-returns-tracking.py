#!/usr/bin/env python
# coding: utf-8
# =============================================================================
# author: saurav.maskar@zeno.health
# purpose: NPI Returns End to End Tracking
# =============================================================================

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MSSql
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
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to

os.environ['env'] = env

logger = get_logger(level='INFO')

rs_db = DB()

rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

mssql = MSSql(connect_via_tunnel=False)
connection = mssql.open_connection()


s3 = S3()
start_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
today_date = start_time.strftime('%Y-%m-%d')
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# =============================================================================
# Fetching total return created as npi-salebale
# =============================================================================

redshift_returns_query = """
    select
        *
    from
        (
        select
            row_number() over(partition by ri1.id
        order by
            ri1.id) as "row",
            nci."check-id" ,
            nc."store-id" ,
            s.name as "store-name",
            s."franchisee-id" ,
            f.name as "franchise-name",
            nci."inventory-id" ,
            -- i1."batch-number" ,
            d."drug-name" ,
            -- i1.expiry ,
            i1.barcode ,
            nci."drug-id" ,
            nci.expected ,
            nci.accounted ,
            nci.scanned ,
            nd."created-at" as "npi-added-in-store-at",
            nci."created-by" as "check-created-by",
            nci."created-at" as "check-created-at",
            nc."type" as "npi-type",
            rs.name as "return-to-dc-wh",
            rtd1.id as "return-id",
            ri1.id as "return-item-id",
            rtd1."created-at" as "store-return-created-at",
            ri1."returned-quantity" as "return-qty",
            ri1.net as "net-value",
            ri1.taxable as "net-taxable",
            ri1."return-reason" as "return-reason",
            ri1.status as "return-status",
            dn1.status as "DN-status",
            dn1.serial as "dn-number",
            dn1."net-value" as "DN-Net",
            dn1."created-at" as "DN-Saved-at",
            dn1."dispatched-at" as "DN-Dispatched-at",
            dn1."received-at" as "DN-Received-AT",
            dn1."received-by" as "DN-Received-by",
            dn1."approved-at" as "dn-approved-at",
            dn1."settled-at" as "dn-settled-at",
            dn1."accounted-at" as "dn-accounted-at",
            dn1."rejected-at" as "dn-rejected-at",
            dn1."created-by" as "dn-created-by",
            dn1."approved-by" as "dn-approved-by",
            dn1."rejected-by" as "dn-rejected-by",
            dn1."settled-by" as "dn-settled-by",
            dn1."accounted-by" as "dn-accounted-by",
            rit."transfer-note-no" ,
            rit."inventory-transferred" ,
            rit."transfer-dc-id" ,
            rit."wms-transfer-id" ,
            rit."transferred-at" as "rit-transferred-at" ,
            split_part(rit."wms-transfer-id", '-', 6)as "mysql-srlno",
            case
                when ri1.status = 'saved' then 'Store Return Saved'
                when ri1.status = 'approved'
                and dn1.status is null then 'Store Return Saved'
                when ri1.status = 'approved'
                and dn1.status = 'saved' then 'Store DN Saved'
                when ri1.status = 'approved'
                and dn1.status = 'dispatched' then 'DN Dispatched'
                when ri1.status = 'approved'
                and dn1.status = 'received' then 'DN Received'
                when rit.id is not null
                and rit."transfer-dc-id" = 256 
                then 'Transferred to Expiry'
                when rit.id is not null
                and rit."transfer-dc-id" = 255
                then 'Transferred to WMS'
                when rit.id is null
                and ri1.status = 'settled'
                and dn1.status = 'settled'
                then 'Settled Without transfer'
                when rit.id is not null
                and rit."transfer-dc-id" is null
                and ri1.status = 'settled'
                and dn1.status = 'settled'
                then 'Transferred location unknown - Settled'
                when ri1.status = 'discarded' then 'Discarded'
                else 'status issue'
            end as "Comprehensive-status"
        from
            "prod2-generico"."npi-check-items" nci
        left join "prod2-generico"."npi-check" nc 
        on
            nci."check-id" = nc.id
        left join "prod2-generico"."npi-drugs" nd 
        on
            nc.id = nd."npi-check-id"
            and nci."drug-id" = nd."drug-id"
            and nc."store-id" = nd."store-id"
        left join "prod2-generico"."return-items-1" ri1 
        on
            nci."inventory-id" = ri1."inventory-id"
            -- and ri1."return-reason" = "reason-npi-saleable"
        left join "prod2-generico"."returns-to-dc-1" rtd1 
        on
            ri1."return-id" = rtd1.id
        left join "prod2-generico"."inventory-1" i1 
             on
            nci."inventory-id" = i1.id
            --       and nd."store-id" = i1."store-id" 
            --		 and rtd1."store-id" = i1."store-id" 
            --		 and ri1."inventory-id" = i1.id 
        left join "prod2-generico"."debit-note-items-1" dni1
        on
            ri1.id = dni1."item-id"
            and dni1."is-active" != 0
        left join "prod2-generico"."debit-notes-1" dn1 
        on
            dni1."debit-note-id" = dn1.id
        left join "prod2-generico"."return-item-transfers" rit on
            ri1.id = rit."return-item-id"
        left join "prod2-generico".stores s 
        on
            rtd1."store-id" = s.id
        left join "prod2-generico".drugs d 
        on
            nci."drug-id" = d.id
        left join "prod2-generico".franchisees f 
        on
            s."franchisee-id" = f.id
        left join "prod2-generico".stores rs
        on
            rtd1."dc-id" = rs.id
        left join "prod2-generico"."return-items-1" ri1ref
        on
            ri1."return-item-reference" = ri1ref.id
        where
            nci.status = 'inventory-check-completed'
            and nci."created-at" <= ri1."approved-at"
            and nc."store-id" = rtd1."store-id"
            and ri1.status not in ('deleted', 'amended')
            and (dn1.id is null
                or dn1."is-internal-debit-note" != 1)
            and ((ri1."return-reason" = 'reason-npi-saleable')
                or ((ri1."return-reason" = 'reason-npi-non-saleable')
                    and (ri1ref."return-reason" = 'reason-npi-saleable')))
            and (dn1.status is null
                or dn1.status not in ('rejected', 'transferred'))
        order by
            nc.id desc)a
    where
        a."row" = 1"""
redshift_returns = rs_db.get_df(redshift_returns_query)
logger.info("Fetched Redshift returns")
logger.info(f"redshift_returns - line items - {len(redshift_returns)}")

other_transferred = redshift_returns[redshift_returns['transfer-dc-id']!=255]

npi_transferred = redshift_returns[redshift_returns['transfer-dc-id']==255]

logger.info(f"npi_transferred - line items - {len(npi_transferred)}")

# =============================================================================
# Connecting redshift returns to wms via fifo (psrlnotrf-barcode)
# =============================================================================

wms_fifo_query = """
   SELECT
        f.Psrlno ,
        f.PsrlnoTrf ,
        f.Pbillno ,
        f.Vno ,
        f.Acno,
        f."wms-drug-id",
        f."wms-drug-name",
        f."fifo-tqty",
        f."fifo-bqty",
        f."import-status"
    from
        (
        SELECT
            COUNT(f.Psrlno) over (partition by f.Pbillno ,
            f.PsrlnoTrf
        order by
            f.Psrlno desc
               range BETWEEN UNBOUNDED PRECEDING and UNBOUNDED FOLLOWING) as "counted-match",
            f.Psrlno ,
            f.PsrlnoTrf ,
            f.Pbillno ,
            f.Vno ,
            f.Acno,
            i.Barcode as 'wms-drug-id',
            i.name as 'wms-drug-name',
            f.TQty as 'fifo-tqty',
            f.BQty as 'fifo-bqty',
            'imported' as 'import-status'
        FROM
            FIFO f
        left join Item i on
            f.Itemc = i.code
        WHERE
            f.Acno = 59353)f
    where
        f."counted-match" = 1
    """
wms_fifo = pd.read_sql(wms_fifo_query,connection)
logger.info("Fetched Fifo Returns")

npi_transferred['barcode'] = npi_transferred['barcode'].apply(pd.to_numeric, errors='ignore').astype('Int64')

wms_fifo['PsrlnoTrf']=wms_fifo['PsrlnoTrf'].apply(pd.to_numeric, errors='ignore').astype('Int64')

npi_transferred = npi_transferred.merge(wms_fifo,left_on = ['barcode','transfer-note-no'], right_on = ['PsrlnoTrf','Pbillno'],how = 'left')

npi_transferred_fifo = npi_transferred[npi_transferred['PsrlnoTrf'].notna()]
logger.info(f"npi_transferred_fifo - line items - {len(npi_transferred_fifo)}")

npi_transferred_fifo['wms-link'] = 'barcode-psrlnotrf'

npi_transferred_notfifo = npi_transferred[npi_transferred['PsrlnoTrf'].isna()]

logger.info(f"npi_transferred_not_in_fifo - line items - {len(npi_transferred_notfifo)}")

# =============================================================================
# Connecting Items which are not imported yet
# =============================================================================

wms_apsync_query = """
    SELECT
        f.Psrlno,
        f.Vno
    from
        (
        SELECT
            Psrlno ,
            Vno ,
            row_number() over (partition by asbt.Psrlno ,
            asbt.Vno
        order by
            asbt.Psrlno desc
                   ) as "row"
        FROM
            AP_SyncBrTrf asbt)F
    WHERE
        f."row"=1
    """
wms_apsync = pd.read_sql(wms_apsync_query,connection)
logger.info("Fetched AP_SyncBrTrf Returns")

wms_apsync['Vno']=wms_apsync['Vno'].apply(pd.to_numeric, errors='ignore').astype('Int64')

npi_transferred_notfifo['transfer-note-no'] = npi_transferred_notfifo['transfer-note-no'].apply(pd.to_numeric, errors='ignore').astype('Int64')

wms_apsync['Psrlno']=wms_apsync['Psrlno'].apply(pd.to_numeric, errors='ignore').astype('Int64')

npi_transferred_notfifo['barcode'] = npi_transferred_notfifo['barcode'].apply(pd.to_numeric, errors='ignore').astype('Int64')

npi_transferred_notfifo = npi_transferred_notfifo.merge(wms_apsync,left_on = ['barcode','transfer-note-no'], right_on=['Psrlno','Vno'],how = 'left',suffixes = ['','-sync'])

npi_transferred_import_pending = npi_transferred_notfifo[npi_transferred_notfifo['Psrlno-sync'].notna()]

npi_transferred_import_pending['import-status'] = 'import-pending'

npi_transferred_import_pending['wms-link'] = 'import-pending'
logger.info(f"npi_transferred_import_pending - line items - {len(npi_transferred_import_pending)}")

npi_transferred_issue = npi_transferred_notfifo[npi_transferred_notfifo['Psrlno-sync'].isna()]

logger.info(f"npi_transferred_issue - line items - {len(npi_transferred_issue)}")

# =============================================================================
# Connecting Fifi (psrlnotrf-innventory-id)
# =============================================================================

wms_fifo['Pbillno']=wms_fifo['Pbillno'].apply(pd.to_numeric, errors='ignore').astype('Int64')

npi_transferred_issue = npi_transferred_issue.merge(wms_fifo,left_on = ['inventory-id','transfer-note-no'], right_on = ['PsrlnoTrf','Pbillno'],how = 'left', suffixes =['','_inventory_match'] )

conditions = [(npi_transferred_issue['Psrlno_inventory_match'].notna())]
choices = ['inventory-psrlnotrf']
npi_transferred_issue['wms-link'] = np.select(conditions, choices)

npi_transferred_issue['Psrlno'] = npi_transferred_issue['Psrlno_inventory_match']
npi_transferred_issue['PsrlnoTrf'] = npi_transferred_issue['PsrlnoTrf_inventory_match']
npi_transferred_issue['Pbillno'] = npi_transferred_issue['Pbillno_inventory_match']
npi_transferred_issue['Vno'] = npi_transferred_issue['Vno_inventory_match']
npi_transferred_issue['Acno'] = npi_transferred_issue['Acno_inventory_match']
npi_transferred_issue['wms-drug-id'] = npi_transferred_issue['wms-drug-id_inventory_match']
npi_transferred_issue['wms-drug-name'] = npi_transferred_issue['wms-drug-name_inventory_match']
npi_transferred_issue['fifo-tqty'] = npi_transferred_issue['fifo-tqty_inventory_match']
npi_transferred_issue['fifo-bqty'] = npi_transferred_issue['fifo-bqty_inventory_match']
npi_transferred_issue['import-status'] = npi_transferred_issue['import-status_inventory_match']

del npi_transferred_issue['Psrlno_inventory_match']
del npi_transferred_issue['PsrlnoTrf_inventory_match']
del npi_transferred_issue['Pbillno_inventory_match']
del npi_transferred_issue['Vno_inventory_match']
del npi_transferred_issue['Acno_inventory_match']
del npi_transferred_issue['wms-drug-id_inventory_match']
del npi_transferred_issue['wms-drug-name_inventory_match']
del npi_transferred_issue['fifo-tqty_inventory_match']
del npi_transferred_issue['fifo-bqty_inventory_match']
del npi_transferred_issue['import-status_inventory_match']

npi_transferred_inv_match = npi_transferred_issue[npi_transferred_issue['PsrlnoTrf'].notna()]

logger.info(f"npi_transferred_inv_match - line items - {len(npi_transferred_inv_match)}")

npi_transferred_issue = npi_transferred_issue[npi_transferred_issue['PsrlnoTrf'].isna()]

logger.info(f"npi_transferred_issue - line items - {len(npi_transferred_issue)}")

# =============================================================================
# Connecting Items by transfer note and drug id (where there is single drug for entire transfer note)
# =============================================================================

npi_transferred_issue['drug-transfernote'] = npi_transferred_issue['drug-id'].astype('str') + '-' + npi_transferred_issue['transfer-note-no'].astype('str')

durg_transfernote = tuple(map(str,npi_transferred_issue['drug-transfernote'].unique()))

wms_transfer_drug_query = """
    SELECT
        f.Psrlno ,
        f.PsrlnoTrf ,
        f.Pbillno ,
        f.Vno ,
        f.Acno,
        f."wms-drug-id",
        f."wms-drug-name",
        f."fifo-tqty",
        f."fifo-bqty",
        f."import-status"
    from
        (
        SELECT
            COUNT(f.Psrlno) over (partition by f.Pbillno ,
            i.Barcode
        order by
            f.Psrlno desc
               range BETWEEN UNBOUNDED PRECEDING and UNBOUNDED FOLLOWING) as "counted-match",
            f.Psrlno ,
            f.PsrlnoTrf ,
            f.Pbillno ,
            f.Vno ,
            f.Acno,
            i.Barcode as 'wms-drug-id',
            i.name as 'wms-drug-name',
            f.TQty as 'fifo-tqty',
            f.BQty as 'fifo-bqty',
            'imported' as 'import-status'
        FROM
            FIFO f
        left join Item i on
            f.Itemc = i.code
        WHERE
            f.Acno = 59353
            and f.TQty > 0
            and concat(i.Barcode, '-', f.Pbillno) in {durg_transfernote})f
    where
        f."counted-match" = 1
    """.format(durg_transfernote=durg_transfernote)
wms_transfer_drug = pd.read_sql(wms_transfer_drug_query,connection)
logger.info("Fetched data for join based on transfer note and drug id Returns")

wms_transfer_drug['wms-drug-id'] = wms_transfer_drug['wms-drug-id'].apply(pd.to_numeric, errors='ignore').astype('Int64')

wms_transfer_drug['Pbillno'] = wms_transfer_drug['Pbillno'].apply(pd.to_numeric, errors='ignore').astype('Int64')

npi_transferred_issue = npi_transferred_issue.merge(wms_transfer_drug,left_on = ['drug-id','transfer-note-no'], right_on = ['wms-drug-id','Pbillno'], how ='left', suffixes = ['','_drug_transfernote'])

conditions = [(npi_transferred_issue['Psrlno_drug_transfernote'].notna())]
choices = ['drug-transfernote']
npi_transferred_issue['wms-link'] = np.select(conditions, choices)

npi_transferred_issue['Psrlno'] = npi_transferred_issue['Psrlno_drug_transfernote']
npi_transferred_issue['PsrlnoTrf'] = npi_transferred_issue['PsrlnoTrf_drug_transfernote']
npi_transferred_issue['Pbillno'] = npi_transferred_issue['Pbillno_drug_transfernote']
npi_transferred_issue['Vno'] = npi_transferred_issue['Vno_drug_transfernote']
npi_transferred_issue['Acno'] = npi_transferred_issue['Acno_drug_transfernote']
npi_transferred_issue['wms-drug-id'] = npi_transferred_issue['wms-drug-id_drug_transfernote']
npi_transferred_issue['wms-drug-name'] = npi_transferred_issue['wms-drug-name_drug_transfernote']
npi_transferred_issue['fifo-tqty'] = npi_transferred_issue['fifo-tqty_drug_transfernote']
npi_transferred_issue['fifo-bqty'] = npi_transferred_issue['fifo-bqty_drug_transfernote']
npi_transferred_issue['import-status'] = npi_transferred_issue['import-status_drug_transfernote']

del npi_transferred_issue['Psrlno_drug_transfernote']
del npi_transferred_issue['PsrlnoTrf_drug_transfernote']
del npi_transferred_issue['Pbillno_drug_transfernote']
del npi_transferred_issue['Vno_drug_transfernote']
del npi_transferred_issue['Acno_drug_transfernote']
del npi_transferred_issue['wms-drug-id_drug_transfernote']
del npi_transferred_issue['wms-drug-name_drug_transfernote']
del npi_transferred_issue['fifo-tqty_drug_transfernote']
del npi_transferred_issue['fifo-bqty_drug_transfernote']
del npi_transferred_issue['import-status_drug_transfernote']

npi_transferred_drug_transfer_note = npi_transferred_issue[npi_transferred_issue['Psrlno'].notna()]

logger.info(f"npi_transferred_drug_transfer_note - line items - {len(npi_transferred_drug_transfer_note)}")

npi_transferred_issue = npi_transferred_issue[npi_transferred_issue['Psrlno'].isna()]
logger.info(f"npi_transferred_issue - line items - {len(npi_transferred_issue)}")

# =============================================================================
# Connecting by salepurchase2 Vtype - BR, Pbillno - Transfernote-no, srlno - wms-transfer-id's last number
# =============================================================================

npi_transferred_issue['mysql-pbillno-srlno'] = npi_transferred_issue['transfer-note-no'].astype(str) + '-' + npi_transferred_issue['mysql-srlno'].astype(str)
sp_list = tuple(map(str,npi_transferred_issue['mysql-pbillno-srlno'].unique()))

salepurchase2_query = """
    SELECT
        f.Psrlno ,
        f.PsrlnoTrf ,
        f.Pbillno ,
        f.Vno ,
        f.Acno,
        f."wms-drug-id",
        f."wms-drug-name",
        f."fifo-tqty",
        f."fifo-bqty",
        f."import-status",
        f."wms-srlno"
    from
        (
        SELECT
            sp.Psrlno ,
            f.PsrlnoTrf,
            sp.Pbillno ,
            f.Vno ,
            f.Acno ,
            i.Barcode as 'wms-drug-id',
            i.name as 'wms-drug-name',
            f.TQty as 'fifo-tqty',
            f.BQty as 'fifo-bqty',
            'imported' as 'import-status',
            sp.srlno as 'wms-srlno',
            COUNT(sp.Psrlno) over (partition by sp.Pbillno ,
        sp.srlno
    order by
        sp.Psrlno desc
                   range BETWEEN UNBOUNDED PRECEDING and UNBOUNDED FOLLOWING) as "counted-match"
    FROM
        SalePurchase2 sp
    left join Item i on
        sp.Itemc = i.code
    left join FIFO f on
        f.Psrlno = sp.Psrlno
    WHERE
        sp.Vtype = 'BR'
        --	and sp.Pbillno = transfer_note
        --	and i.Barcode  = drug_id
        --	and sp.srlno = transfer_end_number
        --	and f.PsrlnoTrf = barcode
        and CONCAT(sp.Pbillno, '-', sp.srlno) in {list_sp}) f
    WHERE
        f."counted-match" = 1
    """.format(list_sp=sp_list)
salepurchase2 = pd.read_sql(salepurchase2_query ,connection)
logger.info("Fetched Salepurchase2 data with Vtype 'BR")

salepurchase2['Pbillno'] = salepurchase2['Pbillno'].apply(pd.to_numeric, errors='ignore').astype('Int64')
salepurchase2['wms-srlno'] = salepurchase2['wms-srlno'].astype(str)
npi_transferred_issue['drug-id'] = npi_transferred_issue['drug-id'].astype(str)

npi_transferred_issue = npi_transferred_issue.merge(salepurchase2,left_on = ['transfer-note-no','drug-id','mysql-srlno'], right_on = ['Pbillno','wms-drug-id','wms-srlno'], how='left', suffixes =['','-sp2'])

npi_transferred_issue['drug-id'] = npi_transferred_issue['drug-id'].astype(int)

conditions = [(npi_transferred_issue['Psrlno-sp2'].notna())]
choices = ['sp2-pbillno-srlno']
npi_transferred_issue['wms-link'] = np.select(conditions, choices)

npi_transferred_issue['Psrlno'] = npi_transferred_issue['Psrlno-sp2']
npi_transferred_issue['PsrlnoTrf'] = npi_transferred_issue['PsrlnoTrf-sp2']
npi_transferred_issue['Pbillno'] = npi_transferred_issue['Pbillno-sp2']
npi_transferred_issue['Vno'] = npi_transferred_issue['Vno-sp2']
npi_transferred_issue['Acno'] = npi_transferred_issue['Acno-sp2']
npi_transferred_issue['wms-drug-id'] = npi_transferred_issue['wms-drug-id-sp2']
npi_transferred_issue['wms-drug-name'] = npi_transferred_issue['wms-drug-name-sp2']
npi_transferred_issue['fifo-tqty'] = npi_transferred_issue['fifo-tqty-sp2']
npi_transferred_issue['fifo-bqty'] = npi_transferred_issue['fifo-bqty-sp2']
npi_transferred_issue['import-status'] = npi_transferred_issue['import-status-sp2']

del npi_transferred_issue['Psrlno-sp2']
del npi_transferred_issue['PsrlnoTrf-sp2']
del npi_transferred_issue['Pbillno-sp2']
del npi_transferred_issue['Vno-sp2']
del npi_transferred_issue['Acno-sp2']
del npi_transferred_issue['wms-drug-id-sp2']
del npi_transferred_issue['wms-drug-name-sp2']
del npi_transferred_issue['fifo-tqty-sp2']
del npi_transferred_issue['fifo-bqty-sp2']
del npi_transferred_issue['import-status-sp2']

del npi_transferred_issue['mysql-pbillno-srlno']
del npi_transferred_issue['wms-srlno']

npi_transferred_sp2 = npi_transferred_issue[npi_transferred_issue['Psrlno'].notna()]

logger.info(f"npi_transferred_sp2 - line items - {len(npi_transferred_sp2)}")

npi_transferred_issue = npi_transferred_issue[npi_transferred_issue['Psrlno'].isna()]
logger.info(f"npi_transferred_issue - line items - {len(npi_transferred_issue)}")

# =============================================================================
# Collating total npi wms transferred returns
# =============================================================================

conditions = [(npi_transferred_issue['Psrlno'].isna())]
choices = ['link-issue']
npi_transferred_issue['wms-link'] = np.select(conditions, choices)

npi_returns = pd.concat([npi_transferred_fifo ,npi_transferred_import_pending, npi_transferred_inv_match, npi_transferred_drug_transfer_note, npi_transferred_sp2,npi_transferred_issue])

logger.info(f"npi_returns - Total line items - {len(npi_returns)}")

logger.info(f"percentage-issue (return-item-wise)- {round((len(npi_transferred_issue)/len(npi_returns))*100,2)}%")
# =============================================================================
# Adding liquidation data
# =============================================================================

psrlno = tuple(map(int,npi_returns[npi_returns['Psrlno'].notna()]['Psrlno'].unique()))

liquidation_query = """
    SELECT
        sp.Psrlno ,
        sum(sp.Qty) as 'liquidated-quantity'
    FROM
        SalePurchase2 sp
    left join fifo f on
        sp.Psrlno = f.Psrlno
    WHERE
        f.Acno = 59353
        and sp.Vtype = 'SB'
    GROUP by sp.Psrlno 
  """
liquidation = pd.read_sql(liquidation_query,connection)
logger.info("Fetched liquidation data")

npi_returns = npi_returns.merge(liquidation,on ='Psrlno', how = 'left' )

# =============================================================================
# Adding Purchase Expiry data
# =============================================================================

pe_query = """
   SELECT
        sum(sppe.Qty) as 'purchase-expiry',
        spge.Psrlno
    FROM
        SalePurchase2 sppe
    left join BrExp be on
        sppe.ChlnSrlno = be.BeSrlno
    left join SalePurchase2 spge on
        spge.Vtype = 'GE'
        and spge.Vno = be.Vno
        and be.Itemc = spge.Itemc
        and spge.ScmPer = be.BeSrlno
    left join FIFO f on
        spge.Psrlno = f.Psrlno
    WHERE
        sppe.Vtype = 'PE'
        and sppe.Acno = 59353
        and f.TQty != 0
    GROUP by spge.Psrlno 
  """.format(psrlno=psrlno)
purchase_expiry = pd.read_sql(pe_query,connection)
logger.info("Fetched purchase_expiry data")

npi_returns = npi_returns.merge(purchase_expiry,on ='Psrlno', how = 'left' )

if len(npi_returns)==len(npi_transferred):
    logger.info('wms-transferred-line-matched')
else:
    logger.info('issue-wms-transferred-line-match')

# =============================================================================
# Collating and creating table for upload
# =============================================================================

return_npi_saleable = pd.concat([other_transferred,npi_returns])

logger.info(f"return_npi_saleable - Total line items - {len(return_npi_saleable)}")

return_npi_saleable.columns = return_npi_saleable.columns.str.lower()

return_npi_saleable[['acno','vno','fifo-bqty','fifo-tqty','inventory-transferred','liquidated-quantity','purchase-expiry','transfer-dc-id','store-id','psrlno','psrlnotrf']] = return_npi_saleable[['acno','vno','fifo-bqty','fifo-tqty','inventory-transferred','liquidated-quantity','purchase-expiry','transfer-dc-id','store-id','psrlno','psrlnotrf']].apply(pd.to_numeric, errors='ignore').astype('Int64')
return_npi_saleable[['dn-net','net-taxable','net-value']] = return_npi_saleable[['dn-net','net-taxable','net-value']].astype(float)
# =============================================================================
# Writing table to RS
# =============================================================================

schema = 'prod2-generico'
table_name = 'npi-returns-tracking'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

status1 = False
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' delete
                        from "{schema}"."{table_name}" 
                        '''
    rs_db_write.execute(truncate_query)
    logger.info(str(table_name) + ' table old data deleted')

    s3.write_df_to_db(df=return_npi_saleable[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table uploaded')
    status1 = True

# =============================================================================
# Sending Email
# =============================================================================

if status1 is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name} table updated",
                      mail_body=f"{table_name} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

rs_db.close_connection()
rs_db_write.close_connection()
mssql.close_connection()