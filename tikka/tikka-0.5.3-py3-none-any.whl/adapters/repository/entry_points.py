# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Any, List, Optional
from uuid import UUID

from tikka.adapters.repository.sqlite3 import Sqlite3RepositoryInterface
from tikka.domains.entities.entry_point import EntryPoint
from tikka.interfaces.adapters.repository.entry_points import (
    EntryPointsRepositoryInterface,
)

TABLE_NAME = "entry_points"

SQL_COLUMNS = {
    EntryPointsRepositoryInterface.COLUMN_URL: "url",
    EntryPointsRepositoryInterface.COLUMN_NODE_ID: "node_id",
}
SQL_SORT_ORDER = {
    EntryPointsRepositoryInterface.SORT_ORDER_ASCENDING: "ASC",
    EntryPointsRepositoryInterface.SORT_ORDER_DESCENDING: "DESC",
}

DEFAULT_LIST_OFFSET = 0
DEFAULT_LIST_LIMIT = 1000


class Sqlite3EntryPointsRepository(
    EntryPointsRepositoryInterface, Sqlite3RepositoryInterface
):
    """
    Sqlite3EntryPointsRepository class
    """

    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_order: int = EntryPointsRepositoryInterface.SORT_ORDER_ASCENDING,
        sort_column: str = EntryPointsRepositoryInterface.COLUMN_URL,
        node_id: Optional[UUID] = None,
    ) -> List[EntryPoint]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            EntryPointsRepositoryInterface.list.__doc__
        )
        # map interface flags to SQL
        sql_sort_column = SQL_COLUMNS[sort_column]
        sql_sort_order = SQL_SORT_ORDER[sort_order]

        # filter by node_id
        where = ""
        sql_args: List[Any] = []
        if node_id is not None:
            where += f"{SQL_COLUMNS[EntryPointsRepositoryInterface.COLUMN_NODE_ID]} = ?"
            sql_args.append(node_id.hex)
        if where != "":
            where = f"WHERE {where}"

        sql = f"SELECT * FROM {TABLE_NAME} {where} ORDER BY {sql_sort_column} {sql_sort_order} LIMIT {limit} OFFSET {offset}"
        if len(sql_args) > 0:
            result_set = self.client.select(sql, sql_args)
        else:
            result_set = self.client.select(sql)

        list_ = []
        for row in result_set:
            list_.append(get_entry_point_from_row(row))

        return list_

    def add(self, entry_point: EntryPoint) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            EntryPointsRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_entry_point(entry_point),
        )

    def get(self, url: str) -> Optional[EntryPoint]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            EntryPointsRepositoryInterface.list.__doc__
        )

        row = self.client.select_one(f"SELECT * FROM {TABLE_NAME} WHERE url=?", (url,))

        if row is None:
            return None

        return get_entry_point_from_row(row)

    def update(self, entry_point: EntryPoint) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            EntryPointsRepositoryInterface.update.__doc__
        )
        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"url='{entry_point.url}'",
            **get_fields_from_entry_point(entry_point),
        )

    def delete(self, url: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            EntryPointsRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, url=url)


def get_fields_from_entry_point(entry_point: EntryPoint) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param entry_point: EntryPoint instance
    :return:
    """
    fields = {}
    for (key, value) in entry_point.__dict__.items():
        if key.startswith("_"):
            continue
        if key == "node_id" and value is not None:
            # node id UUID to hex str
            value = value.hex
        fields[key] = value

    return fields


def get_entry_point_from_row(row: tuple) -> EntryPoint:
    """
    Return a EntryPoint instance from a result set row

    :param row: Result set row
    :return:
    """
    values = list(row)
    # node id str to UUID
    if values[1] is not None:
        values[1] = UUID(row[1])

    return EntryPoint(*values)
