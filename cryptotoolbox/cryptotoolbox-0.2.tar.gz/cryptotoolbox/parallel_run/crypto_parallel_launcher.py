#!/usr/bin/env python3
# coding: utf-8

import sqlite3

from multiprocessing import Pool
from cryptotoolbox.file_saver import dropbox_file_saver
import math
import numpy as np
import json

from cryptotoolbox.signal import signal_utility

class CryptoParalleLauncher():
    def __init__(self,drop_token='', dropbox_backup=True, local_root_directory='../data',user='napoleon',  db_path_suffix = '_run.sqlite', low_bounds=[0.], up_bounds=[1.], ss=[10], ns=[21], leverages =[1.], signal_idiosyncratic_paramaters = [None]):

        self.table_max_size = 2000
        self.args = []
        self.key_args = []
        self.mapping_keys = {}

        self.seed = 0
        for s in ss:
            for n in ns:
                for low_bound in low_bounds:
                    for up_bound in up_bounds:
                        for leverage in leverages:
                            for signal_type, params  in signal_idiosyncratic_paramaters.items():
                                for param in params:
                                    self.args.append((self, self.seed, n, s, low_bound, up_bound, leverage, signal_type,json.dumps(param, sort_keys=True)))
                                    self.key_args.append((self.seed, n, s, low_bound, up_bound, leverage, signal_type,json.dumps(param, sort_keys=True)))
        self.key_args.sort()
        self.counter = 1
        for me_arg in self.key_args:
            saving_key, _ = self.create_saving_key(*me_arg)
            self.mapping_keys[saving_key] = self.counter
            self.counter = self.counter + 1
        self.run_number = self.counter - 1
        print('total number run to execute '+str(self.run_number))
        self.nb_tables = math.ceil(self.run_number/self.table_max_size)
        self.local_root_directory = local_root_directory
        self.user = user
        self.db_path_suffix = db_path_suffix
        self.filename =  user + db_path_suffix
        self.db_path = self.local_root_directory + self.filename
        self.runs = []
        self.totalRow = 0
        self.instantiateTables()
        self.empty_runs_to_investigate = []
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)

    def create_saving_key(self, seed, n, s, low_bound, up_bound, leverage, signal_type, idios_string):
        idios = json.loads(idios_string)
        common_params ={
            'seed':seed,
            'n':n,
            's':s,
            'low_bound': low_bound,
            'up_bound': up_bound,
            'leverage':leverage,
            'signal_type' : signal_type,
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
        results=[]
        for meArg in self.args:
            predicted_weights = toRun(*meArg)
            results.append(predicted_weights)
        return results

    def instantiateTables(self):
        for table_counter in range(self.nb_tables):
            print('instantiating table number '+str(table_counter))
            self.instantiateTable(table_counter)

    def instantiateTable(self, table_number):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            sqlite_create_table_query = 'CREATE TABLE parallel_run_'+str(table_number)+' (effective_date date PRIMARY KEY);'
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

    def insertResults(self, table_number, run, values):
        sqliteConnection = None
        try:
            success = True
            sqliteConnection = sqlite3.connect(self.db_path)
            cursor = sqliteConnection.cursor()
            for i, v in values.iteritems():
                sqlite_insert_query = """INSERT INTO 'parallel_run_""" +str(table_number) + """' ('effective_date', '""" + run + """') VALUES ('""" + str(
                    i) + """','""" + str(v) + """');"""
                cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)
            success = False
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")
        return success

    def updateResults(self, table_number, run, values):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path)
            cursor = sqliteConnection.cursor()
            for i, v in values.iteritems():
                sqlite_update_query = """UPDATE 'parallel_run_"""+str(table_number)+"""' set '""" + run + """' = '""" + str(
                    v) + """' where effective_date = '""" + str(i) + """'"""
                cursor.execute(sqlite_update_query)
            sqliteConnection.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")


    def addRunWeights(self,run, weights_df):
        sqliteConnection = None
        try:
            table_name = run + '_weight'
            sqliteConnection = sqlite3.connect(self.db_path)
            weights_df.columns = [col.replace(' ','_') for col in weights_df.columns]
            weights_df.to_sql(name=table_name, con=sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")

    def addRunWeightsPrediction(self,run, string_date, weights_df):
        sqliteConnection = None
        try:
            table_name = run +'_'+string_date+ '_weight_prediction'
            sqliteConnection = sqlite3.connect(self.db_path)
            weights_df.columns = [col.replace(' ','_') for col in weights_df.columns]
            weights_df.to_sql(name=table_name, con=sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")


    def addRunRecordings(self,run, recordings_df):
        sqliteConnection = None
        try:
            table_name = run + '_recording'
            sqliteConnection = sqlite3.connect(self.db_path)
            recordings_df.to_sql(name=table_name, con=sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")


    def addRunActivationsFollowUp(self, run, activations_df):
        sqliteConnection = None
        try:
            table_name = run + '_activation'
            sqliteConnection = sqlite3.connect(self.db_path)
            activations_df.to_sql(name=table_name, con=sqliteConnection)
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")

    def addResults(self, table_number, run, values):
        success = self.insertResults(table_number, run, values)
        if not success :
            self.updateResults(table_number, run, values)

    def getRunAssociatedTable(self, run):
        run_counter = self.mapping_keys[run]
        table_number = run_counter % self.nb_tables
        return table_number

    def saveResults(self, run, values, weights_df):
        table_number = self.getRunAssociatedTable(run)
        self.addRun(table_number,run)
        self.addResults(table_number, run, values)
        #self.totalRow = self.datesCount()
        self.addRunWeights(run, weights_df)


    def checkRunExistence(self,run):
        for table_number in range(self.nb_tables):
            if self.checkLocalRunExistence(table_number,run):
                return True, table_number
        return False, np.nan

    def checkLocalRunExistence(self,table_number, run):
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

    def datesCount(self):
        sqliteConnection = None
        try:
            sqliteConnection = sqlite3.connect(self.db_path, timeout=20)
            cursor = sqliteConnection.cursor()
            sqlite_select_query = """SELECT count(*) from parallel_run"""
            cursor.execute(sqlite_select_query)
            totalRows = cursor.fetchone()
            print("Total rows are:  ", totalRows)
            cursor.close()
            return totalRows
        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The Sqlite connection is closed")



    def upload_results_to_dropbox(self):
        print('uploading to dropbox the results '+self.db_path)
        self.dbx.uploadFileToDropbox(filename=self.filename,fullpath = self.db_path)
