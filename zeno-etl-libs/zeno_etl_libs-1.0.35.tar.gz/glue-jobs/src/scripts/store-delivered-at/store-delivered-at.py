import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "store-delivered"

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
                "store-delivered-at", 
                "needs-recompute-aggvar", 
                "num-rec"
                )
    select
        s."short-book-id" as "id",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        MAX(b."delivered-at") as "store-delivered-at",
        NULL AS "needs-recompute-aggvar",
        NULL AS "num-rec"
    from
        "prod2-generico"."short-book-invoice-items" s
    join "prod2-generico"."invoice-items" c on
        s."invoice-item-id" = c."id"
    join "prod2-generico"."invoices" b on
        c."invoice-id" = b.id
    group by
        s."short-book-id";
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
