# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import functools
import sys

import pandas


class Registry(dict):
    """
    Registers functions or classes as a dict (for example to store all optimization algorithms automatically), with eventual additional information.
    """

    def __init__(self):
        super().__init__()
        self.information = {}

    def __repr__(self):  # pragma: no cover

        if not bool(self.information):
            to_print = ""
            for elements in self.keys():
                to_print += "{} \n".format(elements)
            return to_print
        else:
            df = (pandas.DataFrame.from_dict(self.information)).transpose()
            pandas.set_option("display.max_rows", None, "display.max_columns", None)
            return df.to_string()

    def to_csv(self, path):  # pragma: no cover
        if not self.information:
            with open(path, 'w') as csv_file:
                for key in self.keys():
                    csv_file.write(f'{key}\n')
        else:
            df = (pandas.DataFrame.from_dict(self.information)).transpose()
            df.to_csv(path)

    def register(self, object, name=None, info=None):
        """Decorator method for registering functions/classes"""
        if name is None:
            name = getattr(object, "__name__", object.__class__.__name__)
        else:
            name = str(name)

        self[name] = object
        if info is not None:
            assert isinstance(info, dict)
            self.information[name] = info
        return object

    def register_with_info(self, **info):
        """Decorator for registering a function/class as well as information about it"""
        return functools.partial(self.register, info=info)


def partialclass(cls, *args, **kwargs):
    """
    Partial class application of the given arguments and keywords.
    The returned object behaves like a "partial function application" on cls
    except that it is a subclass of cls. Used to create classes behaving like a given class
    but with specific init argument set.
    """

    class PartialClass(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwargs)

    return PartialClass
