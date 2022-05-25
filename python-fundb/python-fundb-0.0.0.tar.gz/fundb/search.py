#-----------------------------
# -- fundb --
# search module
#-----------------------------

import copy
import math
from typing import Any, List

# Map filter
# Map filter operators with their functions
QUERY_FILTERING_MAPPER = {
    '=': '_is_equal',
    'eq': '_is_equal',
    '!=': '_is_not_equal',
    'neq': '_is_not_equal',
    '>': '_is_greater',
    'gt': '_is_greater',
    '<': '_is_smaller',
    'lt': '_is_smaller',
    '>=': '_is_greater_equal',
    'gte': '_is_greater_equal',
    '<=': '_is_smaller_equal',
    'lte': '_is_smaller_equal',
    'in': '_is_in',
    'notin': '_is_not_in',
    'null': '_is_null',
    'notnull': '_is_not_null',
    'startswith': '_is_starts_with',
    'endswith': '_is_ends_with',
    'includes': '_is_includes',
    'between': "_is_between"
}

# FILTER_OPERATOR:
FILTER_OPERATOR = ":$"

# SQL_OPERATORS: valid/strict operators for SQL
SQL_OPERATORS = {
    "eq": "= ?",
    "ne": "!= ?",
    "lt": "< ?",
    "gt": "> ? ",
    "lte": "<= ?",
    "gte": ">= ? ",
    "between": "BETWEEN ? AND ?",
}

# -------------------------------------------------------------------

def execute(data: list, filters: dict = {}) -> List[dict]:
    """
    To execute a search

    Args:
        data: list[dict]
        filters: dict

    Returns:
        List[dict]
    """

    # no filters
    if not filters or not data:
        return data
    
    q = _Query(data)
    _generate_query_filter(q, filters)
    return q.get()

# -------------------------------------------------------------------

class _Matcher(object):
    """docstring for Helper."""
    MAP = QUERY_FILTERING_MAPPER

    def _is_equal(self, x, y):
        return x == y

    def _is_not_equal(self, x, y):
        return x != y

    def _is_greater(self, x, y):
        return x > y

    def _is_smaller(self, x, y):
        return x < y

    def _is_greater_equal(self, x, y):
        return x >= y

    def _is_smaller_equal(self, x, y):
        return x <= y

    def _is_in(self, key, arr):
        return isinstance(arr, list) and \
            bool(len(([k for k in key if k in arr]
                 if isinstance(key, list) else key in arr)))

    def _is_not_in(self, key, arr):
        return isinstance(arr, list) and (key not in arr)

    def _is_null(self, x, y=None):
        return x is None

    def _is_not_null(self, x, y=None):
        return x is not None

    def _is_starts_with(self, data, val):
        return data.startswith(val)

    def _is_ends_with(self, data, val):
        return data.endswith(val)

    def _is_includes(self, ldata, val):
        if isinstance(ldata, (list, dict, str)):
            return val in ldata
        return False

    def _is_between(self, data, val):
        """
        TODO: IMPLEMENT
        """
        return False


    def _to_lower(self, x, y):
        return [[v.lower() if isinstance(v, str) else v for v in val]
                if isinstance(val, list) else val.lower()
                if isinstance(val, str) else val
                for val in [x, y]]

    def _match(self, x, op, y, case_insensitive):
        """Compare the given `x` and `y` based on `op`

        :@param x, y, op, case_insensitive
        :@type x, y: mixed
        :@type op: string
        :@type case_insensitive: bool

        :@return bool
        :@throws ValueError
        """
        if (op not in self.MAP):
            raise ValueError('Invalid where condition given: %s' % op)

        if case_insensitive:
            x, y = self._to_lower(x, y)

        func = getattr(self, self.MAP.get(op))
        return func(x, y)


