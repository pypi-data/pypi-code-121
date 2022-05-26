import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "pso-slot-changes"

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
                "first-slot",
                "last-slot",
                "total-slot-changes",
                "first-slot-date",
                "last-slot-date"
                )
    select
        ps."patient-store-order-id" as "id",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        max(first_slot) as "first-slot",
        max(last_slot) as "last-slot",
        max(total_slot_changes) as "total-slot-changes",
        max(first_slot_date) as "first-slot-date",
        max(last_slot_date) as "last-slot-date"
    from
        (
        select
            "pso-id" as "patient-store-order-id",
            first_value("old-slot") over (partition by "pso-id"
        order by
            "created-at" asc rows between unbounded preceding and unbounded  following) as first_slot,
            first_value("new-slot") over (partition by "pso-id"
        order by
            "created-at" desc rows between  unbounded preceding and unbounded following) as last_slot,
            count(id) over (partition by "pso-id") as "total_slot_changes",
        first_value("old-slot-date") over (partition by "pso-id"
        order by
            "created-at" asc rows between unbounded preceding and unbounded  following) as first_slot_date,
            first_value("new-slot-date") over (partition by "pso-id"
        order by
            "created-at" desc rows between  unbounded preceding and unbounded following) as last_slot_date
        from
            "prod2-generico"."pso-slot-changes-log" pscl ) ps
    group by
        "patient-store-order-id";
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
