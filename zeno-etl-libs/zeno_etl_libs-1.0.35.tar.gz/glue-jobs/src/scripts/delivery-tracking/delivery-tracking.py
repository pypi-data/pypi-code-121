import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "delivery-tracking-metadata"

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
                "delivery-status", 
                "assigned-to", 
                "assigned-to-id", 
                "dispatcher", 
                "receiver", 
                "delivered-at", 
                "completed-at", 
                "vendor-bill-number", 
                "no-of-deliveries",
                "scheduled-at"
                )
    select
        "patient-store-order-id" as "id",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        "delivery-status" as "delivery-status" ,
        "assigned-to"  as "assigned-to",
        "assigned-to-id"  as "assigned-to_id",
        "dispatcher" ,
        "receiver" ,
        "delivered-at" as "delivered-at" ,
        "completed-at" as "completed-at",
        "vendor-bill-number" as "vendor-bill-number",
        "no-of-deliveries",
        "scheduled-at"
    from
        (
        select
            "patient-store-order-id",
            "delivery-status" ,
            "assigned-to" ,
            "assigned-to-id" ,
            "dispatcher" ,
            "vendor-bill-number",
            "receiver" ,
            "delivered-at" ,
            "completed-at",
            row_number () over (partition by "patient-store-order-id"
        order by
            "delivered-at" desc) as row_num,
            dense_rank () over (partition by "patient-store-order-id"
        order by
            "delivered-at" ) as "no-of-deliveries",
            dt."schedule-at" as "scheduled-at"
        from
            "prod2-generico"."delivery-tracking" dt
        inner join "prod2-generico"."patients-store-orders" pso on
            pso.id = dt."patient-store-order-id"
        where
            pso."bill-id" is not null
            and pso."order-type" = 'delivery') d1
    where
        d1.row_num = 1;
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
