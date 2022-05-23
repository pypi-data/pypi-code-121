class Encoding:
    """
    Class representing the one-hot encoding for a single set of strings.
    Typically represents one (source) column in a dataset.
    """
    def __init__(self, strings, numeric_type=int):
        # Set the numeric type
        self.__numeric_type = numeric_type

        # Create the lookup tables
        self.__lookup = {}
        self.__reverse_lookup = []

        # Add each unique string to the lookups
        for string in strings:
            if string not in self.__lookup:
                self.__lookup[string] = len(self.__lookup)
                self.__reverse_lookup.append(string)

        # Reset the internal encoding table
        self.__reset_encodings()

    def __reset_encodings(self):
        """
        Resets the internal encoding table cache to the empty state.
        Required when encoding state changes (e.g. numeric type).
        """
        self.__encodings = [None] * self.size()

    def set_numeric_type(self, numeric_type):
        """
        Sets the numeric type to use for encoded values.

        :param numeric_type:    The numeric type to use.
        """
        if numeric_type != self.__numeric_type and numeric_type is not None:
            self.__numeric_type = numeric_type
            self.__reset_encodings()

    def get_index(self, string):
        """
        Gets the encoded index for the given string.

        :param string:  The string to look up.
        :return:        The encoded index of the string.
        """

        # If the string is not encoded, return None
        if string not in self.__lookup:
            return None

        # Return the encoded index
        return self.__lookup[string]

    def get_string(self, index):
        """
        Returns the string that corresponds to the given encoded index.

        :param index:   The index to decode.
        :return:        The string that was encoded to the given index.
        """
        return self.__reverse_lookup[index]

    def get_encoding(self, string):
        """
        Gets the encoded array for the given string.

        :param string:  The string to encode.
        :return:        The encoded list, with a 1 at the encoded index and zeroes
                        everywhere else.
        """

        # Get the encoded index of the string
        index = self.get_index(string)

        # If the string wasn't encoded, abort
        if index is None:
            return None

        # If the encodings cache doesn't have an entry for this string, create it
        if self.__encodings[index] is None:
            self.__encodings[index] = create_encoded_array(index, self.size(), self.__numeric_type)

        # Return the encoding
        return self.__encodings[index]

    def encode_column(self, column):
        """
        Encodes an entire column of strings.

        :param column:  The list of strings to encode.
        :return:        A list of encodings.
        """
        return [self.get_encoding(string) for string in column]

    def get_header_names(self, prefix):
        """
        Gets a list of header names for the set of encoded columns produced
        by the given column name.

        :param prefix:  The name of the column being encoded.
        :return:        The list of column names produced by the encoding.
        """
        return [prefix + '_' + string for string in self.__reverse_lookup]

    def size(self):
        """
        Gets the number of encoded strings in this encoding.

        :return:    The number of encoded strings.
        """
        return len(self)

    def __len__(self):
        return len(self.__lookup)


class Mapping:
    """
    Class representing a collection of encodings, one for each column of a
    dataset. The entry for a particular column may be None, indicating that it
    should not be encoded.
    """
    def __init__(self, num_columns):
        # Create the empty collection of encodings
        self.__mapping = [None] * num_columns

    def add_encoding(self, column, encoding):
        """
        Adds an encoding to the collection at the specified index.

        :param column:      The column index of the encoded column.
        :param encoding:    The encoding.
        """
        self.__mapping[column] = encoding

    def encode_header(self, header):
        """
        Applies the encodings to the column names of a dataset.

        :param header:  The list of column names before encoding.
        :return:        The list of column names after encoding.
        """

        # Create the resultant list of column names
        encoded_header = []

        # Append each group of new column names
        for i, name in enumerate(header):
            if self.__mapping[i] is not None:
                for new_name in self.__mapping[i].get_header_names(name):
                    encoded_header.append(new_name)
            else:
                encoded_header.append(name)

        # Return the new column names
        return encoded_header

    def encode_column_selection(self, selection):
        """
        Applies the encodings to a list of selected column indices.

        :param selection:   The list of selected column indices.
        :return:            The encoded list of selected column indices.
        """

        # Create an accumulated list of encoded column lengths
        cumulative_lengths = [0]
        for i in range(0, len(self)):
            length = 1 if self.__mapping[i] is None else len(self.__mapping[i])
            cumulative_lengths.append(cumulative_lengths[i] + length)

        # Initialise the output
        output = []

        # For each selected index, add all of the indices between the accumulated
        # lengths (i.e. the range of encoded indices)
        for index in selection:
            for i in range(cumulative_lengths[index], cumulative_lengths[index + 1]):
                output.append(i)

        # Return the result
        return output

    def encode(self, data, row_major=True):
        """
        Encodes a dataset with the current encodings.

        :param data:        The dataset (a list of either rows or columns).
        :param row_major:   The data order.
        :return:            Nothing, the data is encoded in place.
        """
        if row_major:
            for row in data:
                self.encode_row(row)
        else:
            for i, column in enumerate(data):
                self.__mapping[i].encode_column(column)

    def encode_row(self, row):
        """
        Encodes a single row of data using the current set of encodings.

        :param row:     The row to encode.
        :return:        Nothing, the row is encoded in place.
        """

        # Process the row from last to first (to preserve indices after insertion)
        for i in reversed(range(len(row))):
            # Can skip non-encoded values
            if self.__mapping[i] is None:
                continue

            # Remove the string value
            value = row.pop(i)

            # Get the encoding from the map
            encoded_value = self.__mapping[i].get_encoding(value)

            # Insert the encoding into the data
            for j in reversed(range(len(encoded_value))):
                row.insert(i, encoded_value[j])

    def __len__(self):
        return len(self.__mapping)


def create_encoded_array(index, size, numeric_type=int):
    """
    Creates a one-hot encoded array with a one at the given index
    and zeroes everywhere else, up to the given size.

    :param index:           The index to set to one.
    :param size:            The size of the encoded array.
    :param numeric_type:    The numeric type for the values in the array.
    :return:        The one-hot encoding for the given parameters.
    """

    # Create the empty encoded value
    encoded_value = [numeric_type(0)] * size

    # Set the requested index to 1
    encoded_value[index] = numeric_type(1)

    # Return the encoded value
    return encoded_value
