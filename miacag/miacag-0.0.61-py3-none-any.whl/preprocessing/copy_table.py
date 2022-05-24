import psycopg2
import argparse
from mia.preprocessing.utils.sql_utils import copy_table

parser = argparse.ArgumentParser(
    description='Define data['inputs'] for copy table')
parser.add_argument(
    '--database', type=str,
    help="database name")
parser.add_argument(
    '--username', type=str,
    help="username for database")
parser.add_argument(
    '--password', type=str,
    help="password for database")
parser.add_argument(
    '--host', type=str,
    help="host for database")
parser.add_argument(
    '--port', type=str,
    help="port for database")
parser.add_argument(
    '--table_name_input', type=str,
    help="table name in database")
parser.add_argument(
    '--table_name_output', type=str,
    help="table name in database")


if __name__ == "__main__":
    args = parser.parse_args()
    sql_config = {'database':
                  args.database,
                  'username':
                  args.username,
                  'password':
                  args.password,
                  'host':
                  args.host,
                  'port':
                  args.port,
                  'table_name_input':
                  args.table_name_input,
                  'table_name_output':
                  args.table_name_output
                  }
    copy_table(sql_config)
