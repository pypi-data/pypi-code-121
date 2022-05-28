from zipfile import ZipFile
from datetime import date
import sqlite3 as lite
import urllib.parse as parse
import pathlib
import os
from dcclab import Database

"""
POM Database() object.
"""

class POMDatabase(Database):
    def __init__(self, databasePath=None):
        if databasePath is None:
            databasePath = self.searchDBPath()

        if databasePath is None:
            raise ValueError("Cannot find database mtp.db")

        super().__init__(databasePath)

    def searchDBPath(self):
        if os.exists('mtp.db'):
            return 'mtp.db'
        return None

    @staticmethod
    def createMTPDatabase():

        # Current directory is :
        print('Beginning process...')
        directory = os.path.dirname(__file__)
        print('Directory is : {}'.format(directory))

        # Path to the Molecular Tools Platform database is :
        mtpPath = os.path.join(directory, 'dcclab', 'database', 'mtp.db')
        print('Path to database "mtp.db" is : {}'.format(mtpPath))

        # We create a database object in rwc mode. If the database doesn't exist, we create it.
        # Then we connect to the database.
        # Database is in asynchronous mode for faster inserts.
        print('Connecting to database...')
        with Database(mtpPath, True) as database:
            print('Dropping all existing tables if any...')
            database.dropTable('Data-souris')
            database.dropTable('Data-Utilisation')
            database.dropTable('cziMetadata')
            database.dropTable('cziChannels')
            database.commit()
            print('Done.')

            print("WARNING : Database is in asynchronous mode.")
            database.asynchronous()

            # Now, we need paths to our metadata (the .czi files and the .csv files.)
            # For the .csv, we have :
            micePath = os.path.join(directory, 'dcclab', 'database', 'Data-souris.csv')
            utilPath = os.path.join(directory, 'dcclab', 'database', 'Data-Utilisation.csv')
            print('Path to mice data is : {}'.format(micePath))
            print('Path to util data is : {}'.format(utilPath))

            # For the .czi, we have :
            print('Finding czi files in POM...')
            files = findFiles(os.path.join(directory, 'dcclab', 'POM', 'injection AAV', 'résultats bruts', 'AAV'), 'czi') + \
                    findFiles(os.path.join(directory, 'dcclab', 'POM', 'injection AAV', 'résultats bruts', 'RABV'), 'czi')
            print('{} czi files were found!'.format(len(files)))

            # Now, we extract the metadata from our files. First, we start with the .csv files.
            # We extract the metadata.
            print('Extracting metadata from .csv files...')
            miceMetadata = Metadata(micePath)
            utilMetadata = Metadata(utilPath)
            print('...Done!')

            # We create tables for the metadata.
            print('Creating tables for the .csv metadata...')
            database.beginTransaction()
            database.createTable(miceMetadata.keys)
            database.createTable(utilMetadata.keys)
            database.commit()
            print('...Done!')

            # We insert the .csv Metadata into the tables.
            print('Inserting metadata into the database...')
            entries = miceMetadata.metadata
            database.beginTransaction()
            for line in entries.keys():
                database.insert('Data-souris', entries[line])
            database.commit()
            print('Data-souris was processed for {} lines...'.format(len(entries)))

            entries = utilMetadata.metadata
            database.beginTransaction()
            for line in entries.keys():
                database.insert('Data-Utilisation', entries[line])
            database.commit()
            print('Data-Utilisation was processed for {} lines...'.format(len(entries)))

            # We now process the czi files into the database.
            # We create the tables.
            database.beginTransaction()
            print('Creating the tables into the database...')
            cziMetadata = Metadata(files[0])
            database.createTable(cziMetadata.keys)
            print('Tables were created, processing the files...')
            database.commit()

            database.beginTransaction()
            for file in files:
                print('Processing {}...'.format(file))
                cziMetadata = Metadata(file)
                database.insert('cziMetadata', cziMetadata.metadata)
                for channelId in cziMetadata.channels.keys():
                    database.insert('cziChannels', cziMetadata.channels[channelId])
            database.commit()
            print('{} czi files were processed!'.format(len(files)))
            print('Database was successfully created.')
            return database

    def queryViralVectors():
            viralVectors = self.select('cziMetadata', 'viral_vectors')
            for viralVector in viralVectors:
                paths = self.select('cziMetadata', 'file_path', 'viral_vectors="{}"'.format(viralVector['viral_vectors']))
                queryFile = os.path.join(directory, 'query', 'query_{}.csv'.format(viralVector['viral_vectors']))
                with open(queryFile, 'w', encoding='UTF-8') as file:
                    for path in paths:
                        file.write(path['file_path'] + '\n')
