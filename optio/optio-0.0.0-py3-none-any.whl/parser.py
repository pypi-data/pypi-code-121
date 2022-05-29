#!/usr/bin/env python3


from __future__ import annotations
from collections import deque
import re
from .option import Option


class Parser:
    """!
    @brief Central parsing object configured by Option instance.
    """

    def __init__(self, options: list[Option] = []) -> Parser:
        """!
        @brief Parser constructor creates instances of a Parser and verifies
            passed Options (duplicates, etc.).
        """

        self.__options = []
        self.__plain_args = []

        for option in options:
            self.add_option(option)

    def __str__(self):
        """!
        @brief Overloaded str(...) magic method.
        """

        return "Parser " + " ".join(list(map(str, self.__options))) + "."

    def options(self) -> list[Option]:
        """!
        Returns list of all defined Options.
        """

        return self.__options

    def plain_args(self) -> list[str]:
        """!
        Returns list of all found plain arguments.
        """

        return self.__plain_args

    def add_option(self, in_opt: Option) -> Parser:
        """!
        @brief Adds option one-by-one, verifies new Option against already
            added Options (duplicates, etc.).

        @note Returning @b self allows chaining, e.g.
            @code{.py}
            p = Parser().add_option(Opt).add_option(Opt)
            @endcode
        """

        for opt in self.__options:
            for view in in_opt.views():
                if (view in opt.views()):
                    raise RuntimeError("View " + view + " conflicts with already defined option.")

        self.__options.append(in_opt)
        return self

    def try_get_option(self, view: str) -> any[Option, None]:
        """!
        @return Option if has a view, otherwise None.
        """

        for option in self.__options:
            if (option.has_view(view)):
                return option

        return None

    def parse_args(self, args: any[str, list], conflicts: list[set[str]] = []) -> Parser:
        """!
        @brief Parse arguments and returns argument structure. Any deviations
            from the expected option configuration are reported via exceptions.

        @note Arguments can appear in the following formats.
            - short views:
                - single, -h
                - with (multiple) parameters, -h 1 2 3
                - sequence with parameters, -hAf 1 2 3 means -h -A -f 1 2 3
            - long views:
                - single, --help
                - with (multiple) parameters, --memset 512Mb 10Mb
        """

        for opt in self.__options:
            opt.reset()

        for i in range(len(conflicts)):
            conflicts[i] = [ [ item, False ] for item in conflicts[i] ]

        # convert string to list of tokens, remove empty ""
        if (isinstance(args, str)):
            args = [ word for word in re.split(r"[ \r\t\n]+", args) if word != "" ]

        args = deque(args)

        only_plain_args = False

        # starts with ./example file.txt -x -> all are plain args
        if (len(args) > 0 and not args[0].startswith("-")):
            only_plain_args = True

        # process arguments one by one
        while args:
            arg = args.popleft()

            if only_plain_args:
                self.__plain_args.append(arg)

            elif arg == "--":
                only_plain_args = True

            else:
                params = []

                if Option.is_single_short_view(arg) or Option.is_single_long_view(arg):

                    # collect parameters
                    while args and not args[0].startswith("-"):
                        params.append(args.popleft())

                    # find corresponding option and accept
                    opt = self.try_get_option(arg)

                    if opt == None:
                        raise ValueError("Encountered option " + arg + " is not defined.")

                    opt.accept(params)

                elif Option.is_multiple_short_views(arg):

                    # cut first '-', reverse, and push single options
                    for char in arg[1:][::-1]:
                        args.appendleft("-" + char)

                else:
                    raise ValueError("Bad view " + arg + ".")

        # options check if in good state
        for opt in self.__options:
            opt.self_check()

        for opt in self.__options:
            for conflict in conflicts:
                for item in conflict:
                    if opt.has_view(item[0]) and opt.found():
                        item[1] = True

        for conflict in conflicts:
            result = True
            for item in conflict:
                result = result and item[1]
            if result:
                raise ValueError("Arguments are in conflict " + str(conflict))

        return self
