from typing import Generic, TypeVar, Type, Union, Optional, Any

import typing_inspect

# The type of the forward-direction keys for the two-way dict
FORWARD_TYPE = TypeVar("FORWARD_TYPE")

# The type of the reverse-direction keys for the two-way dict
REVERSE_TYPE = TypeVar("REVERSE_TYPE")

# Type that applies to either key
EITHER_TYPE = Union[FORWARD_TYPE, REVERSE_TYPE]


class TwoWayDict(Generic[FORWARD_TYPE, REVERSE_TYPE]):
    """
    A two-way dictionary, which can be accessed by either key or value.
    Attempts to auto-discriminate which direction a method call should be
    applied in (forward or reverse) based on the argument types. If the
    keys and values are of the same type, this must be specified explicitly
    with the method with the required suffix.
    """
    def __init__(self):
        self._forward_map = dict()
        self._reverse_map = dict()

    def forward_type(self) -> Type[FORWARD_TYPE]:
        """
        Gets the type of the forward-direction keys for this two-way dict.
        """
        return typing_inspect.get_args(self.__orig_class__)[0]

    def reverse_type(self) -> Type[REVERSE_TYPE]:
        """
        Gets the type of the reverse-direction keys for this two-way dict.
        """
        return typing_inspect.get_args(self.__orig_class__)[1]

    def matches_forward_type(self, value: Any, only: bool = False) -> bool:
        """
        Whether the type of the given key matches the forward type.

        :param value:   The key to check.
        :param only:    Whether the value is not also allowed to match the
                        reverse type.
        :return:        True if matches, False if not.
        """
        forward_type: Type[FORWARD_TYPE] = self.forward_type()

        if typing_inspect.get_origin(forward_type) is type:
            if not isinstance(value, type):
                return False
            forward_type = typing_inspect.get_args(forward_type)[0]
            check = issubclass
        else:
            check = isinstance

        matches: bool = check(value, forward_type)

        if matches and only:
            matches = matches and not self.matches_reverse_type(value)

        return matches

    def matches_reverse_type(self, value: Any, only: bool = False) -> bool:
        """
        Whether the type of the given key matches the reverse type.

        :param value:   The key to check.
        :param only:    Whether the value is not also allowed to match the
                        reverse type.
        :return:        True if matches, False if not.
        """
        reverse_type: Type[REVERSE_TYPE] = self.reverse_type()

        if typing_inspect.get_origin(reverse_type) is type:
            if not isinstance(value, type):
                return False
            reverse_type = typing_inspect.get_args(reverse_type)[0]
            check = issubclass
        else:
            check = isinstance

        matches: bool = check(value, reverse_type)

        if matches and only:
            matches = matches and not self.matches_forward_type(value)

        return matches

    def both_types_same(self) -> bool:
        """
        Returns whether the type of the forward-direction keys is the same
        as the reverse-direction keys.
        """
        return self.forward_type() is self.reverse_type()

    def set(self, key: EITHER_TYPE, value: EITHER_TYPE):
        """
        Sets an entry in this two-way dict. Automatically infers the
        direction based on key/value types.

        :param key:     The key to set.
        :param value:   The value to set against it.
        """
        return self.type_select(key, value,
                                forward_result=self.set_forward,
                                reverse_result=self.set_reverse)(key, value)

    def __setitem__(self, key: EITHER_TYPE, value: EITHER_TYPE):
        """
        Sets an entry in this two-way dict. Automatically infers the
        direction based on key/value types.

        :param key:     The key to set.
        :param value:   The value to set against it.
        """
        self.set(key, value)

    def set_forward(self, key: FORWARD_TYPE, value: REVERSE_TYPE):
        """
        Explicitly sets a mapping in the forward direction.

        :param key:     The forward-direction key.
        :param value:   The value.
        """
        if key in self._forward_map:
            self._reverse_map.pop(self._forward_map[key])

        if value in self._reverse_map:
            self._forward_map.pop(self._reverse_map[value])

        self._forward_map[key] = value
        self._reverse_map[value] = key

    def set_reverse(self, key: REVERSE_TYPE, value: FORWARD_TYPE):
        """
        Explicitly sets a mapping in the reverse direction.

        :param key:     The reverse-direction key.
        :param value:   The value.
        """
        self.set_forward(value, key)

    def get(self, key: EITHER_TYPE) -> EITHER_TYPE:
        """
        Gets the value of an entry in this two-way dict. Automatically infers the
        direction based on key type.

        :param key:     The key to get the value for.
        """
        return self.type_select(key,
                                forward_result=self.get_forward,
                                reverse_result=self.get_reverse)(key)

    def __getitem__(self, item: EITHER_TYPE) -> EITHER_TYPE:
        """
        Gets the value of an entry in this two-way dict. Automatically infers the
        direction based on key type.

        :param item:     The key to get the value for.
        """
        return self.get(item)

    def get_forward(self, key: FORWARD_TYPE) -> REVERSE_TYPE:
        """
        Explicitly gets the value of a mapping in the forward direction.

        :param key:     The forward-direction key.
        :return:        The corresponding value.
        """
        return self._forward_map[key]

    def get_reverse(self, key: REVERSE_TYPE) -> FORWARD_TYPE:
        """
        Explicitly gets the value of a mapping in the reverse direction.

        :param key:     The reverse-direction key.
        :return:        The corresponding value.
        """
        return self._reverse_map[key]

    def contains(self, key: EITHER_TYPE) -> bool:
        """
        Checks if this two-way dict contains the given key. Automatically
        infers the direction based on the key's type.

        :param key:     The key to check for.
        :return:        True if the key is in the dict, False if not.
        """
        return self.type_select(key,
                                forward_result=self.contains_forward,
                                reverse_result=self.contains_reverse)(key)

    def __contains__(self, item: EITHER_TYPE) -> bool:
        """
        Checks if this two-way dict contains the given key. Automatically
        infers the direction based on the key's type.

        :param item:    The key to check for.
        :return:        True if the key is in the dict, False if not.
        """
        return self.contains(item)

    def contains_forward(self, key: FORWARD_TYPE) -> bool:
        """
        Explicitly checks if the given key is contained in the
        dict in the forward direction.

        :param key:     The key to check for.
        :return:        True if the key is in the forward-direction of the dict,
                        False if not.
        """
        return key in self._forward_map

    def contains_reverse(self, key: REVERSE_TYPE) -> bool:
        """
        Explicitly checks if the given key is contained in the
        dict in the reverse direction.

        :param key:     The key to check for.
        :return:        True if the key is in the reverse-direction of the dict,
                        False if not.
        """
        return key in self._reverse_map

    def __iter__(self):
        """
        Iterates through all pairs of keys in the dict.
        """
        return (pair for pair in self._forward_map.items())

    def __len__(self) -> int:
        """
        The number of key-pairs in the dict.
        """
        return len(self._forward_map)

    def type_select(self, key: EITHER_TYPE, value: Optional[EITHER_TYPE] = None, *,
                    forward_result, reverse_result):
        """
        Automatically selects between a forward and reverse direction result based
        on the types of the key and value given.

        :param key:             The key.
        :param value:           The value.
        :param forward_result:  The result to return if the forward direction is inferred.
        :param reverse_result:  The result to return if the reverse direction is inferred.
        :return:                One of the two results.
        """
        if self.both_types_same():
            raise TypeError("Can't auto-differentiate direction when both types the same")

        if value is not None:
            if self.matches_forward_type(key) and self.matches_reverse_type(value):
                return forward_result
            elif self.matches_reverse_type(key) and self.matches_forward_type(value):
                return reverse_result
            else:
                raise TypeError("Key and value types do not align with dict types")
        else:
            if self.matches_forward_type(key, True):
                return forward_result
            elif self.matches_reverse_type(key, True):
                return reverse_result
            else:
                raise TypeError("Key type does not align with dict types")
