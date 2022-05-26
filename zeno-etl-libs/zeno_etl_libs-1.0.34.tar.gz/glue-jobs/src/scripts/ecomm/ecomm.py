import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "ecomm"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."ecomm"
    (
        "etl-created-at",
        "etl-created-by",
        "updated-at",
        "updated-by",
        "zeno-order-id",
        "patient-id",
        "promo-code-id",
        "preferred-store-id",
        "order-type",
        "zeno-created-at",
        "zeno-created-by",
        "is-prescription-required",
        "order-number",
        "status",
        "comments",
        "zeno-drug-id",
        "patient-store-order-id",
        "zeno-qty",
        "overall-min-bill-date",
        "type",
        "category",
        "composition",
        "company-id",
        "composition-master-id",
        "zeno-drug-name",
        "zeno-drug-type",
        "source-pincode",
        "order-cancellation-reason-id",
        "cancel-comment",
        "cancelled-at",
        "cancelled-by",
        "cancel-reason",
        "cancel-type",
        "pso-requested-quantity",
        "patient-request-id",
        "pso-created-at",
        "pso-created-by",
        "pso-inventory-quantity",
        "pso-status",
        "store-id",
        "bill-id",
        "slot-id",
        "turnaround-time",
        "delivered-at",
        "assigned-to",
        "slot-type",
        "per-slot-capacity",
        "vendor-bill-number",
        "prescription-needed",
        "prescreptions-created",
        "completed-at",
        "mrp",
        "selling-rate",
        "gross-quantity",
        "sale-flag",
        "gross-revenue-value",
        "returned-quantity",
        "returned-revenue-value",
        "promo-code",
        "promo-code-type",
        "promo-eligibility",
        "campaign-name",
        "store-name",
        "store-city",
        "store-b2b",
        "abo",
        "line-manager",
        "order-origin",
        "zeno-drug-created-by",
        "billed-at",
        "delivery-type",
        "order-lead")
    select
        convert_timezone('Asia/Calcutta',
        GETDATE()) as "etl-created-at",
        'etl-automation' as "etl-created-by",
        convert_timezone('Asia/Calcutta',
        GETDATE()) as "updated-at",
        'etl-automation' as "updated-by",
        zo.id as "zeno-order-id",
        zo."patient-id" as "patient-id" ,
        zo."promo-code-id" as "promo-code-id",
        zo."preferred-store-id" as "preferred-store-id",
        zo."order-type" as "order-type" ,
        zo."created-at" as "zeno-created-at",
        zo."created-by" as "zeno-created-by",
        zo."is-prescription-required" as "is-prescription-required",
        zo."order-number" as "order-number",
        zo."status",
        zo."comments",
        zos."drug-id" as "zeno-drug-id",
        pso."id" as "patient-store-order-id" ,
        zos."quantity" as "zeno-qty",
        pm."first-bill-date" as "overall-min-bill-date",
        d2."type",
        d2."category",
        d2."composition",
        d2."company-id" as "company-id",
        d2."composition-master-id" as "composition-master-id",
        d2."drug-name" as "zeno-drug-name",
        d2."type" as "zeno-drug-type",
        zpa."pincode" as "source-pincode",
        zocrm."order-cancellation-reason-id" as "order-cancellation-reason-id" ,
        zocrm."comments" as "cancel-comment",
        zocrm."created-at" as "cancelled-at",
        zocrm."created-by" as "cancelled-by",
        zer."reason-name" as "cancel-reason",
        zer."type" as "cancel-type",
        mpr."pso-requested-quantity" ,
        mpr."patient-request-id" ,
        mpr."created-at" as "pso-created-at",
        mpr."created-by" as "pso-created-by",
        mpr."pso-inventory-quantity" ,
        mpr."pso-status" ,
        mpr."store-id" ,
        mpr."bill-id",
        mhd."slot-id" ,
        mhd."turnaround-time",
        mhd."delivered-at",
        mhd."assigned-to" ,
        mhd."slot-type",
        mhd."per-slot-capacity",
        mhd."vendor-bill-number",
        mzol."prescription-needed",
        mzol."prescreptions-created",
        mzol."completed-at",
        case
            when zos."mrp" is null
            and d2."type" = 'generic' then 35
            when zos."mrp" is null
            and d2."type" != 'generic' then 100
            else zos."mrp"
        end as "mrp",
        case
            when zos."selling-rate" is null
            and d2."type" = 'generic' then 35
            when zos."selling-rate" is null
            and d2."type" != 'generic' then 100
            else zos."selling-rate"
        end as "selling-rate",
        msa."gross-quantity" ,
        case
            when msa."gross-quantity" is null then false
            else true
        end as "sale-flag",
        msa."gross-revenue-value" ,
        msa."returned-quantity" ,
        msa."returned-revenue-value",
        mp."promo-code" ,
        mp."promo-code-type" ,
        mp."promo-eligibility" ,
        mp."campaign-name" ,
        msm.store as "store-name",
        msm.city as "store-city",
        msm."store-b2b",
        msm.abo,
        msm."line-manager" ,
        zc."name" as "order-origin",
        zos."created-by" as "zeno-drug-created-by",
        msa."created-at" as "billed-at",
        mhd."delivery-type",
        zo."order-lead"
    from
        "prod2-generico"."zeno-order" as zo
    left join "prod2-generico"."zeno-order-sku" zos on
        zos."zeno-order-id" = zo."id"
    left join "prod2-generico"."patients-store-orders" pso on
        pso."zeno-order-id" = zos."zeno-order-id"
        and zos."drug-id" = pso."drug-id"
    left join "prod2-generico"."patient-requests-metadata" mpr on
        pso."id" = mpr."id"
    left join "prod2-generico"."home-delivery-metadata" mhd on
        pso."id" = mhd."id"
    left join "prod2-generico"."zeno-order-logs" mzol on
        zo."id" = mzol."id"
    left join "prod2-generico".stores s2 on
        s2."id" = pso."store-id"
    left join "prod2-generico"."zeno-patient-address" zpa on
        zo."patient-address-id" = zpa."id"
    left join "prod2-generico"."store-groups" zc on
        zc."id" = zo."store-group-id"
    left join "prod2-generico".drugs d2 on
        d2."id" = zos."drug-id"
    left join "prod2-generico"."patients-metadata" pm on
        zo."patient-id" = pm."patient-id"
    left join "prod2-generico"."zeno-order-cancellation-reason-mapping" zocrm on
        zocrm."zeno-order-id" = zo."id"
    left join "prod2-generico"."zeno-escalation-reason" zer on
        zer."id" = zocrm."order-cancellation-reason-id"
    left join "prod2-generico"."sales-agg" msa on
        NVL(pso."bill-id",
        0) = msa."bill-id"
        and pso."drug-id" = msa."drug-id"
    left join "prod2-generico"."promo" mp on
        pso."promo-id" = mp."id"
    left join "prod2-generico"."stores-master" msm on
        pso."store-id" = msm."id" ;
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

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()