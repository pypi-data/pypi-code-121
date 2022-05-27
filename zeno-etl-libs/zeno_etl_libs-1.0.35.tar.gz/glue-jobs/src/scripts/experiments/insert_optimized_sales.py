import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.queries.sales import sales_config
import pandas as pd


def main(db, table_suffix):
    table_name = f"sales"
    bill_table_name = "bill-flags"
    stores_master_table_name = "stores-master"
    if table_suffix:
        table_name = f"sales_{table_suffix}"
        bill_table_name = f"bill-flags-{table_suffix}"
        stores_master_table_name = f"stores-master-{table_suffix}"

    db.execute(query="begin ;")

    db.execute(sales_config.max_bill_id.format(table_name), params=None)

    sales_intermediate: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    max_bill_id = sales_intermediate.values[0][0]

    db.execute(sales_config.max_return_id.format(table_name), params=None)

    returns_intermediate: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    max_return_id = returns_intermediate.values[0][0]

    db.execute(sales_config.insert_sales_record.format(
        table_name, bill_table_name, stores_master_table_name, max_bill_id,
        bill_table_name, stores_master_table_name, max_return_id))

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
    table_suffix = args.table_suffix
    os.environ['env'] = env
    logger = get_logger()
    logger.info(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db, table_suffix=table_suffix)

    # Closing the DB Connection
    rs_db.close_connection()
