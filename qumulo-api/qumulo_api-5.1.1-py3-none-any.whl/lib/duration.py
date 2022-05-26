# Copyright (c) 2022 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# qumulo_python_versions = { 3.6, latest }

# Helper functions for converting between C's struct duration and Python's
# timedelta.

from datetime import timedelta
from typing import Any

# Helper for working with struct duration_impl (from core/duration.h).
# It makes the duration available as a timedelta object.
#
# NB - This is a lossy conversion. struct duration provides
# time in nanoseconds, but the minimum resolution of
# timedelta is in microseconds.


# XXX jon: should be implemented with dataclasses, once we've ditched python 3.6 support.  The
# difficulty is cause by the rest bindings being included in infrastructure/cranq/cli.py.  See:
#   https://qumulo.slack.com/archives/C73C28ARX/p1649781464637059 and
#   https://qumulo.slack.com/archives/C99BVQQM8/p1649780686757149
class Duration:
    def __init__(self, delta: timedelta):
        self._delta = delta

    @property
    def delta(self) -> timedelta:
        return self._delta

    @classmethod
    def from_dict(cls, field_data: Any) -> 'Duration':
        decoder = lambda ns: timedelta(microseconds=int(ns) / 1000)
        return Duration(decoder(field_data['nanoseconds']))

    def to_dict(self) -> Any:
        encoder = lambda td: str(int(td.total_seconds() * 1e9))
        return {'nanoseconds': encoder(self._delta)}
