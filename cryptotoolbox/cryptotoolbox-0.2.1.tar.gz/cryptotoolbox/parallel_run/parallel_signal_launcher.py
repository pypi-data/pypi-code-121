#!/usr/bin/env python3
# coding: utf-8

import sqlite3

from multiprocessing import Pool
from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.parallel_run import launcher_utility
import json
import math


import numpy as np
import random

import string

class SignalParalleLauncher():
    def __init__(self,starting_date = None, running_date = None, drop_token='', dropbox_backup=True, local_root_directory='../data',user='napoleon',underlying=None,frequence=None,algo=None,db_path_suffix = '_alphas.sqlite', triggers = [True], transaction_costs = [True], normalizations = [False], modulators =[1.] ,signal_idiosyncratic_paramaters=[None], table_max_size = 2000):
        self.starting_date=starting_date
        self.running_date=running_date
        self.args = []
        self.key_args = []
        self.seed = 0
        self.mapping_keys={}
        for trigger in triggers:
            for transaction_cost in transaction_costs:
                for normalization in normalizations:
                    for modulator in modulators:
                        for signal_type, params  in signal_idiosyncratic_paramaters.items():
                            for param in params:
                                rand_hash= ''.join(random.choice(string.ascii_lowercase) for i in range(4))
                                # problem due to json serialization
                                rand_hash = rand_hash.replace('cc','wc')
                                rand_hash = rand_hash.replace('dd','wd')
                                rand_hash = rand_hash.replace('qq','wq')
                                rand_hash = rand_hash.replace('aa','wa')
                                self.args.append((self,rand_hash,trigger,signal_type, json.dumps(param, sort_keys=True), transaction_cost, normalization, modulator))
                                self.key_args.append((rand_hash, trigger, signal_type, json.dumps(param, sort_keys=True),transaction_cost, normalization, modulator))

        self.key_args.sort()
        self.counter = 1
        for me_arg in self.key_args:
            saving_key, _ = self.create_saving_key(*me_arg)
            self.mapping_keys[saving_key] = self.counter
            self.counter = self.counter + 1
        self.run_number = self.counter - 1
        self.local_root_directory = local_root_directory
        self.user = user
        self.db_path_suffix = db_path_suffix
        self.filename =  launcher_utility.get_database_name(user, frequence, underlying, algo, starting_date, running_date, db_path_suffix)
        self.db_path = self.local_root_directory + self.filename
        self.runs = []
        self.totalRow = 0
        self.table_max_size=table_max_size
        self.nb_tables = math.ceil(self.run_number/self.table_max_size)

        self.instantiateTables()
        self.instantiateSignalTables()
        self.empty_runs_to_investigate = []
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)

    def create_saving_key(self,seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator):
        idios = json.loads(idios_string)
        common_params = {
            'seed': seed,
            'trigger': trigger,
            'signal_type': signal_type,
            'transaction_costs': transaction_costs,
            'normalization': normalization,
            'modulator': modulator
        }
        common_params.update(idios)
        saving_key = json.dumps(common_params, sort_keys=True)
        saving_key = signal_utility.convert_to_sql_column_format(saving_key)
        return saving_key, idios

    def launchParallelPool(self, toRun, use_num_cpu):
        with Pool(processes=use_num_cpu) as pool:
            results = pool.starmap(toRun, self.args)
            print('parallel computation done')

    def launchSequential(self, toRun):
        for meArg in self.args:
             toRun(*meArg)

    def instantiateSignalTables(self):
        for table_counter in range(self.nb_tables):
            self.instantiateSignalTable(table_counter)


    def instantiateSignalTable(self, table_counter):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            sqlite_create_table_query = '''CREATE TABLE parallel_signal_'''+str(table_counter)+'''(
                                        effective_date date PRIMARY KEY);'''
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print("SQLite table created")
            cursor.close()
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
            print('we do not recreate tables but resume the run with partially filled tables')
            print('if you want a new run, drop the table')
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")

    def instantiateTables(self):
        for table_counter in range(self.nb_tables):
            self.instantiateTable(table_counter)

    def instantiateTable(self, table_counter):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            sqlite_create_table_query = '''CREATE TABLE parallel_run_'''+str(table_counter)+'''(
                                        effective_date date PRIMARY KEY);'''
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print("SQLite table created")
            cursor.close()
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")



    def insertSignals(self, table_counter, run, values):
        sqliteConnection = None
        try:
            success = True
            sqliteConnection = sqlite3.connect(self.db_path)
            parallel_signal = 'parallel_signal_' + str(table_counter)
            cursor = sqliteConnection.cursor()
            for i, v in values.iteritems():
                sqlite_insert_query = """INSERT INTO '"""+parallel_signal+"""' ('effective_date', '""" + run + """') VALUES ('""" + str(
                    i) + """','""" + str(v) + """');"""
                cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            cursor.close()
        except Exception as error:
            print("Error while working with SQLite", error)
            print('investigate')
            success = False
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")
        return success

    def insertResults(self, table_counter, run, values):
        sqliteConnection = None
        try:
            success = True
            sqliteConnection = sqlite3.connect(self.db_path)
            parallel_run = 'parallel_run_' + str(table_counter)
            cursor = sqliteConnection.cursor()
            for i, v in values.iteritems():
                sqlite_insert_query = """INSERT INTO '"""+parallel_run+"""' ('effective_date', '""" + run + """') VALUES ('""" + str(
                    i) + """','""" + str(v) + """');"""
                cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            cursor.close()
        except Exception as error:
            print("Error while working with SQLite", error)
            print('investigate')

            success = False
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")
        return success

    def updateSignals(self, table_counter, run, values):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            cursor = sqliteConnection.cursor()
            parallel_signal = 'parallel_signal_' + str(table_counter)
            for i, v in values.iteritems():
                sqlite_update_query = """UPDATE '"""+parallel_signal+"""' set '""" + run + """' = '""" + str(
                    v) + """' where effective_date = '""" + str(i) + """'"""
                cursor.execute(sqlite_update_query)
            sqliteConnection.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)
            print('investigate')
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")

    def updateResults(self, table_counter, run, values):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            parallel_run = 'parallel_run_' + str(table_counter)
            cursor = sqliteConnection.cursor()
            for i, v in values.iteritems():
                sqlite_update_query = """UPDATE '"""+parallel_run+"""' set '""" + run + """' = '""" + str(
                    v) + """' where effective_date = '""" + str(i) + """'"""
                cursor.execute(sqlite_update_query)
            sqliteConnection.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)
            print('investigate')
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")

    def addResults(self, table_counter, run, values):
        success = self.insertResults(table_counter,run,values)
        if not success :
            self.updateResults(table_counter,run, values)

    def addSignals(self, table_counter, run, values):
        success = self.insertSignals(table_counter,run,values)
        if not success :
            self.updateSignals(table_counter,run, values)

    def addSignal(self, table_number, run):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            sqlite_create_table_query = 'alter table parallel_signal_'+str(table_number)+' add column ' + run + ' real'
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print("SQLite table created")
            cursor.close()
            self.runs.append(run)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")  # adding the column

    def addRun(self, table_number, run):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            sqlite_create_table_query = 'alter table parallel_run_'+str(table_number)+' add column ' + run + ' real'
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print("SQLite table created")
            cursor.close()
            self.runs.append(run)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")  # adding the column

    def getRunAssociatedTable(self, run):
        run_counter = self.mapping_keys[run]
        table_number = run_counter % self.nb_tables
        return table_number

    def saveAll(self,run, strat_results_df):
        table_number = self.getRunAssociatedTable(run)
        self.saveResults(table_number, run, strat_results_df['reconstituted_perf'])
        self.saveSignals(table_number, run, strat_results_df['signal'])

    def saveResults(self, table_number, run, strat_results_df):
        self.addRun(table_number,run)
        self.addResults(table_number, run, strat_results_df)

    def saveSignals(self, table_number, run, strat_results_df):
        self.addSignal(table_number, run)
        self.addSignals(table_number, run, strat_results_df)


    def checkLocalRunExistence(self, table_number, run):
        sqliteConnection = None
        runExistence=None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            sqlite_select_run_query = 'SELECT effective_date,'+run + ' FROM parallel_run_'+str(table_number)
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_select_run_query)
            sqliteConnection.commit()
            print("SQLite table created")
            cursor.close()
            runExistence = True
        except sqlite3.Error as error:
            print("The run is not present", error)
            runExistence = False
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")  # adding the column
        return runExistence

    def exhaustiveCheckRunExistence(self,run):
        for table_number in range(self.nb_tables):
            if self.checkLocalRunExistence(table_number,run):
                return True, table_number
        return False, np.nan

    def checkRunExistence(self,run):
        table_number = self.getRunAssociatedTable(run)
        return self.checkLocalRunExistence(table_number,run), table_number


    def upload_results_to_dropbox(self):
        print('uploading to dropbox the results '+self.db_path)
        self.dbx.uploadFileToDropbox(filename=self.filename,fullpath = self.db_path)
