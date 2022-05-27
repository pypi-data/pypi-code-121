import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "drug-primary-disease"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert into
        "prod2-generico"."{table_name}" (
            "created-by",
            "created-at",
            "updated-by",
            "updated-at",
            "drug-id",
            "drug-primary-disease"
            )
    select
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta', GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta', GETDATE()) as "updated-at",
        ab."drug-id",
        ab.drug_primary_disease
    from
        (
        select
            b."drug-id",
            a.subgroup as drug_primary_disease,
            row_number () over (partition by "drug-id") as row_num
        from
            "prod2-generico".molecules a
        left join "prod2-generico".composition b on
            a.name = b.molecule
        where
            b."drug-id" is not null
        group by
            b."drug-id",
            a.subgroup) ab
    where
        ab.row_num = 1
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
