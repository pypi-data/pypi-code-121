from typing import List, Union, Iterator, Dict, Iterable

from ._save_helper import quoted
from .._NamedColumnSelection import NamedColumnSelection, SELECTION_TYPE
from ._Attribute import Attribute, StringAttribute, NominalAttribute, NumericAttribute
from . import constants
from ... import onehot
from ...sequence import extract_by_index
from ...iterate import invert_indices
from ._error import ARFFError

# The type of the data section
VALUE_TYPE = Union[None, float, str]
ROW_TYPE = List[VALUE_TYPE]
DATA_TYPE = List[ROW_TYPE]

# Allow our selections to be raw or wrapped
SELECTION_TYPE = Union[NamedColumnSelection, SELECTION_TYPE]


class ARFFFile:
    """
    Represents an ARFF file in memory. Loads the file into memory on initialisation
    so it can be closed straight away.

    Currently does not handle relational attributes or date formats.
    """
    def __init__(self,
                 relation_name: str,
                 attributes: List[Attribute],
                 data: DATA_TYPE):
        self.relation_name: str = relation_name
        self._attributes: List[Attribute] = attributes
        self._data: DATA_TYPE = data

    def remove_row(self, row: int) -> ROW_TYPE:
        """
        Removes a single row from this ARFF file.

        :param row:     The index of the row to remove.
        :return:        The row itself.
        """
        return self._data.pop(row)

    def remove_rows(self, rows: Iterable[int]) -> DATA_TYPE:
        """
        Removes the given rows from this ARFF file and returns
        them. If indices are duplicated, they will be returned
        multiple times but only removed once.

        :param rows:    The rows to remove.
        :return:        The removed rows in the order given.
        """
        # Consume the iterable in case it's an iterator
        rows: List[int] = list(rows)

        # Save the result references first
        result: DATA_TYPE = extract_by_index(self._data, rows)

        # Construct the ordered unique list of rows to remove
        ordered_unique_rows = list(set(rows))
        ordered_unique_rows.sort()

        # Remove each row in reverse order (to not upset
        # ordering)
        for row in reversed(ordered_unique_rows):
            self.remove_row(row)

        return result

    def extract_rows(self, rows: Iterable[int]) -> 'ARFFFile':
        """
        Extracts a new ARFF file from this one consisting of the
        given rows in this file.

        :param rows:    The rows to extract (can contain duplicates).
        :return:        A new ARFF file with the given rows as its data.
        """
        return ARFFFile(
            self.relation_name,
            [attribute.copy() for attribute in self._attributes],
            [row.copy() for row in extract_by_index(self._data, rows)]
        )

    def extract_and_remove_rows(self, rows: Iterable[int]) -> 'ARFFFile':
        """
        Extracts a new ARFF file from this one consisting of the
        given rows in this file, and removes those rows from this
        ARFF file.

        :param rows:    The rows to extract (can contain duplicates).
        :return:        A new ARFF file with the given rows as its data.
        """
        return ARFFFile(
            self.relation_name,
            [attribute.copy() for attribute in self._attributes],
            self.remove_rows(rows)
        )

    def add_attribute(self, attribute: Attribute, at_index: int = -1):
        """
        Adds a new attribute to this ARFF file.

        :param attribute:   The attribute to add.
        :param at_index:    The index at which to insert the attribute.
        """
        # Make sure we don't already have an attribute with this name
        if attribute.name in self.attribute_names():
            raise ARFFError("Attribute '" + attribute.name + "' already exists in ARFF file")

        # Insert the attribute
        self._attributes.insert(at_index, attribute)

        # Insert missing values for the attribute in the data
        for row in self._data:
            row.insert(at_index, None)

    def remove_attributes(self, selection: SELECTION_TYPE):
        """
        Removes attributes and the associated data from the file.

        :param selection:   The selection of the attributes to remove.
        """
        # Get the indices of the attributes to remove
        remove_indices = self.selection_indices(selection)

        # Get the indices of the attributes to keep
        keep_indices = list(invert_indices(remove_indices, self.attribute_count()))

        # Remove the selected indices by extraction
        self._attributes = extract_by_index(self._attributes, keep_indices)

        # Remove the selected columns from the data
        for row_index in range(self.row_count()):
            self._data[row_index] = list(extract_by_index(self._data[row_index], keep_indices))

    def set_value(self, attribute_selection: SELECTION_TYPE, row: int, value: VALUE_TYPE):
        """
        Sets the value of the selected attribute in the given row.

        :param attribute_selection:     The selected attribute.
        :param row:                     The index of the row to set.
        :param value:                   The value to set.
        """
        # Get the index of the selected attribute
        attribute_index = self.selection_index(attribute_selection)

        # Get the attribute itself
        attribute: Attribute = self._attributes[attribute_index]

        # Parse the value to the correct type
        if value is not None:
            value = attribute(value)

        # Set the value in the data
        self._data[row][attribute_index] = value

    def get_value(self, attribute_selection: SELECTION_TYPE, row: int) -> VALUE_TYPE:
        """
        Gets the value of the given attribute in the given row.

        :param attribute_selection:     The attribute to get the value of.
        :param row:                     The row to get the value from.
        :return:                        The value.
        """
        # Get the index of the selected attribute
        attribute_index = self.selection_index(attribute_selection)

        return self._data[row][attribute_index]

    def row_count(self):
        """
        Gets the number of rows in the file.

        :return:    The number of rows.
        """
        return len(self._data)

    def attribute_count(self):
        """
        Gets the number of attributes in the file.

        :return:    The number of attributes.
        """
        return len(self._attributes)

    def map_string_attribute(self, selection: SELECTION_TYPE) -> List[str]:
        """
        Converts a string/nominal attribute to a numerical attribute where each entry is
        the index of the original string in a lookup table.

        :param selection:       The selection of the string/nominal attribute to map.
        :return:                The lookup table.
        """
        # Create the string index map for the selected attribute
        string_index_map = self.create_string_index_map(selection)

        # Get the selected attribute and its index
        attribute_index = self.selection_index(selection)
        attribute = self._attributes[attribute_index]

        # Create a table of strings from the index map (use the nominal ordering if a nominal attribute)
        string_table = attribute.ordered_values() if isinstance(attribute, NominalAttribute) else list(string_index_map)

        # Convert the string data to numeric
        for string_index, string in enumerate(string_table):
            numeric_value = float(string_index)
            row_indices = string_index_map[string]
            for row_index in row_indices:
                self._data[row_index][attribute_index] = numeric_value

        # Convert the attribute to a numeric attribute
        self._attributes[attribute_index] = NumericAttribute(attribute.name)

        # Return the lookup table
        return string_table

    def create_string_index_map(self, selection: SELECTION_TYPE) -> Dict[str, List[int]]:
        """
        Creates a mapping from string values to row indices for a string attribute
        or a nominal attribute.

        :param selection:   The selection of attribute to map.
        :return:            The index map for the strings in the given attribute.
        """
        # Get the index of the selected attribute
        attribute_index = self.selection_index(selection)

        # Get the attribute itself
        attribute = self._attributes[attribute_index]

        # Make sure the selected attribute is a string or nominal attribute
        if not (isinstance(attribute, StringAttribute) or isinstance(attribute, NominalAttribute)):
            raise ValueError("Can only map string or nominal attributes")

        # Create the map
        string_index_map = {}

        # Add each value to the map
        for row_index, row in enumerate(self._data):
            string_value = row[attribute_index]

            if string_value not in string_index_map:
                string_index_map[string_value] = []

            string_index_map[string_value].append(row_index)

        # Return the map
        return string_index_map

    def one_hot_encode(self):
        """
        Applies a one-hot encoding to all nominal attributes in the file.

        :return:    The mapping used to perform the encoding.
        """
        # Create the mapping from nominal to numeric attributes
        one_hot_map = create_one_hot_map(self._attributes)

        # Apply the mapping to the attributes
        self._attributes = one_hot_encode_attributes(self._attributes, one_hot_map)

        # Apply the mapping to the data
        one_hot_map.encode(self._data)

        # Return the one-hot encoding
        return one_hot_map

    def extract_data(self, selection: SELECTION_TYPE) -> DATA_TYPE:
        """
        Extracts the data for a selection of attributes/columns.

        :param selection:   The selection of attributes/columns.
        :return:            The data.
        """
        # Extract the selected columns from the data
        selection = self.selection_indices(selection)
        return [extract_by_index(row, selection) for row in self._data]

    def extract_all_data(self) -> DATA_TYPE:
        """
        Extracts a copy of this ARFF file's data.
        """
        return [row.copy() for row in self._data]

    def selection_attributes(self, selection: SELECTION_TYPE) -> List[Attribute]:
        """
        Gets the attributes selected by the given selection.

        :param selection:   The selection.
        :return:            The attributes.
        """
        return extract_by_index(self._attributes, self.selection_indices(selection))

    def selection_indices(self, selection: SELECTION_TYPE) -> List[int]:
        """
        Gets the attribute indices selected by the given selection.

        :param selection:   The selection.
        :return:            The attribute indices.
        """
        # Wrap any raw selection types
        if not isinstance(selection, NamedColumnSelection):
            selection = NamedColumnSelection(selection)

        return selection.apply(list(self.attribute_names()))

    def selection_index(self, selection: SELECTION_TYPE) -> int:
        """
        Gets the index of the attribute selected by the given selection.
        Enforces that one and only one attribute is selected.

        :param selection:   The selection.
        :return:            The attribute index.
        """
        # Get the selected indices
        attribute_indices = self.selection_indices(selection)

        # Make sure only one is selected
        if len(attribute_indices) != 1:
            raise ValueError("Must select one and only one attribute")

        # Return the single selected index
        return attribute_indices[0]

    def attribute_names(self) -> Iterator[str]:
        """
        Iterates over the names of the attributes.
        """
        return (attribute.name for attribute in self._attributes)

    def relation_section(self) -> str:
        """
        Gets the relation section of this ARFF file as a string.
        """
        return constants.RELATION_SECTION_KEYWORD + " " + quoted(self.relation_name)

    def attributes_section(self) -> str:
        """
        Gets the attributes section of this ARFF file as a string.
        """
        return "\n".join(attribute.to_string() for attribute in self._attributes)

    def data_section(self) -> str:
        """
        Gets the data section of this ARFF file as a string.
        """
        return constants.DATA_SECTION_KEYWORD + "\n" + \
            "\n".join(
                ",".join(
                    quoted(str(value)) if value is not None else constants.MISSING_VALUE_SYMBOL
                    for value in row
                )
                for row in self._data
            )

    def __str__(self) -> str:
        return self.relation_section() + "\n\n" + \
               self.attributes_section() + "\n\n" + \
               self.data_section() + "\n"


