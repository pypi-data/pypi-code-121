from argparse import ArgumentParser
from typing import Type

from ..options import Option
from .._ArgumentParserConfigurer import ArgumentParserConfigurer
from .._OptionHandler import OptionHandler
from ._OptionContext import OptionContext


class OptionClassContext(OptionContext, ArgumentParserConfigurer):
    """
    Class which handles accessing an option in the context of
    a specific class.
    """
    def __init__(self, option: Option, context: Type[OptionHandler]):
        # The option must be owned by the context type (or super-type)
        if not issubclass(context, option.owner):
            raise TypeError("Context type does not have access to this option")

        super().__init__(option, context)

    def configure_parser(self, parser: ArgumentParser):
        # Get the kwargs from the option
        kwargs = dict(self._option.kwargs)

        # Get our help text from the owner if we don't have it already
        if "help" not in kwargs:
            help = self._context.get_help_text_for_option(self._option)
            if help is not None:
                kwargs["help"] = help

        parser.add_argument(*self._option.flags, dest=self._option.name, **kwargs)
