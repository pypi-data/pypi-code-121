from __future__ import annotations

import functools
from typing import Dict, List

from minumtium.infra.database import DatabaseAdapter, DataFetchException, DataNotFoundException, DataInsertException
from pydantic import BaseModel
from sqlalchemy import Table, MetaData, func, create_engine, String, cast

from minumtium_postgres.migrations import apply_migrations


class MinumtiumPostgresAdapterConfig(BaseModel):
    username: str
    password: str
    host: str
    port: int
    dbname: str
    schema_name: str


class MinumtiumPostgresAdapter(DatabaseAdapter):

    def __init__(self, config: MinumtiumPostgresAdapterConfig, table_name: str, engine=None):
        self.engine = self.initialize(config, engine)
        self.metadata_obj = MetaData(bind=self.engine, schema=config.schema_name)
        self.table_name = table_name
        self.table = Table(table_name, self.metadata_obj, autoload=True)

        self.cast_columns = self._setup_cast_columns(self.table)
        self.summary_columns_value = None

    def initialize(self, config: MinumtiumPostgresAdapterConfig, engine=None):
        engine = engine or self.create_postgres(config)
        self._migrate(engine, schema=config.schema_name)
        return engine

    @staticmethod
    def _setup_cast_columns(table):
        columns = []
        for name, column in table.c.items():
            if name in ['id', 'timestamp']:
                columns.append(cast(column, String()))
                continue
            columns.append(column)
        return columns

    @staticmethod
    def _setup_summary_columns(table):
        return [cast(table.c.id, String()),
                table.c.title,
                table.c.author,
                cast(table.c.timestamp, String())]

    @staticmethod
    def create_postgres(config: MinumtiumPostgresAdapterConfig):
        username = config.username
        password = config.password
        host = config.host
        port = config.port
        dbname = config.dbname
        return create_engine(f"postgresql+pg8000://{username}:{password}@{host}:{port}/{dbname}")

    @staticmethod
    def _migrate(engine, schema):
        apply_migrations(engine, schema)

    @staticmethod
    def _cast_results(query_results):
        return [dict(result) for result in query_results]

    @property
    def summary_columns(self):
        if not self.summary_columns_value:
            self.summary_columns_value = self._setup_summary_columns()
        return self.summary_columns_value

    def find_by_id(self, id: str):
        statement = (self.table
                     .select()
                     .where(self.table.c.id == int(id))
                     .with_only_columns(self.cast_columns))

        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    result = connection.execute(statement).mappings().first()
                except Exception as e:
                    raise DataFetchException(f'Error running query: {str(e)}') from e

        if not result:
            raise DataNotFoundException(f'No data found at {self.table_name} for id: {id}')

        return dict(result)

    def find_by_criteria(self, query_criteria: Dict):

        def convert_id(criteria: Dict):
            if 'id' in criteria:
                criteria['id'] = int(criteria['id'])
            return criteria

        def create_query(criteria: Dict):
            query = self.table.select()
            for column, value in criteria.items():
                column = getattr(self.table.c, column)
                query = query.where(column == value)
            query = query.with_only_columns(self.cast_columns)
            return query

        query_criteria = convert_id(query_criteria)
        statement = create_query(query_criteria)

        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    results = connection.execute(statement)
                except Exception as e:
                    raise DataFetchException(f'Could not select by criteria: {str(query_criteria)}') from e

        if not results.rowcount:
            raise DataNotFoundException(f'No data found for the following criteria: {str(query_criteria)}')

        return self._cast_results(results.mappings().all())

    def insert(self, data: Dict) -> str:
        statement = self.table.insert(data)

        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    result = connection.execute(statement)
                except Exception as e:
                    raise DataInsertException(f'An error has happened inserting into: {self.table_name}') from e

        return str(result.inserted_primary_key[0])

    def all(self, limit: int = None, skip: int = None, sort_by: str = None):

        statement = (self.table.select()
                     .limit(limit)
                     .offset(skip)
                     .with_only_columns(self.cast_columns))
        if sort_by:
            column = getattr(self.table.c, sort_by)
            statement = statement.order_by(column.desc())

        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    results = connection.execute(statement)
                except Exception as e:
                    raise DataFetchException(f'An error has happened selecting from: {self.table_name}') from e

        if results is None:
            raise DataNotFoundException(f'No data found at {self.table_name}.')

        return self._cast_results(results.mappings().all())

    def _project_summary_fields(self, projection):
        columns = []
        for field in projection:
            if field in ['id', 'timestamp']:
                columns.append(cast(getattr(self.table.c, field), String()))
                continue
            columns.append(getattr(self.table.c, field))
        return columns

    def summary(self, projection: List[str], limit: int = 10, sort_by: str = None):
        columns = self._project_summary_fields(projection)
        statement = (self.table.select()
                     .with_only_columns(columns)
                     .limit(limit))
        if sort_by:
            column = getattr(self.table.c, sort_by)
            statement = statement.order_by(column.desc())

        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    results = connection.execute(statement)
                except Exception as e:
                    raise DataFetchException(
                        f'An error has happened getting the summary from: {self.table_name}') from e

        if results is None:
            raise DataNotFoundException(f'No data found at {self.table_name}.')

        return self._cast_results(results.mappings().all())

    def delete(self, id: str) -> None:
        statement = (self.table.delete().where(self.table.c.id == int(id)))

        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    connection.execute(statement)
                except Exception as e:
                    raise DataFetchException(f'An error has happened deleting the id: {id}') from e

    def count(self) -> int:
        count_column = func.count(self.table.c.id)
        statement = (self.table
                     .select()
                     .with_only_columns(count_column))
        with self.engine.connect() as connection:
            with connection.begin():
                try:
                    return connection.execute(statement).scalar()
                except Exception as e:
                    raise DataFetchException(f'An error has happened getting the count from: {self.table_name}') from e

    def truncate(self):
        statement = self.table.delete()
        with self.engine.connect() as connection:
            with connection.begin():
                connection.execute(statement)