def create_one_hot_map(attributes: List[Attribute]) -> onehot.Mapping:
    """
    Creates a list of one-hot encoding maps for the given attributes.

    :param attributes:      The attributes being encoded.
    :return:                The list of one-hot mappings.
    """

    # Create the map
    one_hot_map = onehot.Mapping(len(attributes))

    # Process each attribute
    for attribute_index, attribute in enumerate(attributes):
        # If the attribute is nominal, add a mapping from value name to encoding
        if isinstance(attribute, NominalAttribute):
            values = attribute.value_iterator()

            # Append the mapping structure to the one-hot map
            one_hot_map.add_encoding(attribute_index, onehot.Encoding(values, float))

    # Return the map
    return one_hot_map


def one_hot_encode_attributes(attributes: List[Attribute], one_hot_map: onehot.Mapping) -> List[Attribute]:
    """
    Uses the one-hot encoding map to modify the given attribute list into its
    one-hot encoded form.

    :param attributes:      The attributes to encode.
    :param one_hot_map:     The one-hot encoding map to use for the encoding.
    :return:                The encoded list of attributes.
    """

    attribute_names = [attribute.name for attribute in attributes]
    attribute_lookup = {attribute.name: attribute for attribute in attributes}

    new_names = one_hot_map.encode_header(attribute_names)

    for name in new_names:
        if name not in attribute_lookup:
            attribute_lookup[name] = NumericAttribute(name)

    return [attribute_lookup[name] for name in new_names]
