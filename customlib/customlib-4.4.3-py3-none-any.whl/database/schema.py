# -*- coding: UTF-8 -*-

from __future__ import annotations

from abc import ABC
from collections import namedtuple
from typing import Any, Generator

from .dialect import DDL, DML, DQL, Comparison
from .sqlite import SQLite
from ..exceptions import MissingEngineError, MissingColumnsError


class Model(ABC):
    """Base SQL model."""

    @staticmethod
    def _namedtuple(name: str, **kwargs):
        return namedtuple(name, kwargs.keys())(**kwargs)

    @property
    def typename(self):
        return self.__class__.__name__.lower()

    @property
    def parent(self):
        if hasattr(self, "_parent") is True:
            return getattr(self, "_parent")

    @parent.setter
    def parent(self, value):
        setattr(self, "_parent", value)

    @parent.deleter
    def parent(self):
        if hasattr(self, "_parent") is True:
            delattr(self, "_parent")

    def _collection(self, target: str, *args, **kwargs) -> dict:
        return {key: value for key, value in self._filter(target, *args, **kwargs)}

    def _filter(self, target: str, *args, **kwargs) -> Generator:
        """Match and yield only targeted `typename` objects."""
        target = target.lower()
        items = list(args) + list(kwargs.values())

        if "." in target:
            typename, attribute = target.split(".")
            for item in items:
                if (item.typename == typename) and (getattr(item, attribute) is True):
                    if attribute == "index":
                        item = Index(item)
                    if item.parent is None:
                        item.parent = self
                    yield item.name, item

        else:
            for item in items:
                if item.typename == target:
                    item.parent = self
                    yield item.name, item


class Schema(Model):
    """SQL `Schema` handler."""

    def __init__(self, name: str, engine: SQLite = None, *args, **kwargs):
        self.name = name
        self.engine = engine
        self._tables = self._collection("table", *args, **kwargs)

    @property
    def tables(self) -> tuple:
        if len(self._tables) > 0:
            return self._namedtuple("Tables", **self._tables)

    def add_table(self, table: Table):
        table.parent = self
        self._tables.update({table.name: table})

    def create(self, if_not_exists: bool = False):
        """
        Construct and execute a `CREATE` script for this schema.

        :param if_not_exists: Add 'IF NOT EXISTS' to the SQL statements.
        """
        sql_commands = self._create_sql(if_not_exists)
        script = "\n".join(sql_commands)
        self.executescript(script)

    def drop(self, if_exists: bool = False):
        """
        Construct and execute a `DROP` script for this schema.

        :param if_exists: Add 'IF EXISTS' to the SQL statements.
        """
        sql_commands = self._drop_sql(if_exists)
        script = "\n".join(sql_commands)
        self.executescript(script)

    def vacuum(self):
        """Issue a vacuum command."""
        self.execute(sql="VACUUM;")

    def _create_sql(self, if_not_exists: bool) -> Generator:
        """Construct and yield a `CREATE` statement for each object in the schema."""

        for table in self.tables:
            create = table.create(if_not_exists)
            yield f"{create.statement};"

            indexes = table.indexes
            if indexes is not None:
                for index in indexes:
                    create = index.create(if_not_exists)
                    yield f"{create.statement};"

    def _drop_sql(self, if_exists: bool) -> Generator:
        """Construct and yield a `DROP` statement for each object in the schema."""

        for table in self.tables:

            indexes = table.indexes
            if indexes is not None:
                for index in indexes:
                    drop = index.drop(if_exists)
                    yield f"{drop.statement};"

            drop = table.drop(if_exists)
            yield f"{drop.statement};"

    def executescript(self, script: str):
        """
        Execute a SQL script and commit the changes.

        :param script: The SQL script to be executed.
        :raises MissingEngineError: If no SQL engine is found.
        """

        try:
            engine = self._get_engine()
        except MissingEngineError:
            raise MissingEngineError(
                "Failed to execute the SQL script! "
                f"`{self.name}` schema is not bound to an Engine or Connection!"
            )
        else:
            engine.executescript(script)

    def execute(self, *args, **kwargs):
        """
        Execute a SQL command and commit the changes.

        :raises MissingEngineError: If no SQL engine is found.
        """

        try:
            engine = self._get_engine()
        except MissingEngineError:
            raise MissingEngineError(
                "Failed to execute the SQL statement! "
                f"`{self.name}` schema is not bound to an Engine or Connection!"
            )
        else:
            engine.execute(*args, **kwargs)

    def query(self, *args, **kwargs):
        """
        Execute a SQL query and return the results.

        :raises MissingEngineError: If no SQL engine is found.
        """

        try:
            engine = self._get_engine()
        except MissingEngineError:
            raise MissingEngineError(
                "Failed to execute the SQL statement! "
                f"`{self.name}` schema is not bound to an Engine or Connection!"
            )
        else:
            return engine.query(*args, **kwargs)

    def _get_engine(self) -> Any:
        if self.engine is not None:
            return self.engine
        else:
            raise MissingEngineError(
                f"`{self.name}` schema is not bound to an Engine or Connection!"
            )

    def __repr__(self):
        return f"{self.typename.title()}(name='{self.name}', engine={self.engine}, tables={self.tables})"