class _Query(object):
    """Query over Json file"""

    def __init__(self, data: list):
        """
        TODO: To perform the search, we will flattent the data - O(n)
        :@param file_path: Set main json file path
        :@type dict: data
        """

        if isinstance(data, list):
            self._raw_data = data
            self._json_data = copy.deepcopy(self._raw_data)
        else:
            raise TypeError("Provided Data is not json")

        self.__reset_queries()
        self._matcher = _Matcher()

    def __reset_queries(self):
        """Reset previous query data"""

        self._queries = []
        self._current_query_index = 0

    def get(self):
        """Getting prepared data

        :@return object
        """
        self.__prepare()
        return self._json_data

    def clone(self):
        """Clone the exact same copy of the current object instance."""
        return copy.deepcopy(self._json_data)

    def __store_query(self, query_items):
        """Make where clause

        :@param query_items
        :@type query_items: dict
        """
        temp_index = self._current_query_index
        if len(self._queries) - 1 < temp_index:
            self._queries.append([])

        self._queries[temp_index].append(query_items)

    def __prepare(self):
        """Prepare query result"""

        if len(self._queries) > 0:
            self.__execute_queries()
            self.__reset_queries()

    def __execute_queries(self):
        """Execute all condition and filter result data"""

        def func(item):
            or_check = False
            for queries in self._queries:
                and_check = True
                for query in queries:
                    and_check &= self._matcher._match(
                        item.get(query.get('key'), None),
                        query.get('operator'),
                        query.get('value'),
                        query.get('case_insensitive')
                    )
                or_check |= and_check
            return or_check

        self._json_data = list(
            filter(lambda item: func(item), self._json_data))

    # ---------- Query Methods ------------- #

    def where(self, key, operator, value, case_insensitive=False):
        """Make where clause

        :@param key
        :@param operator
        :@param value
        :@type key,operator,value: string

        :@param case_insensitive
        :@type case_insensitive: bool

        :@return self
        """
        self.__store_query({
            "key": key,
            "operator": operator,
            "value": value,
            "case_insensitive": case_insensitive
        })

        return self

    def or_where(self, key, operator, value):
        """Make or_where clause

        :@param key
        :@param operator
        :@param value
        :@type key, operator, value: string

        :@return self
        """
        if len(self._queries) > 0:
            self._current_query_index += 1
        self.__store_query({"key": key, "operator": operator, "value": value})
        return self

    # ---------- Aggregate Methods ------------- #

    def count(self):
        """Getting the size of the collection

        :@return int
        """
        self.__prepare()
        return len(self._json_data)

    def first(self):
        """Getting the first element of the collection otherwise None

        :@return object
        """
        self.__prepare()
        return self._json_data[0] if self.count() > 0 else None

    def last(self):
        """Getting the last element of the collection otherwise None

        :@return object
        """
        self.__prepare()
        return self._json_data[-1] if self.count() > 0 else None

    def nth(self, index):
        """Getting the nth element of the collection

        :@param index
        :@type index: int

        :@return object
        """
        self.__prepare()
        return None if self.count() < math.fabs(index) else self._json_data[index]

    def sum(self, property):
        """Getting the sum according to the given property

        :@param property
        :@type property: string

        :@return int/float
        """
        self.__prepare()
        total = 0
        for i in self._json_data:
            total += i.get(property)

        return total

    def max(self, property):
        """Getting the maximum value from the prepared data

        :@param property
        :@type property: string

        :@return object
        :@throws KeyError
        """
        self.__prepare()
        try:
            return max(self._json_data, key=lambda x: x[property]).get(property)
        except KeyError:
            raise KeyError("Key is not exists")

    def min(self, property):
        """Getting the minimum value from the prepared data

        :@param property
        :@type property: string

        :@return object
        :@throws KeyError
        """
        self.__prepare()
        try:
            return min(self._json_data, key=lambda x: x[property]).get(property)
        except KeyError:
            raise KeyError("Key is not exists")

    def avg(self, property):
        """Getting average according to given property

        :@param property
        :@type property: string

        :@return average: int/float
        """
        self.__prepare()
        return self.sum(property) / self.count()


def _generate_query_filter_row(q: _Query, k: str, value: Any, _or: bool = False):
    operator = "$eq"  # default operator
    if ":" in k:
        k, operator = k.split(":", 2)
        operator = operator.lower()
    operator = operator.replace("$", "")

    if _or:
        q.or_where(k, operator, value)
    q.where(k, operator, value)

def _generate_query_filter(q: _Query, filters: dict) -> tuple:
    """
    Create a FILTER clause

    Params:
        filters: dict
            {
                'name': 'something',
                'age:$gt': 18,
                'cities:$in': ['charlotte', 'Concord'],
                '$or': [{
                       "cities:$in": [],
                       "_perms.read:$in":[] 
                 }]
                ]
            }
    """

    for k in filters:
        if k.startswith("$"):
            k_ = k.lower()
            # operation
            if k_ in ["$or"] and isinstance(filters[k], (dict, list)):
                fk = filters[k]
                if isinstance(fk, dict):
                    fk = [fk]
                for k0 in fk:
                    for k2 in k0:
                        _generate_query_filter_row(q, k2, k0[k2], _or=True)
            else:
                raise Exception("Invalid logic: %s" % k)
        else:
            _generate_query_filter_row(q, k, filters[k])



