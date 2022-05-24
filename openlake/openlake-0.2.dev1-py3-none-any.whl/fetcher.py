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
Fetcher implementations.
"""
import abc
import typing

from forml.io import dsl

from openlake import provider


class Mixin(typing.Generic[provider.PartitionT, provider.PayloadT], abc.ABC):
    """Fetcher mixin base class."""

    @abc.abstractmethod
    def partitions(
        self, columns: typing.Collection[dsl.Column], predicate: typing.Optional[dsl.Predicate]
    ) -> typing.Iterable[provider.PartitionT]:
        """Get the partitions for the data selection.

        Args:
            columns: Iterable of required columns (more can be returned).
            predicate: Optional push-down row filter (mismatching rows can still be returned).

        Returns:
            Iterable of partition identifiers containing the requested data.
        """

    @abc.abstractmethod
    def fetch(self, partition: provider.PartitionT) -> provider.PayloadT:
        """Fetch the content and return a data content object.

        Args:
            partition: Partition identifiers to be fetched.

        Returns:
            Data content object in a generic PayloadT to be parsed.
        """
