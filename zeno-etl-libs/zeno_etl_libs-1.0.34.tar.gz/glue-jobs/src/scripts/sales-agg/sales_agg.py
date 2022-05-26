import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "sales-agg"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" (
        "created-by",
        "created-at",
        "updated-by",
        "updated-at",
        "bill-id",
        "drug-id",
        "patient-id",
        "store-id",
        "year-created-at",
        "month-created-at",
        "net-quantity",
        "net-revenue-value",
        "gross-quantity",
        "gross-revenue-value",
        "returned-quantity",
        "returned-revenue-value",
        "created-date"
        )
    select
        'etl-automation' as "created-by",
        b."created-at" as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',
        GETDATE()) as "updated-at",
        ms."bill-id" ,
        ms."drug-id" ,
        ms."patient-id" ,
        ms."store-id" ,
        extract(year
    from
        b."created-at") as "year-created-at",
        extract(month
    from
        b."created-at") as "month-created-at",
        sum(ms."net-quantity") as "net-quantity",
        sum(ms."revenue-value") as "net-revenue-value",
        sum(case when ms."bill-flag" = 'gross' then ms."quantity" else 0 end ) as "gross_quantity",
        sum(case when ms."bill-flag" = 'gross' then ms."revenue-value" else 0 end ) as "gross_revenue_value",
        sum(case when ms."bill-flag" = 'return' then ms."quantity" else 0 end ) as "returned-quantity",
        sum(case when ms."bill-flag" = 'return' then ms."revenue-value" else 0 end ) as "returned-revenue-value",
        date(b."created-at") as "created-date"
    from
        "prod2-generico".sales ms
    inner join "prod2-generico"."bills-1" b on
        ms."bill-id" = b.id
    group by
        ms."bill-id",
        ms."drug-id" ,
        ms."patient-id" ,
        ms."store-id",
        b."created-at"
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
