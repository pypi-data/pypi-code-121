import json


class ParamStoreResult:
    """Encapsulates the value of a key.

    Provides helper methods to transform values.
    """

    def __init__(self, key, value, store):
        """Initializes the class with a key/value pair.

        Args:
            key: The key.
            value: The value.
        """
        self._key = key
        self._value = value
        self._store = store

    @property
    def key(self):
        """Gets the key."""
        return self._key

    @property
    def value(self):
        """Gets the value."""
        return self._value

    @property
    def store(self):
        """Gets the the key/value store name this instance was retrieved from."""
        return self._store

    def to_int(self):
        """Parses the value into an integer.

        Returns:
            The value as an integer or None
        """
        if isinstance(self.value, int):
            return self.value
        elif self.value is not None and str(self.value).strip() == '':
            return None
        elif self.value is not None:
            return int(self.value)

    def to_float(self):
        """Parses the value into a float.

        Returns:
            The value as a float or None
        """
        if isinstance(self.value, float):
            return self.value
        elif self.value is not None and str(self.value).strip() == '':
            return None
        elif self.value is not None:
            return float(self.value)

    def to_bool(self, true_values=['true', 't', '1']):
        """Parses the value into a boolean.

        Args:
            true_values: List of string values that evaluate to True. These are case insensitive.

        Returns:
            The value as a boolean or None
        """
        if isinstance(self.value, bool):
            return self.value
        elif self.value is None:
            return False
        else:
            bool_value = str(self.value).strip().lower()
            return bool_value in map(str.lower, true_values)

    def to_list(self, delimiter=','):
        """Parses the value into a list.

        Args:
            delimiter: The delimiter to split the value on.

        Returns:
            A list with any empty values removed.
        """
        if self.value:
            values = self.value.split(delimiter)
            return [v.strip() for v in values if v and v.strip()]
        return []

    def to_json(self):
        """Parses the value into a Python object from a JSON string.

        A value of None or an empty string will not be parsed and will return None.

        Returns:
            Python object or None.
        """
        if self.value is None or (isinstance(self.value, str) and len(self.value.strip()) == 0):
            return None
        else:
            return json.loads(self.value)

