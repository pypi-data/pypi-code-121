import argparse
import sys

sys.path.append('../../../..')

import os
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "composition-activation"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
        insert	into
        "prod2-generico"."{table_name}" (
        "created-by",
        "created-at",
        "updated-by",
        "updated-at",
        "store-id",
        "composition-master-id",
        "system-first-inv-date",
        "system-first-bill-date",
        "store-first-inv-date",
        "store-first-bill-date")
    select
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',
        GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',
        GETDATE()) as "updated-at",
        b."store-id" as "store-id",
        d."composition-master-id" as "composition-master-id",
        max(y.system_first_inv_date) as "system-first-inv-date",
        max(y.system_first_bill_date) as "system-first-bill-date",
        MIN(c."created-at") as "store-first-inv-date",
        MIN(b."created-at") as "store-first-bill-date"
    from
        "prod2-generico"."inventory-1" c
    left join "prod2-generico"."bill-items-1" a on
        c."id" = a."inventory-id"
    left join "prod2-generico"."bills-1" b on
        b."id" = a."bill-id"
    left join "prod2-generico"."drugs" d on
        d."id" = c."drug-id"
    left join (
        select
            d."composition-master-id", MIN(b."created-at") as "system_first_bill_date", MIN(c."created-at") as "system_first_inv_date"
        from
            "prod2-generico"."inventory-1" c
        left join "prod2-generico"."bill-items-1" a on
            c."id" = a."inventory-id"
        left join "prod2-generico"."bills-1" b on
            b."id" = a."bill-id"
        left join "prod2-generico"."drugs" d on
            d."id" = c."drug-id"
        where
            d."composition-master-id" is not null
            and d."company-id" = 6984
        group by
            d."composition-master-id" ) as y on
        d."composition-master-id" = y."composition-master-id"
    where
        d."composition-master-id" is not null
        and d."company-id" = 6984
    group by
        b."store-id",
        d."composition-master-id"
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
