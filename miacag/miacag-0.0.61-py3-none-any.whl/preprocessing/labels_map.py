import argparse
import psycopg2
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from psycopg2.extras import execute_batch
from miacag.configs.config import load_config
from miacag.utils.sql_utils import update_cols, getDataFromDatabase


parser = argparse.ArgumentParser(
    description='Define data inputs for building database.')
parser.add_argument(
            '--query', type=str,
            help='query for retrieving data',
            required=True)
parser.add_argument(
            '--config', type=str,
            help='Path to the YAML config file',
            required=True)
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
    '--table_name', type=str,
    help="table_name in database")


def get_trans_dict(label_names):
    trans_names = [i + '_transformed' for i in label_names]
    trans_dict = dict(zip(label_names, trans_names))
    return trans_dict, trans_names


class labelsMap():
    def __init__(self, sql_config, labels_config=None):
        self.sql_config = sql_config
        self.labels_config = labels_config
        self.df, self.connection = getDataFromDatabase(sql_config=sql_config)

    def create_labels_config_list(self, labels_config, trans_names):
        result = [labels_config for i in range(0, len(trans_names))]
        return result

    def __call__(self):
        self.df = self.df.dropna(
            subset=self.sql_config["labels_names"],
            how='any')
        trans_dict, trans_names = get_trans_dict(
            self.sql_config["labels_names"])
        self.df[trans_names] = self.df[self.sql_config['labels_names']]

        if len(self.sql_config["labels_names"]) > 1:
            print('WARNING: not implemented with label names greater than one')
        if self.labels_config is not None:
            label_c_list = self.create_labels_config_list(
                self.labels_config, trans_names)
            replace_dict = dict(zip(trans_names, label_c_list))
            self.df = self.df.replace(replace_dict)

        update_cols(self.connection,
                    self.df.to_dict('records'),
                    self.sql_config,
                    trans_names,)
        return trans_names


if __name__ == '__main__':
    args = parser.parse_args()

    config = load_config(args.config)
    labels_config = config['labels_dict']
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
                  args.query,
                  'TestSize':
                  args.TestSize
                  }

    mapper = labelsMap(sql_config, labels_config)
    mapper()
