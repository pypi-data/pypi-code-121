import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "patient-requests-metadata"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" (
                "id" ,
                "created-at", 
                "created-by", 
                "updated-by", 
                "updated-at", 
                "year-created-at", 
                "month-created-at", 
                "patient-id", 
                "doctor-id", 
                "store-id", 
                "bill-id", 
                "drug-id", 
                "zeno-order-id", 
                "drug-name", 
                "pso-requested-quantity", 
                "pso-inventory-quantity", 
                "order-number", 
                "order-source", 
                "order-type", 
                "patient-request-id", 
                "payment-type", 
                "promo-id", 
                "pso-status", 
                "fulfilled-to-consumer", 
                "type", 
                "category", 
                "company", 
                "company-id", 
                "composition", 
                "composition-master-id", 
                "lp-fulfilled-qty", 
                "sb-id" , 
                "ff-distributor", 
                "ordered-distributor-id", 
                "quantity", 
                "required-quantity", 
                "ordered-at", 
                "completed-at", 
                "invoiced-at", 
                "dispatched-at", 
                "received-at", 
                "sb-status", 
                "decline-reason", 
                "inventory-at-ordering", 
                "re-ordered-at", 
                "dc-ff-time", 
                "store-received-ff-time", 
                "consumer-ff-time", 
                "order-raised-at-dc", 
                "order-raised-at-distributor", 
                "billed-at", 
                "store-name", 
                "store-manager", 
                "line-manager", 
                "abo", 
                "city", 
                "store-b2b", 
                "substituted", 
                "gross-quantity", 
                "gross-revenue-value",
                "net-quantity", 
                "net-revenue-value", 
                "selling-rate", 
                "store-delivered-at",
                "franchisee-short-book",
                "pr-created-at",
                "sb-created-at",
                "acquired" ,
                "old-new-static" ,
                "completion-type"
                )
    select
        pso."id" as "id",
        pso."created-at" as "created-at",
        pso."created-by" as "created-by",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        extract(year from pso."created-at") as "year-created-at",
        extract(month from pso."created-at") as "month-created-at",
        pso."patient-id" as "patient-id" ,
        pso."doctor-id" as "doctor-id" ,
        pso."store-id" as "store-id" ,
        pso."bill-id" as "bill-id" ,
        pso."drug-id" as "drug-id",
        pso."zeno-order-id" as "zeno-order-id",
        pso."drug-name" as "drug-name" ,
        pso."requested-quantity" as "pso-requested-quantity",
        pso."inventory-quantity" as "pso-inventory-quantity",
        pso."order-number" as "order-number" ,
        pso."order-source" as "order-source" ,
        pso."order-type" as "order-type" ,
        pso."patient-request-id" as "patient-request-id" ,
        pso."payment-type" as "payment-type" ,
        pso."promo-id" as "promo-id",
        pso.status as "pso-status",
        (case
            when ms."gross-quantity" > 0 then 1
            else 0
        end) as "fulfilled-to-consumer",
        d2."type" ,
        d2."category" ,
        d2."company" ,
        d2."company-id" as "company-id" ,
        d2."composition" ,
        d2."composition-master-id" as "composition-master-id",
        NVL(prlp."lp-fulfilled-qty", 0) as "lp-fulfilled-qty",
        sb."id" as "sb-id",
        sb."distributor-id" as "ff-distributor",
        sb."ordered-distributor-id" as "ordered-distributor-id",
        sb."quantity" as "quantity" ,
        sb."required-quantity" as "required-quantity" ,
        case
            when sb."ordered-at" = '0101-01-01' then null
            else sb."ordered-at"
        end as "ordered-at",
        case
            when sb."completed-at" = '0101-01-01' then null
            else sb."completed-at"
        end as "completed-at",
        case
            when sb."invoiced-at" = '0101-01-01' then null
            else sb."invoiced-at"
        end as "invoiced-at",
        case
            when sb."dispatched-at" = '0101-01-01' then null
            else sb."dispatched-at"
        end as "dispatched-at",
        case
            when sb."received-at" = '0101-01-01' then null
            else sb."received-at"
        end as "received-at",
        sb."status" as "sb-status",
        sb."decline-reason" as "decline-reason",
        sb."inventory-at-ordering" as "inventory-at-ordering" ,
        case
            when sb."re-ordered-at" = '0101-01-01' then null
            else sb."re-ordered-at"
        end as "re-ordered-at",
        (case
            when (pso."created-at" = '0101-01-01'
            or msda."store-delivered-at" = '0101-01-01') then null
            else datediff(hour,
            pso."created-at",
            msda."store-delivered-at")
        end) as "dc-ff-time",
        (case
            when (pso."created-at" = '0101-01-01'
            or sb."received-at" = '0101-01-01') then null
            else datediff(hour,
            pso."created-at",
            sb."received-at")
        end) as "store-received-ff-time",
        (case
            when (pso."created-at" = '0101-01-01'
            or b2."created-at" = '0101-01-01') then null
            else datediff(hour,
            pso."created-at",
            b2."created-at")
        end) as "consumer-ff-time",
        (case
            when sb."quantity">0 then 1
            else 0
        end) as "order-raised-at-dc",
        (case
            when ("ordered-at" = '0101-01-01' or "ordered-at" is null) then 0
            else 1
        end) as "order-raised-at-distributor",
        b2."created-at" as "billed-at",
        msm."store" as "store-name",
        msm."store-manager",
        msm."line-manager",
        msm."abo",
        msm."city",
        msm."store-b2b",
        case
            when "generic-flag" is null then 'not-available'
            when "generic-flag" is not null
            and d2."type" = 'generic' then 'substituted'
            when "generic-flag" is not null
            and d2."type" != 'generic' then 'not-substituted'
            else 'not-available'
        end as "substituted",
        ms."gross-quantity",
        ms."gross-revenue-value",
        ms."net-quantity",
        ms."net-revenue-value",
        case
            when (pso."selling-rate" is null
            or pso."selling-rate" =0)
            and d2."type" = 'generic' then 35
            when (pso."selling-rate" is null
            or pso."selling-rate" =0)
            and d2."type" != 'generic' then 100
            else pso."selling-rate"
        end as "selling-rate",
        msda."store-delivered-at",
        sb."franchisee-short-book" as "franchisee-short-book",
        pra."created-at" as "pr-created-at",
        sb."created-at" as "sb-created-at" ,
        msm."acquired" ,
        msm."old-new-static" ,
        pra."completion-type"
    from
            "prod2-generico"."patients-store-orders" pso
    left join 
        (
        select
                    prlp."patient-request-id" ,
                    sum("fulfilled-quantity") as "lp-fulfilled-qty"
        from
                    "prod2-generico"."patient-request-local-purchase" prlp
        inner join 
                "prod2-generico"."patients-store-orders" pso on
                    NVL(pso."patient-request-id", 0) = prlp."patient-request-id"
        group by
                    prlp."patient-request-id" ) as prlp on
                prlp."patient-request-id" = NVL(pso."patient-request-id", 0)
    left join "prod2-generico"."patient-requests"  pra on 
                pra."id"=NVL(pso."patient-request-id",0)
    left join "prod2-generico"."patient-requests-short-books-map" mprsb on
        NVL(pso."patient-request-id", 0) = mprsb."patient-request-id"
    left join "prod2-generico"."short-book-1" sb on
        sb.id = mprsb."short-book-id"
    left join "prod2-generico"."store-delivered" msda on
        mprsb."short-book-id" = msda."id"
    left join "prod2-generico"."bills-1" b2 on
        b2.id = NVL(pso."bill-id", 0)
    left join "prod2-generico"."drugs" d2 on
        d2."id" = pso."drug-id"
    left join "prod2-generico"."substitutable-compositions" msc on
        msc."id" = d2."composition-master-id"
    left join "prod2-generico"."sales-agg" ms on
        ms."bill-id" = pso."bill-id"
        and ms."drug-id" = pso."drug-id"
    left join "prod2-generico"."stores-master" msm on
        pso."store-id" = msm.id;
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
    logger.info(f"env: {env}")
    logger.info("running job for patient request")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
