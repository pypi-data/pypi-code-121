import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger

def main(db):
    table_name = "as-ms"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" (
        "id",
        "etl-created-by",
        "updated-by",
        "updated-at",
        "patient-id",
        "store-name",
        "drug-name",
        "as-ms",
        "created-to-invoice-days",
        "created-to-invoice-hour",
        "created-to-dispatch-days",
        "created-to-dispatch-hour",
        "created-to-delivery-days",
        "created-to-delivery-hour",
        "created-to-re-order-days",
        "created-to-re-order-hour",
        "created-to-order-days",
        "created-to-order-hour",
        "status",
        "requested-quantity",
        "quantity",
        "required-quantity",
        "inventory-at-creation",
        "inventory-at-ordering",
        "created-at",
        "year-created-at",
        "month-created-at",
        "ordered-time",
        "invoiced-at",
        "dispatched-at",
        "delivered-at",
        "completed-at",
        "re-ordered-at",
        "store-delivered-at",
        "decline-reason",
        "type",
        "store-id",
        "drug-id",
        "company",
        "company-id",
        "composition",
        "composition-master-id",
        "category",
        "schedule",
        "sub-type",
        "preferred-distributor-id",
        "preferred-distributor-name",
        "drug-grade",
        "purchase-rate",
        "ptr",
        "distributor-type",
        "recieved-distributor-id",
        "received-distributor-name",
        "forward-dc-id",
        "dc-name",
        "abo",
        "line-manager",
        "store-manager",
        "city",
        "store-b2b",
        "franchisee-short-book"
        )
    select
        a.id,
        'etl-automation' as "etl-created-by",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta', GETDATE()) as "updated-at",
        a."patient-id" as "patient-id",
        b."name" as "store-name",
        a."drug-name" as "drug-name",
        case
            when a."auto-short" = 1
            and a."created-by" = 'AUTO SHORT'
            and a."patient-id" = 4480 then
        'AS'
            when 
        a."auto-short" = 1
            and a."patient-id" != 4480 then
        'MS'
            else
        'NA'
        end as "as-ms",
        --Fulfillment on Invoice
        (case
            when (a."invoiced-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(day,
            a."created-at",
            a."invoiced-at")
        end) as "created-to-invoice-days",
        (case
            when (a."invoiced-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(hours,
            a."created-at",
            a."invoiced-at")
        end) as "created-to-invoice-hour",
        --Fulfillment on dispatch
        (case
            when (a."dispatched-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(day,
            a."created-at",
            a."dispatched-at")
        end) as "created-to-dispatch-days",
        (case
            when (a."dispatched-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(hours,
            a."created-at",
            a."dispatched-at")
        end) as "created-to-dispatch-hour",
        --Fulfillment on    delivery
        (case
            when (msda."store-delivered-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(day,
            a."created-at",
            msda."store-delivered-at")
        end) as "created-to-delivery-days",
        (case
            when (msda."store-delivered-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(hours,
            a."created-at",
            msda."store-delivered-at")
        end) as "created-to-delivery-hour",
        -- Re-order Timing --
        (case
            when (a."re-ordered-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(day,
            a."created-at",
            a."re-ordered-at")
        end) as "created-to-re-order-days",
        (case
            when (a."re-ordered-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(hours,
            a."created-at",
            a."re-ordered-at")
        end) as "created-to-re-order-hour",
        --order Timing--
        (case
            when (a."ordered-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(day,
            a."created-at",
            a."ordered-at")
        end) as "created-to-order-days",
        (case
            when (a."ordered-at" = '0101-01-01'
            or a."created-at" = '0101-01-01') then null
            else datediff(hours,
            a."created-at",
            a."ordered-at")
        end) as "created-to-order-hour",
        a."status" as "status",
        a."requested-quantity" as "requested-quantity",
        a."quantity" as "quantity",
        a."required-quantity" as "required-quantity",
        a."inventory-at-creation" as "inventory-at-creation" ,
        a."inventory-at-ordering" as "inventory-at-ordering",
        case
            when a."created-at" = '0101-01-01' then null
            else a."created-at"
        end as "created-at",
        extract(year
    from
        a."created-at") as "year-created-at",
        extract(month
    from
        a."created-at") as "month-created-at",
        case
            when a."ordered-at" = '0101-01-01' then null
            else a."ordered-at"
        end as "ordered-time",
        case
            when a."invoiced-at" = '0101-01-01' then null
            else a."invoiced-at"
        end as "invoiced-at",
        case
            when a."dispatched-at" = '0101-01-01' then null
            else a."dispatched-at"
        end as "dispatched-at",
        case
            when a."delivered-at" = '0101-01-01' then null
            else a."delivered-at"
        end as "delivered-at",
        case
            when a."completed-at" = '0101-01-01' then null
            else a."completed-at"
        end as "completed-at",
        case
            when a."re-ordered-at" = '0101-01-01' then null
            else a."re-ordered-at"
        end as "re-ordered-at",
        case
            when msda."store-delivered-at" = '0101-01-01' then null
            else msda."store-delivered-at"
        end as "store-delivered-at",
        a."decline-reason" as "decline-reason",
        c."type",
        a."store-id" as "store-id",
        a."drug-id" as "drug-id",
        c."company",
        c."company-id" as "company-id" ,
        c."composition" ,
        c."composition-master-id" as "composition-master-id" ,
        c."category" ,
        c."schedule" ,
        c."sub-type" as "sub-type" ,
        f."id" as "preferred-distributor-id",
        f."name" as "preferred-distributor-name",
        e."drug-grade" as "drug-grade",
        dp."purchase-rate" as "purchase-rate",
        dp."ptr",
        d."type" as "distributor-type",
        d."id" as "recieved-distributor-id",
        d."name" as "received-distributor-name",
        j."forward-dc-id" as "forward-dc-id",
        ss."name" as "dc-name",
        msm."abo" ,
        msm."line-manager" ,
        msm."store-manager" ,
        msm."city",
        msm."store-b2b",
        a."franchisee-short-book" as "franchisee-short-book"
    from
        "prod2-generico"."short-book-1" a
    left join "prod2-generico"."stores" b on
        b."id" = a."store-id"
    left join "prod2-generico"."drugs" c on
        c."id" = a."drug-id"
    left join (
        select
            "drug-id",
            AVG("purchase-rate") as "purchase-rate",
            AVG(ptr) as "ptr"
        from
            "prod2-generico"."inventory-1" i
        where
            "created-at" >= dateadd(day,
            -360,
            CURRENT_DATE)
        group by
            "drug-id") as dp on
        a."drug-id" = dp."drug-id"
    left join "prod2-generico"."distributors" d on
        d."id" = a."distributor-id"
    left join "prod2-generico"."drug-order-info" e on
        e."store-id" = a."store-id"
        and e."drug-id" = a."drug-id"
    left join "prod2-generico"."distributors" f on
        a."preferred-distributor" = f."id"
    left join (
        select
            *
        from
            "prod2-generico"."store-dc-mapping"
        where
            "drug-type" = 'ethical') j on
        j."store-id" = a."store-id"
    left join "prod2-generico"."stores" ss on
        ss."id" = j."forward-dc-id"
    left join "prod2-generico"."store-delivered" msda on
        a."id" = msda."id"
    left join "prod2-generico"."stores-master" msm on
        a."store-id" = msm.id
    where
        a."auto-short" = 1
        and a."status" not in ('deleted');
    """

    db.execute(query=query)

    """ committing the transaction """
    db.execute(query=" end; ")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    args, unknown = parser.parse_known_args()
    env = args.env

    os.environ['env'] = env
    logger = get_logger()

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
