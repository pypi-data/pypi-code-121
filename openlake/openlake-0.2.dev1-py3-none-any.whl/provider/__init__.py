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
"""
Openlake providers.
"""
import abc
import logging
import pathlib
import types
import typing

import forml
import pandas
from forml.io import dsl

from openlake import cache

LOGGER = logging.getLogger(__name__)

_DTYPES: typing.Mapping[dsl.Any, type] = {
    dsl.Integer(): int,
    dsl.Float(): float,
    dsl.String(): object,
}


class Partition(abc.ABC):
    """Provider specific representation of a data partition."""

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.key == self.key

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """Get the partition identifier key."""


PayloadT = typing.TypeVar('PayloadT')
PartitionT = typing.TypeVar('PartitionT', bound=Partition)


class Origin(typing.Generic[PartitionT, PayloadT], metaclass=abc.ABCMeta):
    """Openlake origin base class."""

    def __hash__(self):
        return hash(self.source)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.source == self.source

    def __call__(self, partitions: typing.Iterable[PartitionT]) -> pandas.DataFrame:
        LOGGER.info('Loading %s', self.key)
        frame = self._load(partitions)
        expected = {f.name: f.kind for f in self.source.features}
        assert (actual := set(frame.columns)).issubset(expected), f'Unexpected column(s): {actual.difference(expected)}'
        return frame.astype({c: _DTYPES.get(expected[c], expected[c].__type__) for c in frame.columns})

    @property
    def _cachedir(self) -> pathlib.Path:
        """Root directory for this origin cache."""
        return cache.DIR / self.__class__.__module__.rsplit('.', 1)[-1]

    def _load(self, partitions: typing.Iterable[PartitionT]) -> pandas.DataFrame:
        """Content loader with caching capabilities.

        Args:
            partitions: Sequence of partitions to load.

        Returns:
            Data in Pandas DataFrame format.
        """

        def load(partition: PartitionT) -> pandas.DataFrame:
            """Helper for cached loading of the given partition."""
            LOGGER.debug('Loading %s:%s', self.key, partition.key)
            return cache.dataframe(
                f'{self.key}:{partition.key}',
                lambda: self.parse(partition, self.fetch(partition)),
                self._cachedir,
            )

        return pandas.concat((load(p) for p in partitions), ignore_index=True)

    @property
    def key(self) -> str:
        """Name to be used for internal (unique) referencing.

        Must be a valid identifier -> [_a-zA-Z][_a-zA-Z0-9]*
        """
        return repr(self.source)

    @property
    @abc.abstractmethod
    def source(self) -> dsl.Queryable:
        """The source query this origin provides."""

    @abc.abstractmethod
    def partitions(
        self, columns: typing.Collection[dsl.Column], predicate: typing.Optional[dsl.Predicate]
    ) -> typing.Iterable[PartitionT]:
        """Get the partitions for the data selection.

        Args:
            columns: Iterable of required columns (more can be returned).
            predicate: Optional push-down row filter (mismatching rows can still be returned).

        Returns:
            Iterable of partition identifiers containing the requested data.
        """

    @abc.abstractmethod
    def fetch(self, partition: PartitionT) -> PayloadT:
        """Fetch the content and return a data content object.

        Args:
            partition: Partition identifiers to be fetched.

        Returns:
            Data content object in a generic PayloadT to be parsed.
        """

    @abc.abstractmethod
    def parse(self, partition: PartitionT, content: PayloadT) -> pandas.DataFrame:
        """Parse the origin dataset.

        Args:
            partition: Partition identifier representing the content.
            content: The data content object as returned by `.fetch()`.

        Returns:
            Data in Pandas DataFrame format.
        """


class Unavailable(types.ModuleType):
    """Placeholder for missing provider functionality that raises upon access."""

    class Error(forml.MissingError):
        """Custom exception for indicating access to an unavailable provider."""

    def __init__(self, name: str, error: Exception):
        super().__init__(name)
        self.__error__: Exception = error

    def __getattr__(self, item: str):
        raise self.Error(
            f'Provider {self.__name__} not available when accessing {item}: {self.__error__}.'
        ) from self.__error__
