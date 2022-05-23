import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db, table_suffix):
    table_name = f"sales"
    bill_table_name = "bill-flags"
    stores_master_table_name = "stores-master"
    if table_suffix:
        table_name = f"sales_{table_suffix}"
        bill_table_name = f"bill-flags-{table_suffix}"
        stores_master_table_name = f"stores-master-{table_suffix}"

    db.execute(query="begin ;")

    gross_update_query = f"""
                            update
                                "prod2-generico"."{table_name}"
                            set
                                "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
                                "drug-name" = c."drug-name",
                                "type" = c."type",
                                "category" = c."category",
                                "patient-category" = p."patient-category",
                                "p-reference" = p."reference",
                                "pr-flag" = NVL(pso2."pr-flag", false),
                                "hd-flag" = NVL(pso2."hd-flag", false),
                                "ecom-flag" = NVL(pso2."ecom-flag", false),
                                "hsncode" = c."hsncode",
                                "is-repeatable" = c."is-repeatable",
                                "store-manager" = msm."store-manager",
                                "line-manager" = msm."line-manager",
                                abo = msm.abo,
                                city = msm.city,
                                "store-b2b" = msm."store-b2b",
                                composition = c.composition,
                                company = c.company
                            from
                                "prod2-generico"."{table_name}" sales
                            join "prod2-generico"."drugs" c on
                                c."id" = sales."drug-id"
                            join "prod2-generico"."patients" p on
                                sales."patient-id" = p."id"
                            join "prod2-generico"."{bill_table_name}" as pso2 on
                                sales."bill-id" = pso2."id"
                            join "prod2-generico"."{stores_master_table_name}" as msm on
                                sales."store-id" = msm."id"
                            where
                                ( c."updated-at" > sales."updated-at"
                                or p."updated-at" > sales."updated-at"
                                or pso2."updated-at" > sales."updated-at"
                                or msm."updated-at" > sales."updated-at")
                                and sales."bill-flag" = 'gross';             
                            """
    #TODO: Optimize the bills-flag table
    db.execute(query=gross_update_query)

    return_update_query = f"""update
                                "prod2-generico"."{table_name}"
                            set
                                "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
                                "drug-name" = c."drug-name",
                                "type" = c."type",
                                "category" = c."category",
                                "patient-category" = p."patient-category",
                                "p-reference" = p."reference",
                                "pr-flag" = NVL(pso2."pr-flag", false),
                                "hd-flag" = NVL(pso2."hd-flag", false),
                                "ecom-flag" = NVL(pso2."ecom-flag", false),
                                "hsncode" = c."hsncode",
                                "is-repeatable" = c."is-repeatable",
                                "store-manager" = msm."store-manager",
                                "line-manager" = msm."line-manager",
                                abo = msm.abo,
                                city = msm.city,
                                "store-b2b" = msm."store-b2b",
                                composition = c.composition,
                                company = c.company
                            from
                                "prod2-generico"."{table_name}" sales
                            join "prod2-generico"."drugs" c on
                                c."id" = sales."drug-id"
                            join "prod2-generico"."patients" p on
                                sales."patient-id" = p."id"
                            join "prod2-generico"."{bill_table_name}" as pso2 on
                                sales."bill-id" = pso2."id"
                            join "prod2-generico"."{stores_master_table_name}" as msm on
                                sales."store-id" = msm."id"
                            where
                                ( c."updated-at" > sales."updated-at"
                                or p."updated-at" > sales."updated-at"
                                or pso2."updated-at" > sales."updated-at"
                                or msm."updated-at" > sales."updated-at")
                                and sales."bill-flag" = 'return';            
                                """

    db.execute(query=return_update_query)

    """ committing the transaction """
    db.execute(query=" end; ")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-ts', '--table_suffix', default="", type=str, required=False,
                        help="Table suffix for testing.")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    logger = get_logger()
    table_suffix = args.table_suffix
    logger.info(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db, table_suffix=table_suffix)

    # Closing the DB Connection
    rs_db.close_connection()
