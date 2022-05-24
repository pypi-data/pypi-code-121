from argparse import Namespace
from typing import Union, Any

from .options import Option
from ._OptionHandler import OptionHandler
from ._typing import OptionsList


class OptionValueHandler(OptionHandler):
    """
    Base class for classes which handle options and their values.
    """
    @property
    def namespace(self) -> Namespace:
        """
        Gets the namespace that holds this handler's values.

        :return:    The namespace.
        """
        raise NotImplementedError("OptionValueHandler.namespace")

    def get_option_value(self, option: Union[str, Option]) -> Any:
        """
        Gets the current value for an option.

        :param option:  The option, by name or reference.
        :return:        The option's value.
        """
        # Convert option names to their descriptors
        if isinstance(option, str):
            option = self._get_option(option)

        # Get the value from the namespace by name
        return option.__get__(self, type(self))

    def set_option_value(self, option: Union[str, Option], value: Any):
        """
        Sets the current value for an option.

        :param option:  The option, by name or reference.
        :param value:   The value to set.
        """
        # Convert option names to their descriptors
        if isinstance(option, str):
            option = self._get_option(option)

        # Get the value from the namespace by name
        return option.__set__(self, value)

    def to_options_list(self) -> OptionsList:
        """
        Gets the values of all options as an options-list.
        """
        options_list = []

        for option in self._get_all_options():
            options_list += option.get_as_options_list(self)

        return options_list