class Table(Model):
    """SQL `Table` handler."""

    @staticmethod
    def _resolve_constraints(target: Column, **columns):
        for column in columns.values():

            if column is not target:

                if column.primary is True:
                    column.primary = False

                if column.autoincrement is True:
                    column.autoincrement = False

            else:
                if column.primary is False:
                    column.primary = True

    def __init__(self, name: str, schema: Schema, *args, **kwargs):
        self.name = name
        self.schema = schema

        self._columns = self._collection("column", *args, **kwargs)

        if len(self._columns) == 0:
            raise MissingColumnsError(
                f"Failed to resolve the `columns` attribute for {self.typename.title()}(name={self.name})!"
            )

        self._indexes = self._collection("column.index", **self._columns)

        # we're also mapping foreign keys here, but they're not being used yet...
        self._primary, self._autoincrement, self._foreign = self._constraints(**self._columns)

        self.schema.add_table(table=self)
        self.ddl = DDL(model=self)
        self.dml = DML(model=self)
        self.dql = DQL(model=self)

    @property
    def columns(self):
        if len(self._columns) > 0:
            return self._namedtuple("Columns", **self._columns)

    c = columns

    @property
    def indexes(self):
        if len(self._indexes) > 0:
            return self._namedtuple("Indexes", **self._indexes)

    @property
    def primary(self):
        if len(self._primary) > 0:
            return self._namedtuple("Primary", **self._primary)

    @property
    def autoincrement(self):
        if len(self._autoincrement) > 0:
            return self._namedtuple("Autoincrement", **self._autoincrement)

    @property
    def foreign(self):
        if len(self._foreign) > 0:
            return self._namedtuple("Foreign", **self._foreign)

    def create(self, if_not_exists: bool = False):
        return self.ddl.create(if_not_exists)

    def drop(self, if_exists: bool = False):
        return self.ddl.drop(if_exists)

    def insert(self, *args, **kwargs):
        return self.dml.insert(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.dml.update(*args, **kwargs)

    def delete(self):
        return self.dml.delete()

    def select(self, *args):
        return self.dql.select(*args)

    def execute(self, *args, **kwargs):
        self.parent.execute(*args, **kwargs)

    def query(self, *args, **kwargs):
        return self.parent.query(*args, **kwargs)

    def _constraints(self, **kwargs) -> tuple:

        primary = self._collection("column.primary", **kwargs)
        autoincrement = self._collection("column.autoincrement", **kwargs)
        foreign = self._collection("column.foreign", **kwargs)

        try:
            ai = list(autoincrement)[0]
        except IndexError:
            pass
        else:
            column = autoincrement.pop(ai)
            autoincrement = {column.name: column}
            primary = {column.name: column}

            self._resolve_constraints(column, **kwargs)

        return primary, autoincrement, foreign

    def __repr__(self):
        return f"{self.typename.title()}(name='{self.name}', columns={self.columns}, indexes={self.indexes})"


class Column(Model):
    """SQL `Column` handler."""

    def __init__(self, name: str, type: str, **kwargs):
        self.name = name
        self.type = type
        self.null = kwargs.pop("null", True)
        self.primary = kwargs.pop("primary", False)
        self.foreign = kwargs.pop("foreign", False)
        self.autoincrement = kwargs.pop("autoincrement", False)
        self.unique = kwargs.pop("unique", False)
        self.index = kwargs.pop("index", False)

        self._comp = Comparison(model=self)

    def __eq__(self, other):
        return self._comp(operator="==", value=other)

    def __ne__(self, other):
        return self._comp(operator="!=", value=other)

    def __le__(self, other):
        return self._comp(operator="<=", value=other)

    def __ge__(self, other):
        return self._comp(operator=">=", value=other)

    def __lt__(self, other):
        return self._comp(operator="<", value=other)

    def __gt__(self, other):
        return self._comp(operator=">", value=other)

    def is_null(self):
        return self._comp(operator="IS", value="NULL")

    def is_not_null(self):
        return self._comp(operator="IS NOT", value="NULL")

    def like(self, value: str):
        return self._comp(operator="LIKE", value=value)

    def __repr__(self):
        return (
            f"{self.typename.title()}("
            f"name='{self.name}', "
            f"type='{self.type}', "
            f"null={self.null}, "
            f"primary={self.primary}, "
            f"foreign={self.foreign}, "
            f"autoincrement={self.autoincrement}, "
            f"unique={self.unique}, "
            f"index={self.index}"
            f")"
        )


class Index(Model):
    """SQL `Index` handler."""

    def __init__(self, column: Column):
        self.column = column.name
        self.table = column.parent.name
        self.name = f"idx_{self.column}_{self.table}"
        self.unique = column.unique

        self.ddl = DDL(model=self)

    def create(self, if_not_exists: bool = False):
        return self.ddl.create(if_not_exists)

    def drop(self, if_exists: bool = False):
        return self.ddl.drop(if_exists)

    def execute(self, *args, **kwargs):
        self.parent.execute(*args, **kwargs)

    def __repr__(self):
        return (
            f"{self.typename.title()}("
            f"name='{self.name}', table='{self.table}', column='{self.column}', unique={self.unique}"
            f")"
        )
