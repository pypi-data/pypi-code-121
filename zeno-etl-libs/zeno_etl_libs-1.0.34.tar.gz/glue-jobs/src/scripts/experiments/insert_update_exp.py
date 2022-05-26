import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB


def main(db):
    try:
        table_name = "promo"

        db.execute(query="begin ;")
        # db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)

        update_query = f"""update "prod2-generico"."{table_name}" a
                            set
                                "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
                                "promo-code" = b."promo-code" ,
                                "promo-code-type" = b."code-type",
                                "promo-eligibility" = b."type",
                                "promo-discount-type" = b."discount-type",
                                "promo-min-purchase" = b."min-purchase",
                                "campaign-id" = b."campaign-id",
                                "campaign-name" = b."campaign"
                            from (
                            select pc.id, pc."promo-code", pc."code-type", pc."type", pc."discount-type", pc."min-purchase", pc."campaign-id", c."campaign"
                            from "prod2-generico"."{table_name}" a
                            inner join "prod2-generico"."promo-codes" pc
                                on a.id = pc.id
                            left join "prod2-generico".campaigns c 
                                on pc."campaign-id" = c.id
                            where
                                pc."updated-at" > a."updated-at"
                                or
                                c."updated-at" > a."updated-at") b
                            where a.id = b.id;
                        """
        db.execute(query=update_query)

        insert_query = f"""
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
            'etl-automation' as "updated-by",
            convert_timezone('Asia/Calcutta', GETDATE()) as "updated-at" ,
            pc."promo-code" as "promo-code" ,
            pc."code-type" as "promo-code-type",
            pc."type" as "promo-eligibility",
            pc."discount-type" as "promo-discount-type",
            pc."min-purchase" as "promo-min-purchase",
            pc."campaign-id" as "campaign-id",
            c."campaign" as "campaign-name"
        from
            "prod2-generico"."promo-codes" pc
        left join "prod2-generico"."{table_name}" pr on
            pc.id = pr.id 
        left join "prod2-generico".campaigns c on
            pc."campaign-id" = c.id
        where
            pr.id IS NULL
        """
        db.execute(query=insert_query)

        """ committing the transaction """
        db.execute(query=" end; ")
    except Exception as error:
        raise error


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env

    print(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
