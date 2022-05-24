#!/usr/bin/env python3
# coding: utf-8

import sqlite3
import pandas as pd

from datetime import datetime
from cryptotoolbox.file_saver import dropbox_file_saver

class ParallelRunResultAnalyzer():

    def __init__(self,drop_token='', dropbox_backup=True, local_root_directory='../data',user='cryptotoolbox',  db_path_suffix = '_run.sqlite', max_table_number=20):
        self.max_table_number = max_table_number
        self.local_root_directory = local_root_directory
        self.user = user
        self.db_path_suffix = db_path_suffix
        self.filename =  user + db_path_suffix
        self.db_path = self.local_root_directory + self.filename
        print(f'reading from dbpath {self.db_path}')
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)

    def getAllRuns(self):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            cursor = sqliteConnection.cursor()
            print("Connected to SQLite")
            sqlite_select_runs =  """PRAGMA table_info(parallel_run);"""
            cursor.execute(sqlite_select_runs)
            all_runs_tuple = cursor.fetchall()

            cursor.close()
            all_runs = [r[1] for r in all_runs_tuple if not 'date' in r[1]]
            print("Total run numbers :  ", len(all_runs))

            return all_runs
        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")

    def analyzeRunResults(self, run):
        runs = self.getAllRuns()
        results_df = None

        if run not in runs :
            return results_df

        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = """SELECT effective_date, """+run+""" from parallel_run order by effective_date asc"""
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")
        return results_df

    def analyzeAllRunResults(self):
        results_df = None
        for table_number in range(self.max_table_number):
            local_df = self.analyzeLocalAllRunResults(table_number)
            if local_df is not None:
                if results_df is None:
                    if local_df.shape[0] > 0:
                        results_df = local_df.copy()
                else:
                    if local_df.shape[0]>0:
                        print('merging table ' + str(local_df.shape))
                        results_df = pd.merge(results_df, local_df, how='left', on=['Date'])
            else :
                break
        return results_df


    def analyzeLocalAllRunResults(self, table_number):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = """SELECT * from parallel_run_"""+str(table_number)+""" order by effective_date asc"""
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except Exception as error:
            print("Failed to read data from sqlite table", error)
            return None
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")

        results_df = results_df.rename(columns={"effective_date": "Date"})
        results_df['Date'] = pd.to_datetime(results_df['Date'])
        results_df = results_df.sort_values(by=['Date'])
        results_df = results_df.set_index(results_df['Date'])
        results_df = results_df.drop(['Date'], axis=1)
        run_empty_results = results_df.sum(axis = 0)
        self.empty_runs_to_investigate = list(run_empty_results.index[run_empty_results == 0])
        results_df = results_df.drop(columns=self.empty_runs_to_investigate)
        return results_df


    def analyzeAllRunResultsSingleTable(self):
        runs = self.getAllRuns()
        if len(runs)>1:
            runs = ','.join(runs)
        else :
            runs = runs[0]

        sqliteConnection = None

        try:
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = """SELECT effective_date, """+runs+""" from parallel_run order by effective_date asc"""
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")


        results_df = results_df.rename(columns={"effective_date": "Date"})
        results_df['Date'] = pd.to_datetime(results_df['Date'])
        results_df = results_df.sort_values(by=['Date'])
        results_df = results_df.set_index(results_df['Date'])
        results_df = results_df.drop(['Date'], axis=1)


        run_empty_results = results_df.sum(axis = 0)
        self.empty_runs_to_investigate = list(run_empty_results.index[run_empty_results == 0])

        results_df = results_df.drop(columns=self.empty_runs_to_investigate)
        return results_df

    def analyzeRunWeightResult(self,run):
        sqliteConnection = None
        try:
            table_name = run + '_weight'
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = 'SELECT * from  ' + table_name
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")

        if 'index' in results_df.columns :
            results_df = results_df.rename(columns={'index':'Date'})


        if 'Date' not in results_df.columns :
            results_df['Date'] = results_df.index

        results_df['Date'] = pd.to_datetime(results_df['Date'])
        results_df = results_df.sort_values(by=['Date'])
        results_df = results_df.set_index(results_df['Date'])
        results_df = results_df.drop(['Date'], axis=1)
        return results_df

    def analyzeRunWeightPredictionResult(self,run,string_date):
        run_date = datetime.strptime(string_date, '%Y-%m-%d')

        sqliteConnection = None
        try:
            table_name = run + '_' + run_date.strftime('%d_%b_%Y') + '_weight_prediction'
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = 'SELECT * from  ' + table_name
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")
        return results_df

    def analyzeRunRecording(self,run):
        sqliteConnection = None
        try:
            table_name = run + '_recording'
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = 'SELECT * from  ' + table_name
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")
        results_df = results_df.drop(columns=['index'])
        return results_df

    def analyzeRunActivation(self,run):
        sqliteConnection = None
        try:
            table_name = run + '_activation'
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = 'SELECT * from  ' + table_name
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")
        results_df = results_df.drop(columns=['index'])
        return results_df


    def download_run_results(self):
        print('downloaoding from dropbox the results to '+self.db_path)
        self.dbx.local_sqlite_overwrite_from_db(sqlite_file_name=self.filename,local_root_directory = self.local_root_directory)

