# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Openlake ForML feed."""
import functools
import itertools
import logging
import types
import typing

import forml
import sqlalchemy
from forml import io
from forml.io import dsl, layout
from forml.io.dsl import parser as parsmod
from forml.provider.feed.reader.sql import alchemy
from sqlalchemy import sql
from sqlalchemy.engine import interfaces

from openlake import provider
from openlake.provider import kaggle, sklearn

__version__ = '0.2.dev1'
__author__ = 'ForML Authors'

ORIGINS: typing.Collection[provider.Origin] = {kaggle.Titanic(), sklearn.BreastCancer(), sklearn.Iris()}

LOGGER = logging.getLogger(__name__)


class _Columns(dsl.Source.Visitor):
    """Visitor for extracting used columns."""

    def __init__(self):
        self._items: set[dsl.Column] = set()

    @classmethod
    def extract(cls, query: dsl.Query) -> frozenset[dsl.Column]:
        """Frontend method for extracting all involved columns from the given query.

        Args:
            query: Query to extract the columns from.

        Return:
            Set of columns involved in the query.
        """
        return cls()(query)

    def __call__(self, query: dsl.Query) -> frozenset[dsl.Column]:
        """Apply this visitor to the given query.

        Args:
            query: Query to dissect.

        Returns:
            Set of dsl.Column instances involved in the query.
        """
        self._items = set()
        query.accept(self)
        return frozenset(self._items)

    def visit_join(self, source: dsl.Join) -> None:
        self._items.update(dsl.Column.dissect(source.condition))
        super().visit_join(source)

    def visit_query(self, source: dsl.Query) -> None:
        self._items.update(dsl.Column.dissect(*source.features))
        if source.prefilter:
            self._items.update(dsl.Column.dissect(source.prefilter))
        self._items.update(dsl.Column.dissect(*source.grouping))
        if source.postfilter:
            self._items.update(dsl.Column.dissect(source.postfilter))
        for ordering in source.ordering:
            self._items.update(dsl.Column.dissect(ordering.feature))
        super().visit_query(source)


class Local(io.Feed[sql.Selectable, sql.ColumnElement]):
    """Openlake feed."""

    class Reader(alchemy.Reader):
        """Extending the SQLAlchemy reader."""

        class Backend(interfaces.Connectable):
            """Serializable in-memory SQLite connection."""

            def __init__(self):
                self._engine: interfaces.Connectable = sqlalchemy.create_engine('sqlite://')

            def __repr__(self):
                return 'OpenLakeLocalBackend'

            def __reduce__(self):
                return self.__class__, ()

            def connect(self, **kwargs):
                return self._engine.connect(**kwargs)

            def execute(self, object_, *multiparams, **params):
                return self._engine.execute(object_, *multiparams, **params)

            def scalar(self, object_, *multiparams, **params):
                return self._engine.scalar(object_, *multiparams, **params)

            # pylint: disable=protected-access
            def _run_visitor(self, visitorcallable, element, **kwargs):
                return self._engine._run_visitor(visitorcallable, element, **kwargs)

            def _execute_clauseelement(self, elem, multiparams=None, params=None):
                return self._engine._execute_clauseelement(elem, multiparams, params)

            def __getattr__(self, item):
                return getattr(self._engine, item)

        def __init__(
            self,
            sources: typing.Mapping[dsl.Source, parsmod.Source],
            features: typing.Mapping[dsl.Feature, parsmod.Feature],
            origins: typing.Iterable[provider.Origin],
            **kwargs,
        ):
            self._loaded: dict[provider.Origin, frozenset[provider.Partition]] = {}
            self._origins: dict[dsl.Queryable, provider.Origin] = {o.source: o for o in origins}
            self._backend: Local.Reader.Backend = self.Backend()
            super().__init__(sources, features, self._backend, **kwargs)

        def __call__(self, query: dsl.Query, entry: typing.Optional[layout.Entry] = None) -> layout.Tabular:
            items = (
                (t, tuple(g)) for t, g in itertools.groupby(sorted(_Columns.extract(query)), key=lambda c: c.origin)
            )
            for table, columns in items:
                LOGGER.debug('Request for %s using columns: %s', table, columns)
                if table not in self._origins:
                    raise forml.MissingError(f'Unknown origin for table {table}')
                origin = self._origins[table]
                partitions = origin.partitions(columns, None)
                if origin not in self._loaded or not self._loaded[origin].symmetric_difference(partitions):
                    origin(partitions).to_sql(origin.key, self._backend, index=False, if_exists='replace')
                    self._loaded[origin] = frozenset(partitions)
            return super().__call__(query, entry)

    def __init__(self, *origins: provider.Origin, **readerkw):
        if not origins:
            origins = ORIGINS
        self._sources: typing.Mapping[dsl.Source, sql.Selectable] = types.MappingProxyType(
            {o.source: sqlalchemy.table(o.key) for o in origins}
        )
        self.__reduced: typing.Callable[[], Local] = functools.partial(self.__class__, *origins, **readerkw)
        super().__init__(origins=frozenset(origins), **readerkw)

    def __reduce__(self):
        return self.__reduced, ()

    @property
    def sources(self) -> typing.Mapping[dsl.Source, sql.Selectable]:
        return self._sources
