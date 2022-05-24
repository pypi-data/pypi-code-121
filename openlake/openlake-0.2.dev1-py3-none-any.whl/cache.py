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
Openlake caching.
"""
import logging
import pathlib
import typing

import pandas
from forml import conf

DIR = conf.USRDIR / 'openlake'

LOGGER = logging.getLogger(__name__)


def dataframe(
    key: str, loader: typing.Callable[[], pandas.DataFrame], cachedir: pathlib.Path = DIR
) -> pandas.DataFrame:
    """Return the dataframe for the given key - either from cache or via the loader followed by caching the content."""
    stored = cachedir / f'{key}.parquet'
    if stored.exists():
        LOGGER.debug('[%s] cache hit', key)
        return pandas.read_parquet(stored)
    LOGGER.debug('[%s] cache miss', key)
    frame = loader()
    cachedir.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(stored, index=False, engine='pyarrow', flavor='spark')
    return frame
