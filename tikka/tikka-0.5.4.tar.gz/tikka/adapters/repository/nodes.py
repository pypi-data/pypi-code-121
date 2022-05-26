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

from typing import List, Optional
from uuid import UUID

from tikka.adapters.repository.sqlite3 import Sqlite3RepositoryInterface
from tikka.domains.entities.node import Node
from tikka.interfaces.adapters.repository.nodes import NodesRepositoryInterface

TABLE_NAME = "nodes"

SQL_COLUMNS = {
    NodesRepositoryInterface.COLUMN_ID: "id",
    NodesRepositoryInterface.COLUMN_PEER_ID: "peer_id",
    NodesRepositoryInterface.COLUMN_BLOCK: "block",
    NodesRepositoryInterface.COLUMN_SOFTWARE: "software",
    NodesRepositoryInterface.COLUMN_SOFTWARE_VERSION: "software_version",
}
SQL_SORT_ORDER = {
    NodesRepositoryInterface.SORT_ORDER_ASCENDING: "ASC",
    NodesRepositoryInterface.SORT_ORDER_DESCENDING: "DESC",
}

DEFAULT_LIST_OFFSET = 0
DEFAULT_LIST_LIMIT = 1000


class Sqlite3NodesRepository(NodesRepositoryInterface, Sqlite3RepositoryInterface):
    """
    Sqlite3NodesRepository class
    """

    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_order: int = NodesRepositoryInterface.SORT_ORDER_ASCENDING,
        sort_column: str = NodesRepositoryInterface.COLUMN_ID,
    ) -> List[Node]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.list.__doc__
        )
        # map interface flags to SQL
        sql_sort_column = SQL_COLUMNS[sort_column]
        sql_sort_order = SQL_SORT_ORDER[sort_order]

        sql = f"SELECT * FROM {TABLE_NAME} ORDER BY {sql_sort_column} {sql_sort_order} LIMIT {limit} OFFSET {offset}"
        result_set = self.client.select(sql)
        list_ = []
        for row in result_set:
            list_.append(get_node_from_row(row))

        return list_

    def add(self, node: Node) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.add.__doc__
        )
        # insert only non protected fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_node(node),
        )

    def get(self, id: UUID) -> Optional[Node]:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.list.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE id=?", (id.hex,)
        )
        if row is None:
            return None

        return get_node_from_row(row)

    def update(self, node: Node) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"id='{node.id.hex}'",
            **get_fields_from_node(node),
        )

    def delete(self, id: UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, id=id.hex)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.delete.__doc__
        )

        self.client.clear(TABLE_NAME)

    def count(self) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.delete.__doc__
        )
        row = self.client.select_one(f"SELECT count(id) FROM {TABLE_NAME}")
        if row is None:
            return 0

        return row[0]


def get_fields_from_node(node: Node) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param node: Node instance
    :return:
    """
    fields = {}
    for (key, value) in node.__dict__.items():
        if key.startswith("_") or key == "entry_points":
            continue
        if key == "id":
            # id UUID to hex str
            value = value.hex
        fields[key] = value

    return fields


def get_node_from_row(row: tuple) -> Node:
    """
    Return a Node instance from a result set row

    :param row: Result set row
    :return:
    """
    values = list(row)
    values[0] = UUID(row[0])

    return Node(*values)
