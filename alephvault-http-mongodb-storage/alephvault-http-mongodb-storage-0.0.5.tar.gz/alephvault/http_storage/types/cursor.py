from typing import NamedTuple, Optional, List
from pymongo import ASCENDING, DESCENDING


class Cursor(NamedTuple):
    """
    A cursor has 3 fields to use: an offset and a limit (defaults to 0) and
    a limit (default to whatever is set in MAX_RESULTS or a default of 20
    if that setting is absent), and perhaps a list of fields to order by
    (defaults to None).
    """

    order_by: Optional[List[str]]
    offset: Optional[int]
    limit: Optional[int]

    def sort_criteria(self):
        """
        Converts a list of strings to a list of sort criteria in pymongo
        format (list of (field_name, ASCENDING|DESCENDING)).
        :return: The converted criteria.
        """

        if not self.order_by:
            return []

        result = []
        for element in self.order_by:
            element = element.strip()
            if not element:
                raise ValueError("Invalid order_by field: empty name")
            direction = ASCENDING
            if element[0] == '-':
                element = element[1:]
                direction = DESCENDING
            result.append((element, direction))
        return result
