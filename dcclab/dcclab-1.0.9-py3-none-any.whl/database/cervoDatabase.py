from zipfile import ZipFile
from datetime import date
import sqlite3 as lite
import urllib.parse as parse
import pathlib
import os


"""
POM Database() object.
"""


class POMDatabase:
    def __init__(self, databasePath, writePermission=False):
        if writePermission is True:
            # Possible modes are read-only, read write and read write create
            # which are 'ro', 'rw', and 'rwc' respectively
            mode = 'rwc'
        elif writePermission is False:
            mode = 'ro'
        else:
            raise ValueError("writePermission parameter must be true or false")

        self.__mode = mode
        self.__databasePath = databasePath
        self.__connection = None
        self.__rows = None
        self.cursor = None

        self.connect()

