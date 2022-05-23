#   Copyright 2022-2022 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from itertools import zip_longest
from typing import List, Optional, Union

from sortedcontainers import SortedDict
from th2_common_utils.event_utils import create_event_body


class AbstractTable:

    def __init__(self, columns_names: List[str]):
        self.rows = SortedDict()
        self.columns_names = columns_names

    def add_row(self, *values: Optional[Union[str, int, float]]) -> None:
        if values:
            row_name = values[0]
            row_values = values[1:]
            self.rows[row_name] = {
                'type': 'row',
                'columns': dict(zip_longest(self.columns_names, row_values, fillvalue=''))
            }

    def add_table(self, table_name: Union[str, int, float], table: 'Table') -> None:
        self.rows[table_name] = table


class Table(AbstractTable):

    def __init__(self, columns_names: List[str]):
        super().__init__(columns_names)
        self.type = 'collection'


class TreeTable(AbstractTable):

    def __init__(self, columns_names: List[str]) -> None:
        super().__init__(columns_names)
        self.type = 'treeTable'

    def __bytes__(self) -> bytes:
        return create_event_body(self)
