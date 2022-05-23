import argparse
import os
import sys

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.queries.storesmaster import storesmaster_config


def main(db, table_suffix):
    table_name = f"stores-master"
    if table_suffix:
        table_name = f"stores-master-{table_suffix}"

    db.execute(query="begin ;")

    db.execute(storesmaster_config.max_store_id.format(table_name), params=None)

    stores_intermediate: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    max_store_id = stores_intermediate.values[0][0]

    if max_store_id is None:
        max_store_id = 0

    db.execute(query=storesmaster_config.insert_stores_query.format(table_name, max_store_id))

    """ committing the transaction """
    db.execute(query=" end; ")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-ts', '--table_suffix', default="", type=str, required=False,
                        help="Table suffix for testing.")

    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env

    table_suffix = args.table_suffix
    print(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db, table_suffix=table_suffix)

    # Closing the DB Connection
    rs_db.close_connection()
