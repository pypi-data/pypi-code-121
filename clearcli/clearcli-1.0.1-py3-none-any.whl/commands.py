"""
Copyright 2022
Author: Thomas Mahé <contact@tmahe.dev>

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

import abc
import argparse
import inspect


def _populate_args_handler(command_item, cli):
    if inspect.isclass(command_item):
        if ClearCliCommand in inspect.getmro(command_item):
            command_item.populate_args(cli)
        else:
            raise TypeError(f'Classes is descriptor must be of type <ClearCliCommand>, '
                            f'Found <{command_item.__name__}>')
    # Handle Lambdas
    elif command_item.__code__.co_name == "<lambda>":
        for item in inspect.signature(command_item).parameters.keys():
            cli.add_argument(item)
    else:
        raise TypeError(f'Supported types for descriptor items {{<lambda>, <ClearCliCommand>}}, '
                        f'Found <{command_item.__name__}>')


class ClearCliCommand(abc.ABC):
    _reserved_arguments = {"_CLEARCLI_CALLABLE"}

    def __init__(self, **kwargs):
        self.filtered_args = {k: kwargs.get(k) for k in set(kwargs.keys()) - self._reserved_arguments}

    @staticmethod
    @abc.abstractmethod
    def populate_args(parser: argparse.ArgumentParser):
        pass  # pragma: nocover
