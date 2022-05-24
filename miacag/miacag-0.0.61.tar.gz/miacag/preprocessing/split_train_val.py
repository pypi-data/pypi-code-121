import argparse
import psycopg2
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from psycopg2.extras import execute_batch
from miacag.configs.config import load_config
from miacag.utils.sql_utils import update_cols, getDataFromDatabase


parser = argparse.ArgumentParser(
    description='Define inputs for building database.')
parser.add_argument(
            '--query', type=str,
            help='query for retrieving data',
            required=True)
parser.add_argument(
            '--config', type=str,
            help='Path to the YAML config file',
            required=True)
parser.add_argument(
    '--TestSize', type=float,
    default=0.2,
    help='Proportion of dataset used for testing')
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


class splitter():
    def __init__(self, sql_config, labels_config=None):
        self.sql_config = sql_config
        self.df, self.connection = getDataFromDatabase(sql_config=sql_config)
        self.df = self.df.dropna(subset=sql_config["labels_names"], how='any')

    def groupEntriesPrPatient(self, df):
        '''Grouping entries pr patients'''
        X = df.drop(self.sql_config['labels_names'], 1)
        y = df[self.sql_config['labels_names']]
        if self.sql_config['TestSize'] == 1:
            return None, df
        else:
            gs = GroupShuffleSplit(
                n_splits=2,
                test_size=self.sql_config['TestSize'],
                random_state=0)
            train_ix, val_ix = next(
                gs.split(X, y, groups=df['PatientID']))
            df_train = df.iloc[train_ix]
            df_val = df.iloc[val_ix]
            self.addPhase(df_train, df_val)
            return df_train, df_val

    def addPhase(self, train_df, val_df):
        train_df['phase'] = "train"
        val_df['phase'] = "val"
        val_df = val_df[['phase', 'rowid'] + self.sql_config['labels_names']]
        train_df = train_df[
            ['phase', 'rowid'] + self.sql_config['labels_names']]

        update_cols(self.connection,
                    val_df.to_dict('records'),
                    self.sql_config,
                    ['phase'] + self.sql_config['labels_names'],)
        update_cols(self.connection,
                    train_df.to_dict('records'),
                    self.sql_config,
                    ['phase'] + self.sql_config['labels_names'])

    def __call__(self):
        df = self.df[self.df['phase'] != 'test']
        self.train_df, self.val_df = self.groupEntriesPrPatient(df)



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

    spl = splitter(sql_config, labels_config)
    spl()
