import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "zeno-order-logs"

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
                "prescription-needed", 
                "prescreptions-created", 
                "completed-at",
                "pso-created-by",
                "pso-created-at",
                "follow-up-by",
                "follow-up-at",
                "follow-up-doc-by",
                "follow-up-doc-at",
                "presc-created-by",
                "presc-created-at",
                "confirm-need-presc-by",
                "confirm-need-presc-at",
                "out-del-by",
                "out-del-at"
                )
    select
        zoal."zeno-order-id" as "id",
        'etl-automation' as "created-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        count(case when zoal."target-state" = 'CONFIRM-BUT-NEED-PRESCRIPTION' then zoal.id end) as "prescription-needed",
        count(case when zoal."target-state" = 'PRESCRIPTION-CREATED' then zoal.id end) as "prescreptions-created",
        max(case when zoal."target-state" = 'DELIVERED' then zoal."created-at" end) as "completed-at",
        max(case when "target-state" = 'CREATE-PATIENT-STORE-ORDER' and r = 1 then "action-executed-by" end) as "pso-created-by",
        max(case when "target-state" = 'CREATE-PATIENT-STORE-ORDER' and r = 1 then "created-at" end) as "pso-created-at",
        max(case when "target-state" = 'FOLLOW-UP-WITHIN-TAT' and r = 1 then "action-executed-by" end) as "follow-up-by",
        max(case when "target-state" = 'FOLLOW-UP-WITHIN-TAT' and r = 1 then "created-at" end) as "follow-up-at",
        max(case when "target-state" = 'FOLLOW-UP-DOCTOR-WITHIN-TAT' and r = 1 then "action-executed-by" end) as "follow-up-doc-by",
        max(case when "target-state" = 'FOLLOW-UP-DOCTOR-WITHIN-TAT' and r = 1 then "created-at" end) as "follow-up-doc-at",
        max(case when "target-state" = 'PRESCRIPTION-CREATED' and r = 1 then "action-executed-by" end) as "presc-created-by",
        max(case when "target-state" = 'PRESCRIPTION-CREATED' and r = 1 then "created-at" end) as "presc-created-at",
        max(case when "target-state" = 'CONFIRM-BUT-NEED-PRESCRIPTION' and r = 1 then "action-executed-by" end) as "confirm-need-presc-by",
        max(case when "target-state" = 'CONFIRM-BUT-NEED-PRESCRIPTION' and r = 1 then "created-at" end) as "confirm-need-presc-at",
        max(case when "target-state" = 'OUT-FOR-DELIVERY' and r = 1 then "action-executed-by" end) as "out-del-by",
        max(case when "target-state" = 'OUT-FOR-DELIVERY' and r = 1 then "created-at" end) as "out-del-at"
    from
        (
        select
            * ,
            rank() over (partition by "zeno-order-id",
            "target-state"
        order by
            "created-at" desc ) r
        from
            "prod2-generico"."zeno-order-action-log" zoal
        where
            "action-status" = 'SUCCESS') zoal
    group by
        zoal."zeno-order-id";
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

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
