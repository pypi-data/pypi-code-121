#!/usr/bin/env python3


from __future__ import annotations


class Option:
    """!
    @brief Option configurable by the user. Option is any construct received
        from the command line, which has a view (e.g. --option) beginning with
        "-" and optional parameters following after the view.

    @note Instances of this class are passed to the Parser constructor.
    """

    @classmethod
    def is_single_short_view(cls, view: str) -> bool:
        """!
        @brief Checks if passed string is a short view, e.g. -h
        """

        return len(view) == 2 and view[0] == "-" and view[1].isalpha()

    @classmethod
    def is_single_long_view(cls, view: str) -> bool:
        """!
        @brief Checks if passed string is a long view, e.g. --help
        """

        result = len(view) >= 3 and view.startswith("--") and view[2].isalpha()

        for char in view[3:]:
            result = result and char.isalnum()

        return result

    @classmethod
    def is_multiple_short_views(cls, view: str) -> bool:
        """!
        @brief Checks if passed view are multiple short views, e.g. -hAf
        """

        result = len(view) >= 3 and view[0] == "-"

        for char in view[1:]:
            result = result and char.isalpha()

        return result

    def __verify_views(self) -> None:
        """!
        @brief The function verifies short and long views.
            - The Option has at least one view.
            - @b short view is a "-" followed by a letter of English alphabet.
            - @b long view is a "--" followed by a letter of English alphabet
                followed by any sequence of alphanumeric chars.

        @return None or Exception
        """

        if (len(self.__views) == 0):
            raise ValueError("Option does not have views.")

        for view in self.__views:
            if not Option.is_single_short_view(view) and not Option.is_single_long_view(view):
                raise ValueError("Malformed view " + view + ".")

    def __verify_acceptor(self) -> None:
        """!
        @brief Enforces @b acceptor is a callable function.

        @return None or Exception
        """

        if not callable(self.__acceptor):
            raise ValueError("Acceptor shall be a callable function.")

    def __verify_required(self) -> None:
        """!
        @brief Enforces @b required to be a Boolean.
        """

        if not isinstance(self.__required, bool):
            raise ValueError("Required shall be a boolean.")

    def __verify_infos(self):
        """!
        @brief Enforces short and long informations to be Strings.
        """

        for info in [ self.__short_info, self.__long_info ]:
            if not isinstance(info, str):
                raise ValueError("Info shall be a string.")

    def __verify(self) -> None:
        """!
        @brief Applies a bunch of @b __verify_X functions on the constructor
            parameters.
        """

        funcs = [
            self.__verify_views,
            self.__verify_acceptor,
            self.__verify_required,
            self.__verify_infos
        ]

        for func in funcs:
            func()

    def __init__(self, views: set[str], acceptor: function = lambda id: id,
        required: bool = True, short_info: str = "", long_info: str = "") -> Option:
        """!
        Option constructor.
            - @b views is a set of acceptable short and long views, e.g. -h or --help.
            - @b acceptor is a function accepting Option parameters, e.g. -h 1 2 3.
                - acceptor is provided by the user of the library.
                - acceptor takes a list of parameters, verifies it and/or transform.
                - acceptor could return any Python entity, further interaction
                    with such entity is a responsibility of the user.
                - acceptor could report failed transformation via exception.
            - @b required is a Boolean flag telling if an Option shall appear
                in arguments.
            - @b short_info is a concise description of an Option.
            - @b long_info is a long piece of text describing an Option.
        """

        self.__views = views
        self.__acceptor = acceptor
        self.__required = required
        self.__short_info = short_info
        self.__long_info = long_info

        self.__params = None
        self.__found = False

        self.__verify()

    def __str__(self) -> str:
        """!
        @brief Overloaded str(...) magic method.
        """

        return "Option " + str(self.__views)

    def views(self) -> set[str]:
        """!
        @return Set of short and long views.
        """
        return self.__views

    def params(self) -> any:
        """!
        @return Any object representing accepted parameters.
        """

        return self.__params

    def required(self) -> bool:
        """!
        @return Boolean flag signalizing if Option is required.
        """

        return self.__required

    def found(self) -> bool:
        """!
        @return Boolean flag signalizing the Option is found during parsing.
        """

        return self.__found

    def short_info(self) -> str:
        """!
        @return Short information.
        """

        return self.__short_info

    def long_info(self) -> str:
        """!
        @return Long information.
        """

        return self.__long_info

    def accept(self, params: list[str]) -> None:
        """!
        @brief The method takes list of parameters and calls acceptor on it.

        @note An Option could accept only once, implies synonyms of the same
            Option could be mentioned only once.
        """

        if self.__found:
            raise ValueError("Option " + str(self) + " has already been encountered.")

        self.__found = True
        self.__params = self.__acceptor(params)
        return self

    def has_view(self, view: str) -> bool:
        """!
        @return @b True if Option is representable by the @b view parameter
            and @b False otherwise.
        """

        return view in self.__views

    def self_check(self) -> None:
        """!
        @brief Option self-check after parsing.
        """

        if self.__required and not self.__found:
            raise RuntimeError(str(self) + " is required, but not found.")

    def reset(self) -> None:
        """!
        @brief Allows repeated parsing on different arguments with the same
            structure.
        """

        self.__params = None
        self.__found = False
