#!/usr/bin/env python3
# coding: utf-8

import sqlite3
import pandas as pd

from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.signal import signal_utility
import json
import hashlib

import pickle

from pathlib import Path
from cryptotoolbox.parallel_run import launcher_utility

from sklearn.metrics import accuracy_score


def unjsonize_mapping_dataframe(mapping_df):
    human_readable_dictionary = {}
    json_params_dictionary = {}
    for col in mapping_df.columns :
        run_json_string = signal_utility.recover_to_sql_column_format(col)
        #saving_key = signal_utility.convert_to_sql_column_format(run_json_string)
        salty = str(int(hashlib.sha1(run_json_string.encode('utf-8')).hexdigest(), 16) % (10 ** 8))
        params = json.loads(run_json_string)
        readable_label = params['signal_type'] + str(params['transaction_costs']) + str(params['normalization']) + salty
        params = json.loads(run_json_string)
        signal_name = mapping_df.iloc[0,mapping_df.columns.get_loc(col)]
        human_readable_dictionary[signal_name] = readable_label
        json_params_dictionary[signal_name] = params
    return human_readable_dictionary, json_params_dictionary

class ParallelRunResultAnalyzer():

    def __init__(self,frequence = None, underlying = None, algo = None, starting_date = None, running_date = None, drop_token='', dropbox_backup=True, local_root_directory='../data',user='napoleon',  db_path_name = None, max_table_number = 200):
        self.local_root_directory = local_root_directory
        self.user = user

        self.frequence=frequence
        self.underlying=underlying
        self.algo=algo
        self.starting_date=starting_date
        self.running_date=running_date

        self.db_path_name = db_path_name

        self.db_path = self.local_root_directory + self.db_path_name
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.max_table_number = max_table_number

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
            sqlite_select_run_query = """SELECT effective_date, """ + run + """_perf_return, """ + run + """_turn_over from parallel_run order by effective_date asc"""
            results_df = pd.read_sql_query(sqlite_select_run_query, sqliteConnection)
        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")
        return results_df

    def analyzeAllRunResults(self,jsonized_output = True ):
        results_df = self.analyzeAllRunPerfResults(jsonized_output=jsonized_output)
        signals_df = self.analyzeAllRunSignalsResults(jsonized_output=jsonized_output)
        return results_df, signals_df

    def analyzeHourlyzationResult(self, signal_name_to_analyse, path_to_close_pkl = None, jsonized_output = True, transaction_cost=True, shift = None):
        signals_df = self.analyzeAllRunSignalsResults(jsonized_output=jsonized_output)
        ohlc = pd.read_pickle(path_to_close_pkl)
        close = ohlc['close']
        signal = signals_df[signal_name_to_analyse]
        perf_df = signal_utility.daily_signal_hourlyzation(close,signal,transaction_cost=transaction_cost, shift=shift)
        results_df = perf_df[[ 'reconstituted_perf']]
        signals_df = perf_df[['signal']]
        return results_df, signals_df


    def analyzeLocalAllRunSignalsResults(self,table_number, jsonized_output = True):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            sqlite_select_run_query = """SELECT * from parallel_signal_"""+str(table_number)+""" order by effective_date asc"""
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

        #run_empty_results = results_df.sum(axis = 0)
        #self.empty_runs_to_investigate = list(run_empty_results.index[run_empty_results == 0])
        #results_df = results_df.drop(columns=self.empty_runs_to_investigate)

        if not jsonized_output :
            renaming_dictionary = {}
            for col in results_df.columns:
                if col != 'Date':
                    run_json_string=signal_utility.recover_to_sql_column_format(col)
                    try:
                        params = json.loads(run_json_string)
                    except json.decoder.JSONDecodeError as e:
                        print('trouble generating seed')
                        print(e)
                        continue
                    salty =str(int(hashlib.sha1(run_json_string.encode('utf-8')).hexdigest(), 16) % (10 ** 8))
                    if 'transaction_costs' in params.keys():
                        transacs = str(params['transaction_costs'])
                    else:
                        transacs = ''
                    if 'normalization' in params.keys():
                        normas = str(params['normalization'])
                    else:
                        normas=''
                    renaming_dictionary[col] = params['signal_type']+transacs+normas+salty

            results_df = results_df.rename(columns=renaming_dictionary, errors="raise")
        return results_df

    def analyzeAllRunSignalsResults(self,jsonized_output = True):
        results_df = None
        for table_number in range(self.max_table_number):
            local_df = self.analyzeLocalAllRunSignalsResults(table_number,jsonized_output)
            if local_df is not None:
                if results_df is None:
                    if local_df.shape[0]>0 and local_df.shape[1]>0:
                        results_df = local_df.copy()
                else:
                    if local_df.shape[0]>0 and local_df.shape[1]>0:
                        print('merging table ' + str(local_df.shape))
                        results_df = pd.merge(results_df, local_df, how='left', on=['Date'])
            else :
                break
        return results_df

    def analyzeAllRunPerfResults(self,jsonized_output = True):
        results_df = None
        for table_number in range(self.max_table_number):
            local_df = self.analyzeLocalAllRunPerfResults(table_number,jsonized_output)
            if local_df is not None:
                if results_df is None and local_df.shape[1]>0:
                    results_df = local_df.copy()
                else:
                    if local_df.shape[0]>0 and local_df.shape[1]>0:
                        print('merging table ' + str(local_df.shape))
                        results_df = pd.merge(results_df, local_df, how='left', on=['Date'])
            else :
                break
        return results_df

    def analyzeLocalAllRunPerfResults(self,table_number, jsonized_output = True):
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

        if not jsonized_output :
            renaming_dictionary = {}
            for col in results_df.columns:
                if col != 'Date':
                    run_json_string=signal_utility.recover_to_sql_column_format(col)
                    try:
                        params = json.loads(run_json_string)
                    except json.decoder.JSONDecodeError as e:
                        print('trouble generating seed')
                        print(e)
                        continue
                    #salty = hashlib.sha256(run_json_string)
                    salty =str(int(hashlib.sha1(run_json_string.encode('utf-8')).hexdigest(), 16) % (10 ** 8))
                    if 'transaction_costs' in params.keys():
                        transacs = str(params['transaction_costs'])
                    else:
                        transacs = ''
                    if 'normalization' in params.keys():
                        normas = str(params['normalization'])
                    else:
                        normas=''
                    renaming_dictionary[col] = params['signal_type']+transacs+normas+salty

            results_df = results_df.rename(columns=renaming_dictionary, errors="raise")
        return results_df




    def download_run_results(self):
        print('downloaoding from dropbox the results to '+self.db_path)
        self.dbx.local_sqlite_overwrite_from_db(sqlite_file_name=self.filename,local_root_directory = self.local_root_directory)

    def save_pickled_list_to_dropbox(self, list_to_save=None, local_root_directory= None, list_pkl_file_name = None):
        full_path = local_root_directory + list_pkl_file_name
        with open(full_path, 'wb') as f:
            pickle.dump(list_to_save, f)
        print('uploading to dropbox')
        self.dbx.upload(fullname=full_path, folder='', subfolder='', name=list_pkl_file_name,overwrite=True)

    def read_pickled_list_from_dropbox(self, list_pkl_file_name = None):
        raw_data = self.dbx.download_pkl(pkl_file_name=list_pkl_file_name)
        return raw_data


    def get_accuracy_results(self, user=None, frequence=None, ssj=None, algo=None, starting_date=None, running_date=None, db_path_suffix=None, freqly_return_pkl_filename_suffix = None, jsonized_output = True):
        db_path_name = launcher_utility.get_database_name(user,frequence,ssj,algo,starting_date,running_date,db_path_suffix)
        dates_stub = starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y')
        if freqly_return_pkl_filename_suffix is None:
            freqly_return_pkl_filename_suffix = '_' + frequence + '_returns.pkl'
        return_pkl_path = '../data_'+frequence+'/'+ssj+ '_' + dates_stub + freqly_return_pkl_filename_suffix
        print(f'getting returns associated with {db_path_name}')
        print(f'reading return from file {return_pkl_path}')
        returns_df = pd.read_pickle(return_pkl_path)
        returns_df['close_return'] = returns_df['close'].pct_change()
        print('merging signals and results')
        signals_df = self.analyzeAllRunSignalsResults(jsonized_output=jsonized_output)
        results = {}
        for me_sig in signals_df.columns:
            print(f'computing accuracy for {me_sig}')
            acc_df = pd.merge(signals_df[me_sig], returns_df['close_return'],how = 'inner', left_index=True, right_index=True)
            me_acc = accuracy_score(acc_df['close_return']>0,acc_df[me_sig]>0)
            results[me_sig] = [me_acc]
        #print(f'dictionnary results {results}')
        results_df = pd.DataFrame(results).T
        results_df.columns = ['accuracy']
        results_df = results_df.sort_values(by='accuracy', ascending=False)
        return results_df


