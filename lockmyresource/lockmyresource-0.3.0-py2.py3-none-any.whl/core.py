import datetime
import logging
import os
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from util import traced
from tableformatter import TableFormatter, rows_to_dicts


github_url = "https://github.com/szabopeter/lockmyresource"


class WrongDbVersionError(Exception):
    def __init__(self, program_version: str, db_version: str):
        self.program_version = program_version
        self.db_version = db_version
        super().__init__(
            f"Program ({program_version}) and DB version ({db_version}) don't match!",
        )


class InvalidUserError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


@dataclass
class Resource:
    name: str


@dataclass
class User:
    login: str
    @staticmethod
    def from_os() -> "User":
        try:
            return User(os.getlogin())
        except OSError:
            return no_user


no_user = User(None)


class Const:
    LOCKS_TABLE = "locks"
    VERSION_TABLE = "version"
    DB_VERSION = "0"


class ConnectionContextManager:
    def __init__(self, connection: Optional[sqlite3.Connection], dbfile: Path):
        self.is_my_connection = False
        if connection is None:
            connection = sqlite3.connect(str(dbfile), isolation_level=None)
            self.is_my_connection = True
        connection.row_factory = sqlite3.Row
        self.connection = connection
    
    def __enter__(self) -> "ConnectionContextManager":
        return self

    def __exit__(self, type, value, traceback):
        if self.is_my_connection is True:
            self.connection.close()

    @traced
    def execute_sql(self, sql, *args):
        return self.connection.execute(sql, *args)


class IDatabase(ABC):
    def __init__(self, dbfile: Path):
        self.dbfile = dbfile

    def get_dbdir(self) -> str:
        return str(self.dbfile.parent)
    
    def get_dbfile(self) -> str:
        return str(self.dbfile.name)

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def info(self) -> str:
        pass


class NoDatabase(IDatabase):
    def __init__(self, dbfile: Path):
        super().__init__(dbfile)
        self.dbfile = dbfile

    def list(self):
        return []

    def info(self) -> str:
        return f"Could not open {self.dbfile}"


