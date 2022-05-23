import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "promo"

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
                "promo-code",
                "promo-code-type",
                "promo-eligibility",
                "promo-discount-type",
                "promo-min-purchase",
                "campaign-id",
                "campaign-name"
                )
    select
        pc.id ,
        pc."created-by",
        pc."created-at",
        pc."updated-by",
        pc."updated-at" ,
        pc."promo-code" as "promo-code" ,
        pc."code-type" as "promo-code-type",
        pc."type" as "promo-eligibility",
        pc."discount-type" as "promo-discount-type",
        pc."min-purchase" as "promo-min-purchase",
        pc."campaign-id" as "campaign-id",
        c."campaign" as "campaign-name"
    from
        "prod2-generico"."promo-codes" pc
    left join "prod2-generico".campaigns c on
        pc."campaign-id" = c.id
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
