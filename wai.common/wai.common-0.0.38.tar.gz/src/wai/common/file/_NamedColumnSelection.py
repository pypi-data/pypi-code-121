from typing import Union, Tuple, Pattern, Iterable, List

import re

from ..sequence import normalise_index, flatten

SELECTION_TYPE = Union[int,  # Selects a column by index
                       Tuple[int, int],  # Selects a half-open range of columns by index
                       str,  # Selects columns by name using regex matching
                       Pattern,  # Selects columns by name using regex matching
                       Iterable['SELECTION_TYPE']]  # Any iterable of any of the above


class NamedColumnSelection:
    """
    Class representing a selection of columns from a table-like structure
    with named columns.
    """
    def __init__(self, selection: SELECTION_TYPE):
        self.selection: SELECTION_TYPE = selection

    def apply(self, column_names: List[str]) -> List[int]:
        return self.select(self.selection, column_names)

    @staticmethod
    def select(selection: SELECTION_TYPE, column_names: List[str]) -> List[int]:
        """
        Selects the indices of a set of columns.

        :param selection:       The selection criteria.
        :param column_names:    The names of the columns.
        :return:                The list of column indices selected.
        """
        # Calculate the number of columns
        num_columns: int = len(column_names)

        # Process integer selections by normalisation
        if isinstance(selection, int):
            # Return the normalised selection as a list of itself
            return [normalise_index(selection, num_columns)]

        # Process tuple selections as a half-open range of indices
        elif isinstance(selection, tuple):
            # Get the normalised start and end indices
            start = normalise_index(selection[0], num_columns)
            end = normalise_index(selection[1], num_columns)

            # If end is before start, return the indices in reverse order
            step = -1 if end < start else 1

            # Return the half-open range between start and stop, as a list
            return [i for i in range(start, end, step)]

        # Process strings and patterns by regex matching column names
        elif isinstance(selection, str) or isinstance(selection, Pattern):
            # Return any columns that match by name
            return [i
                    for i, column_name in enumerate(column_names)
                    if re.search(selection, column_name)]

        # Process lists by recurse-and-flatten
        elif isinstance(selection, list):
            sub_selections = [NamedColumnSelection.select(sub_selection, column_names)
                              for sub_selection in selection]

            return flatten(sub_selections)
