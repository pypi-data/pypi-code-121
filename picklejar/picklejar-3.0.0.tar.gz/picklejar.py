# coding=utf-8
"""PickleJar is a python module that allows you to work with multiple pickles inside a single file (I call it a "jar")!
"""
# Copyright (C) 2015-2022 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import os
import dill
from typing import Any


class Jar:
    """A file containing multiple pickle objects

    :param filepath: Path to the file
    :type filepath: str, required
    :return: None
    :rtype: None
    """
    def __init__(self, filepath: str) -> None:
        self.jar = os.path.abspath(os.path.expanduser(filepath))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def exists(self) -> bool:
        """Does the Jar exist

        :return: True or False
        :rtype: bool
        """
        return os.path.exists(self.jar)

    def remove(self) -> bool:
        """Remove the current jar file if it exists

        :return: True
        :rtype: bool
        """
        if self.__exists():
            os.remove(self.jar)
        return True

    def load(self, always_list: bool = False) -> Any:
        """Loads all the pickles out of the file/jar

        :param always_list: Ensure that Jars with single pickle return as a list (Default: False)
        :type always_list: bool, optional
        :return: List of de-pickled objects or de-pickled object if always_list is False and pickled object is not list
        :rtype: Any
        :raises: IOError
        """
        items = list()
        if self.__exists() is False:
            raise IOError('File does not exist: ' + self.jar)
        with open(self.jar, 'rb') as jar:
            while True:
                try:
                    items.append(dill.load(jar))
                except EOFError:
                    break
        if len(items) == 1:
            if always_list:
                return items
            else:
                return items[0]
        else:
            return items

    def dump(self, items: Any, new_jar: bool = False, collapse: bool = False) -> bool:
        """Write a Pickle to the file/jar.

        :param items: Item or list of items to pickle
        :type items: Any
        :param new_jar: Start a new jar (Default: False)
        :type new_jar: bool, optional
        :param collapse: If items is a list write list as single pickle
        :return: True on file write
        :rtype: bool
        """
        if new_jar:
            writemode = 'wb'
        else:
            writemode = 'ab'
        with open(self.jar, writemode) as jar:
            if collapse:
                dill.dump(items, jar, dill.HIGHEST_PROTOCOL)
            else:
                if type(items) is list:
                    for item in items:
                        dill.dump(item, jar, dill.HIGHEST_PROTOCOL)
                else:
                    dill.dump(items, jar, dill.HIGHEST_PROTOCOL)
        return True

    # Protecting internal calls
    __exists = exists
    __remove = remove
    __load = load
    __dump = dump
