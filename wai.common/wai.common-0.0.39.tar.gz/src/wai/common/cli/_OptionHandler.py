from argparse import ArgumentParser, Namespace
from typing import Type, Iterator, Union, Optional

from .options import Option
from ._ArgumentParserConfigurer import ArgumentParserConfigurer
from ._typing import OptionsList, is_options_list


class OptionHandler(ArgumentParserConfigurer):
    """
    Super class for option-handling classes.
    """
    @classmethod
    def configure_parser(cls, parser: ArgumentParser):
        from .context import OptionClassContext

        # Configure the parser with each option
        for option in cls._get_all_options():
            OptionClassContext(option, cls).configure_parser(parser)

    @classmethod
    def get_all_options(cls) -> Iterator[str]:
        """
        Gets the names of all options on this class.

        :return:    An iterator of option names.
        """
        return (option.name for option in cls._get_all_options())

    @classmethod
    def get_common_options(cls, other: Type['OptionHandler']) -> Iterator[str]:
        """
        Gets the options common to this handler and another.

        :param other:   The other option handler.
        :return:        The set of common option names.
        """
        # Get the other's options, keyed by name
        other_options = {option.name: option for option in other._get_all_options()}

        # Return all option names which refer to identical options
        return (option.name
                for option in cls._get_all_options()
                if option.name in other_options
                and other_options[option.name] == option)

    @classmethod
    def get_help_text_for_option(cls, option: Option) -> Optional[str]:
        """
        Allows the help text for options to be set by the owning
        class.

        :param option:  The option to get the help text for.
        :return:        The help text for the option,
                        or None if not provided.
        """
        return None

    @classmethod
    def _get_all_options(cls) -> Iterator[Option]:
        """
        Gets all options for this option handler.

        :return:    An iterator over the options.
        """
        for name in dir(cls):
            # Option names can't start with underscores
            if name.startswith("_"):
                continue

            # Get the attribute
            obj = getattr(cls, name)

            # If it's an option descriptor, yield it
            if isinstance(obj, Option):
                yield obj

    @classmethod
    def _get_option(cls, name: str) -> Option:
        """
        Gets an option by name.

        :param name:    The option's name.
        :return:        The option.
        """
        # Get the attribute
        attr = getattr(cls, name, None)

        # Make sure it is an option
        if not isinstance(attr, Option):
            raise NameError(f"Class '{cls.__qualname__}' has no option '{name}'")

        return attr

    @classmethod
    def _ensure_namespace(cls, namespace: Union[Namespace, OptionsList, None] = None) -> Namespace:
        """
        Helper method which takes a namespace or an options list
        and returns a namespace. If None is provided, uses
        sys.argv.

        :param namespace:   The namespace or options list.
        :return:            The namespace.
        """
        # If already a namespace, return it
        if isinstance(namespace, Namespace):
            return namespace

        # Must be an options list if not a namespace
        if namespace is not None and not is_options_list(namespace):
            raise TypeError(f"{namespace} is not a Namespace or an options list")

        # Parse the options list (uses sys.argv if namespace is None)
        try:
            return cls.get_configured_parser().parse_args(namespace)
        except SystemExit as e:
            raise ValueError("Error parsing options list") from e