class Database(IDatabase):
    def __init__(self, connection: Optional[sqlite3.Connection], dbfile: Path):
        super().__init__(dbfile)
        self.connection = connection
        self.dbfile = dbfile
        self.ensure_tables()

    def __repr__(self):
        return f"Database[{self.dbfile}]"

    @staticmethod
    @traced
    def open(dbfile: Path):
        try:
            return Database(None, dbfile)
        except sqlite3.OperationalError:
            logging.exception(f"Could not open {dbfile}")
            return NoDatabase(dbfile)

    @staticmethod
    @traced
    def keep_open(dbfile: Path):
        connection = sqlite3.connect(str(dbfile), isolation_level=None)
        return Database(connection, dbfile)

    def info(self) -> str:
        return f"Opened {self.dbfile}"

    @traced
    def get_connection(self) -> ConnectionContextManager:
        return ConnectionContextManager(self.connection, self.dbfile)

    @traced
    def set_dbfile(self, dbfile: Path):
        if self.connection is not None:
            self.connection.close()
            self.connection = sqlite3.connect(str(dbfile), isolation_level=None)
        self.dbfile = dbfile

    @traced
    def ensure_tables(self):
        db_version = self.get_db_version()
        if db_version is None:
            self.create_tables()
            return
        if db_version == Const.DB_VERSION:
            return
        raise WrongDbVersionError(Const.DB_VERSION, db_version)

    @traced
    def get_db_version(self):
        with self.get_connection() as conn:
            cursor = conn.execute_sql(
                f"SELECT COUNT(1) AS count FROM sqlite_master "
                f"WHERE type='table' AND name='{Const.VERSION_TABLE}'"
            )
            if cursor.fetchone()["count"] == 0:
                return None
            cursor = conn.execute_sql(
                f"SELECT MAX(version) AS version FROM {Const.VERSION_TABLE}"
            )
            return cursor.fetchone()["version"]

    @traced
    def create_tables(self):
        logging.info("Initializing database in {%s}", self.dbfile)
        with self.get_connection() as conn:
            for sql in [
                f"CREATE TABLE {Const.VERSION_TABLE} (version TEXT);",
                f"INSERT INTO {Const.VERSION_TABLE} VALUES ('{Const.DB_VERSION}');",
                f"CREATE TABLE {Const.LOCKS_TABLE} ("
                "resource TEXT PRIMARY KEY NOT NULL, "
                "user TEXT, "
                "locked_at TIMESTAMP, "
                "comment TEXT)",
            ]:
                conn.execute_sql(sql)
            conn.connection.commit()

    def lock(
        self, resource: Resource, user: User, timestamp: datetime.datetime, comment: str
    ):
        with self.get_connection() as conn:
            cursor = conn.execute_sql(
                f"SELECT user FROM {Const.LOCKS_TABLE} WHERE resource = ?;",
                (resource.name,),
            )
            row = cursor.fetchone()
            if row is None:
                conn.execute_sql(
                    f"INSERT INTO {Const.LOCKS_TABLE} VALUES (?, ?, ?, ?);",
                    (
                        resource.name,
                        user.login,
                        timestamp,
                        comment,
                    ),
                )
            else:
                locking_user = row["user"]
                if locking_user is not None:
                    logging.debug(
                        "Resource {%s} is already locked by {%s}",
                        resource.name,
                        locking_user,
                    )
                    return False

                cursor = conn.execute_sql(
                    f"UPDATE {Const.LOCKS_TABLE} SET user=?, locked_at=?, comment=? "
                    f"WHERE resource=? AND user IS NULL;",
                    (
                        user.login,
                        timestamp,
                        comment,
                        resource.name,
                    ),
                )

            conn.connection.commit()
            return True

    def release(self, resource: Resource, user: User) -> bool:
        with self.get_connection() as conn:
            cursor = conn.execute_sql(
                f"SELECT user FROM {Const.LOCKS_TABLE} WHERE resource = ?;",
                (resource.name,),
            )
            row = cursor.fetchone()
            locking_user = row["user"] if row is not None else None
            if locking_user != user.login:
                logging.debug(
                    "Resource {resource.name} is locked by {%s}, not {%s}",
                    locking_user,
                    user,
                )
                return False

            cursor = conn.execute_sql(
                f"UPDATE {Const.LOCKS_TABLE} SET user=NULL, locked_at=NULL, comment=NULL "
                f"WHERE resource=? AND user=?;",
                (
                    resource.name,
                    user.login,
                ),
            )
            conn.connection.commit()
            return True

    def list(self):
        with self.get_connection() as conn:
            cursor = conn.execute_sql(
                f"SELECT resource, user, locked_at, comment FROM {Const.LOCKS_TABLE};"
            )
            many = cursor.fetchall()
            return many


class LockRecord:
    def __init__(self, core: "Core", resource: Resource, user: User, locked_at: datetime.datetime, comment: str):
        self.core = core
        self.resource = resource
        self.user = user
        self.locked_at = locked_at
        self.comment = comment

    def lock(self, comment: str) -> bool:
        return self.core.lock(self.resource, comment)

    def release(self) -> bool:
        return self.core.release(self.resource)


class Core:
    def __init__(self, user: User, database: IDatabase, table_formatter: TableFormatter):
        if user is no_user or not isinstance(user, User) or not user.login:
            raise InvalidUserError()
        self.user = user
        self.database = database
        self.table_formatter = table_formatter

    def __repr__(self):
        return f"Core[{self.user, self.database}]"

    @traced
    def switch_database(self, database: IDatabase):
        self.database = database

    @traced
    def list_str(self) -> str:
        return self.table_formatter.to_string(self.database.list())
    
    @traced
    def list_raw(self) -> List[Dict]:
        return rows_to_dicts(self.database.list())

    @traced
    def list(self) -> List[LockRecord]:
        return [LockRecord(self, Resource(row["resource"]), User(row["user"]), row["locked_at"], row["comment"]) 
                for row in self.list_raw()]

    @traced
    def lock(self, resource: Resource, comment: str) -> bool:
        now = datetime.datetime.now()
        has_lock = False
        try:
            has_lock = self.database.lock(resource, self.user, now, comment)
        except sqlite3.OperationalError:
            logging.exception("sqlite exception while locking")
            return has_lock
        if has_lock is False:
            logging.warning("Could not lock {%s} for {%s}", resource, self.user)
        return has_lock

    @traced
    def release(self, resource: Resource) -> bool:
        return self.database.release(resource, self.user)
