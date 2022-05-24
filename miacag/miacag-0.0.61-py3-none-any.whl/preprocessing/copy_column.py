import psycopg2
import argparse
from miacag.utils.sql_utils import copyCol

parser = argparse.ArgumentParser(
    description='Define data inputs for copy table')
parser.add_argument(
    '--database', type=str,
    help="database name")
parser.add_argument(
    '--query', type=str,
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
    '--table_name', type=str,
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
                  'table_name':
                  args.table_name,
                  'query':
                  args.query
                  }
    copyCol(
        sql_config,
        ['sten_procent_3_prox_rca', 'sten_procent_2_midt_rca'],
        ['sten_procent_3_prox_rca_transformed',
         'sten_procent_2_midt_rca_transformed'])
