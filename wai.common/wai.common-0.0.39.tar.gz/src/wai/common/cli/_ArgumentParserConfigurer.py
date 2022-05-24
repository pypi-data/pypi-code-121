from argparse import ArgumentParser

from ..meta import instanceoptionalmethod, non_default_kwargs
from .util import LoggingArgumentParser


class ArgumentParserConfigurer:
    """
    Interface for classes which can configure an argument parser.
    """
    @instanceoptionalmethod
    def configure_parser(self, parser: ArgumentParser):
        """
        Configures the parser.

        :param parser:  The parser to configure.
        """
        raise NotImplementedError(ArgumentParserConfigurer.configure_parser.__qualname__)

    @instanceoptionalmethod
    def get_configured_parser(self, *,
                              prog=...,
                              usage=...,
                              description=...,
                              epilog=...,
                              parents=...,
                              formatter_class=...,
                              prefix_chars=...,
                              fromfile_prefix_chars=...,
                              argument_default=...,
                              conflict_handler=...,
                              add_help=...,
                              allow_abbrev=...,
                              logging: bool = True) -> ArgumentParser:
        """
        Creates a configured parser.

        TODO: Parameter typing and descriptions
        TODO: Remove unsupported parameters e.g. prefix_chars
        TODO: Caching?

        :return:    The configured parser.
        """
        # Get the parser class based on the logging flag
        parser_class = LoggingArgumentParser if logging else ArgumentParser

        # Create a parser
        parser = parser_class(**non_default_kwargs(ArgumentParserConfigurer.get_configured_parser, locals()))

        # Configure it
        self.configure_parser(parser)

        return parser
