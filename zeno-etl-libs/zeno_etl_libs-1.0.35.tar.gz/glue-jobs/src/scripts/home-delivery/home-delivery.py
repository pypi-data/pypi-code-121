import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "home-delivery-metadata"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" (
            "id", 
            "created-by", 
            "created-at", 
            "updated-by", 
            "updated-at", 
            "patient-id", 
            "doctor-id", 
            "store-id", 
            "store-name", 
            "store-lat", 
            "store-lon", 
            "drug-id", 
            "drug-name", 
            "type", 
            "category", 
            "composition", 
            "composition-master-id", 
            "company", 
            "company-id", 
            "requested-quantity", 
            "inventory-quantity", 
            "order-number", 
            "bill-id", 
            "billed-at", 
            "order-source", 
            "order-type", 
            "status", 
            "order-mode", 
            "pso-created-at", 
            "year-pso-created-at", 
            "month-pso-created-at", 
            "payment-type", 
            "slot-id", 
            "turnaround-time", 
            "patient-request-id", 
            "pr-flag", 
            "abo", 
            "line-manager", 
            "store-manager", 
            "city", 
            "store-b2b", 
            "delivery-status", 
            "assigned-to", 
            "assigned-to-id", 
            "dispatcher", 
            "receiver", 
            "delivered-at", 
            "completed-at", 
            "no-of-deliveries", 
            "vendor-bill-number", 
            "first-slot", 
            "last-slot", 
            "total-slot-changes", 
            "slot-type",
            "per-slot-capacity",
            "scheduled-at",
            "zeno-order-id",
            "delivery-type",
            "first-slot-date", 
            "last-slot-date"
            ) 
    select
        pso."id" as "id",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        pso."patient-id" as "patient-id" ,
        pso."doctor-id" as "doctor-id",
        pso."store-id" as "store-id",
        s."name" as "store-name",
        s."lat" as "store-lat",
        s."lon" as "store-lon",
        pso."drug-id" as "drug-id",
        pso."drug-name" as "drug-name",
        d."type" ,
        d."category" ,
        d."composition" ,
        d."composition-master-id" as "composition-master-id",
        d."company" ,
        d."company-id" as "company-id",
        pso."requested-quantity" as "requested-quantity",
        pso."inventory-quantity" as "inventory-quantity",
        pso."order-number" as "order-number",
        pso."bill-id" as "bill-id" ,
        b."created-at" as "billed-at",
        pso."order-source" as "order-source",
        pso."order-type" as "order-type" ,
        pso."status",
        pso."order-mode" as "order-mode",
        pso."created-at" as "pso-created-at",
        extract(year
    from
        pso."created-at") as "year-pso-created-at",
        extract(month
    from
        pso."created-at") as "month-pso-created-at",
        pso."payment-type" as "payment-type",
        pso."slot-id" as "slot-id" ,
        pso."turnaround-time" as "turnaround-time" ,
        pso."patient-request-id" as "patient-request-id",
        (case
            when pso."patient-request-id" is null then false
            else true
        end) as "pr-flag",
        sm."abo",
        sm."line-manager",
        sm."store-manager",
        sm."city",
        sm."store-b2b",
        dt."delivery-status",
        dt."assigned-to",
        dt."assigned-to-id" ,
        dt."dispatcher",
        dt."receiver",
        dt."delivered-at",
        dt."completed-at",
        dt."no-of-deliveries",
        dt."vendor-bill-number",
        sc."first-slot",
        sc."last-slot",
        sc."total-slot-changes",
        ss."slot-type" as "slot-type" ,
        ss."per-slot-capacity" as "per-slot-capacity",
        dt."scheduled-at",
        pso."zeno-order-id",
        ss."type" as "delivery-type",
        sc."first-slot-date",
        sc."last-slot-date"
    from
        "prod2-generico"."patients-store-orders" pso
    left join "prod2-generico"."bills-1" b on
            b."id" = pso."bill-id"
    left join "prod2-generico"."stores" s on
            s."id" = pso."store-id"
    left join "prod2-generico".patients p2 on
            p2."id" = pso."patient-id"
    left join "prod2-generico"."drugs" d on 
            d."id" = pso."drug-id"
    left join "prod2-generico"."stores-master" sm on
        sm."id" = pso."store-id"
    left join "prod2-generico"."delivery-tracking-metadata" dt on
        pso.id = dt."id"
    left join "prod2-generico"."pso-slot-changes" sc on
        pso.id = sc."id"
    left join "prod2-generico"."store-slots" ss on
        pso."slot-id" = ss.id
    where
        pso."order-type" = 'delivery';
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
    print(f"env: {env}")
    os.environ['env'] = env

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
