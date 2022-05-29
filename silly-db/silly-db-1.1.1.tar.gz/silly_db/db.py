
"""This module provides the class DB, main class of silly_db.

"""


import os
import sqlite3
from silly_db.helpers import (
    color,
    INITIALIZE_DB,
    hasher,
    )
from silly_db.exceptions import (
    SillyDbError,
    MIGRATE_ALL_ERROR,
)

from silly_db.selections import (
    Selection,
    SelectionItem,
    Model,
)


class DB:
    """Central object interacting with the database itself.
    params:
        - base: the absolute path on wich 'file' and 'migrations_dir' are
        relatives to.
        - file (required): path to your desired [name].sqlite3 file
        - migrations_dir: path to the directory containing the migrations
        - debug: default is 'True', shows some warnings in console.
         'False' will hide the warnings.
    """
    def __init__(
        self,
        base=None,
        file: str = None,
        migrations_dir: str = None,
        debug: bool = True
            ):
        if file is None:
            raise SillyDbError(
                "Missing parameter for DB: file=some_file_name.sqlite3")
        self.file = os.path.join(base, file)
        self.connection = sqlite3.connect(self.file)
        self.cursor = self.connection.cursor()
        self.migrations_dir = os.path.join(base, migrations_dir)
        self.debug = debug

        self.execute(INITIALIZE_DB)

    def _read_sql_file(self, file: str) -> str:
        """Returns the content of a given file"""
        with open(file, 'r') as sql_file:
            commands = sql_file.read()
        return commands

    def _get_headers(self, cursor_description):
        """Gathers the headers from a query. In case of duplicated headers,
        renames them, and sends a warning (if self.debug is True)"""
        headers = [description[0] for description in cursor_description]
        uniques = []
        warning = False  # inform the user if the headers have been changed
        for header in headers:
            counter = 1
            if header not in uniques:
                uniques.append(header)
            else:
                uniques.append(header + f"_{counter}")
                counter += 1
                warning = True
        if warning and self.debug:
            print(
                color["warning"] +
                "\n!!! WARNING : ambiguous query :\n"
                "Headers with same names, silly_db arbitrarily "
                "changed some of your headers. Use '[name] as [other_name)]'"
                " in your SQL query to fix this.\n" +
                color['end']
                )
        return uniques

    def model(self, table):
        """Takes a table name as parameter, returns the table as a Model"""
        new_model = Model(self, table)
        return new_model

    def execute(self, command):
        """'Begin transaction' and 'commit' are automatically added
        to the command, so don't use this key words."""
        commands = command.strip().split(";")
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            for command in commands:
                self.cursor.execute(command)
            self.cursor.execute("COMMIT;")
        except sqlite3.OperationalError as e:
            print("sqlite3.OperationalError :")
            print(e)

    def migrate(self, file=None):
        """Execute the migrations from a .sql file if the migration
        have not be done already."""
        hashes_selection = self.select("sha1 FROM _migrations_applied")
        hashes = [hash.sha1 for hash in hashes_selection]
        sha1 = hasher(file)
        if sha1 not in hashes:
            commands = self._read_sql_file(file)
            try:
                self.connection.executescript(commands)
                file_name = os.path.split(file)[-1]
                register_migration = (
                    "INSERT INTO '_migrations_applied' (file, sha1) "
                    f"VALUES('{file_name}', '{sha1}');"
                )
                self.execute(register_migration)
                if self.debug:
                    print(
                        color["success"] +
                        f"Migration successfully applied: {file_name}" +
                        color['end']
                        )
            except sqlite3.OperationalError as e:
                print("sqlite3.OperationalError :")
                print(e)

    def migrate_all(self, directory=None):
        """migrates all the files in the self.migrations_dir or a given
        directory"""
        if directory is not None:
            apply_dir = directory
        elif self.migrations_dir is None:
            raise SillyDbError(MIGRATE_ALL_ERROR)
        else:
            apply_dir = self.migrations_dir
        files = [
            file for file in os.listdir(apply_dir)
            if file.endswith(".sql")
            ]
        files.sort()
        for file in files:
            self.migrate(os.path.abspath(os.path.join(apply_dir, file)))

    def export(
        self,
        structure_file="00_structure.sql_bkp",
        data_file="01_data.sql_bkp",
        action="both"  # both / structure / data
            ):
        """By default export both data and structure with default file names"""
        structure = ""
        data = "BEGIN TRANSACTION;\n"
        for line in self.connection.iterdump():
            if "sqlite_sequence" not in line and \
                    "_migrations_applied" not in line:
                if line.startswith("INSERT"):
                    data += line+"\n"
                else:
                    structure += line+"\n"
        data += "COMMIT;"
        if action == "both" or action == "structure":
            with open(structure_file, 'w') as f:
                f.write(structure)
        if action == "both" or action == "data":
            with open(data_file, 'w') as f:
                f.write(data)

    def export_all(self, file=None):
        """Exports both structure and data to a single file,
         into a sql format."""
        if file is None:
            file = "backup_all_in_one.sql_bkp"
        with open(file, 'w') as f:
            for line in self.connection.iterdump():
                if "sqlite_sequence" not in line and \
                        "_migrations_applied" not in line:
                    f.write(f"{line}\n")

    def export_data(self, file=None):
        """Exports the datas only to a given file,
         into a sql format."""
        if file is not None:
            self.export(data_file=file, action="data")
        else:
            self.export(action="data")

    def export_structure(self, file=None):
        """Exports only the structure of the database to a given file,
        into a sql format."""
        if file is None:
            file = "00_structure.sql_bkp"
        self.cursor.execute("SELECT sql FROM sqlite_master;")
        with open(file, 'w') as f:
            f.write("BEGIN TRANSACTION;\n")
            for line in self.cursor.fetchall():
                if "sqlite_sequence" not in line[0] and \
                        "_migrations_applied" not in line[0]:
                    f.write(f"{line[0]};\n")
            f.write("COMMIT;")

    def query(self, command: str) -> Selection:
        """command is a SQL query, returns a Selection object"""
        self.cursor.execute(command)
        headers = self._get_headers(self.cursor.description)
        results = self.cursor.fetchall()
        answers = []
        responses = []
        for result in results:
            elem = dict(zip(headers, result))
            answers.append(elem)
        for answer in answers:
            dico = dict(answer.items())
            response = SelectionItem(dico)
            responses.append(response)
        selection = Selection(*responses)
        return selection

    def select(self, command: str) -> Selection:
        """Query tool, the parameter is a purely SQL query, but without
        the word SELECT at the beginig (as it's already the method name)
        """
        command = "SELECT " + command
        return self.query(command)
