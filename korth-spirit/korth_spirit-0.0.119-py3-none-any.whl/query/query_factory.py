# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from korth_spirit.query.world_attribute import WorldAttributeQuery

from .objects import ObjectQuery
from .query_enum import QueryEnum
from .terrain import TerrainQuery


class QueryFactory:
    def __init__(self, instance: "Instance", query_type: QueryEnum = QueryEnum.OBJECT) -> None:
        self.query_type = query_type
        self.instance = instance

    def __call__(self, **kwargs) -> "Query":
        """
        Creates a query.

        Args:
            **kwargs: The query arguments.

        Returns:
            Query: The query.
        """
        if self.query_type == QueryEnum.OBJECT:
            return ObjectQuery(self.instance).query(**kwargs)
        elif self.query_type == QueryEnum.TERRAIN:
            return TerrainQuery(self.instance).query(**kwargs)
        elif self.query_type == QueryEnum.WORLD:
            return WorldAttributeQuery(self.instance).query(**kwargs)
        
        raise ValueError("Invalid query type.")
