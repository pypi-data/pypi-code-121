import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "ecomm-das"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" (
                "id",
                "created-at",
                "created-by",
                "updated-at",
                "updated-by",
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
                "order-city",
                "min",
                "max",
                "safe-stock",
                "grade-updated-at",
                "zeno-drug-created-by"
                )
    select
        me."id",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        'etl-automation' as "updated-by",
        me."patient-id",
        me."promo-code-id",
        me."preferred-store-id",
        me."order-type",
        me."zeno-created-at",
        me."zeno-created-by",
        me."is-prescription-required",
        me."order-number",
        me."status",
        me."comments",
        me."zeno-drug-id",
        me."patient-store-order-id",
        me."zeno-qty",
        me."overall-min-bill-date",
        me."type",
        me."category",
        me."composition",
        me."company-id",
        me."composition-master-id",
        me."zeno-drug-name",
        me."zeno-drug-type",
        me."source-pincode",
        me."order-cancellation-reason-id",
        me."cancel-comment",
        me."cancelled-at",
        me."cancelled-by",
        me."cancel-reason",
        me."cancel-type",
        me."pso-requested-quantity",
        me."patient-request-id",
        me."pso-created-at",
        me."pso-created-by",
        me."pso-inventory-quantity",
        me."pso-status",
        me."store-id",
        me."bill-id",
        me."slot-id",
        me."turnaround-time",
        me."delivered-at",
        me."assigned-to",
        me."slot-type",
        me."per-slot-capacity",
        me."vendor-bill-number",
        me."prescription-needed",
        me."prescreptions-created",
        me."completed-at",
        me."mrp",
        me."selling-rate",
        me."gross-quantity",
        me."sale-flag",
        me."gross-revenue-value",
        me."returned-quantity",
        me."returned-revenue-value",
        me."promo-code",
        me."promo-code-type",
        me."promo-eligibility",
        me."campaign-name",
        me."store-name",
        me."store-city",
        me."store-b2b",
        me."abo",
        me."line-manager",
        me."order-origin",
        doi."min",
        doi."max",
        doi."safe-stock" as "safe-stock",
        doi."grade-updated-at" as "grade-updated-at",
        me."zeno-drug-created-by" as "zeno-drug-created-by"
    from
        "prod2-generico".ecomm me
    left join "prod2-generico"."drug-order-info" doi on
        me."store-id" = doi."store-id"
        and me."zeno-drug-id" = doi."drug-id";
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
    print(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
