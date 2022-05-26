import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "patient-requests-short-books-map"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" (
                "patient-request-id", 
                "created-by", 
                "created-at", 
                "updated-by", 
                "updated-at", 
                "short-book-id"
                )
    select
        a."patient-request-id" as "patient-request-id",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        a."short-book-id" as "short-book-id" 
    from
        (
        select
            "patient-request-id",
            "short-book-id",
            row_number() over (partition by "patient-request-id"
        order by
            sb."required-quantity" asc) as row_num
        from
            "prod2-generico"."patient-requests-short-books" prsb
        inner join "prod2-generico"."short-book-1" sb on
            prsb."short-book-id" = sb.id) a
    where
        a.row_num = 1;
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
