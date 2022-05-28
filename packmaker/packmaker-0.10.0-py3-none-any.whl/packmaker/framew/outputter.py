# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from itertools import compress

import operator
import sys

from .baseobject import BaseObject
from .config import InvalidCommandlineArgument
from .formatter import CSVFormatter, TableFormatter, JSONFormatter, YAMLFormatter, ValueFormatter, ShellFormatter

##############################################################################


class BaseOutputter (BaseObject):

    formatters = {}
    formatter_default = None

    def add_argument_group(self, parser):
        formatter_group = parser.add_argument_group(title='output formatter',
                                                    description='output formatter options')
        self._formatter_group = formatter_group
        fchoices = sorted(self.formatters.keys())
        fdefault = self.formatter_default
        if fdefault not in fchoices:
            fdefault = fchoices[0]

        formatter_group.add_argument('-f', '--format',
                                     dest='formatter',
                                     action='store',
                                     choices=fchoices,
                                     default=fdefault,
                                     help='the output format, defaults to %s' % fdefault)
        formatter_group.add_argument('-c', '--column',
                                     action='append',
                                     default=[],
                                     dest='columns',
                                     metavar='COLUMNS',
                                     help='specify the column(s) to include, can be repeated')

        for formatter in self.formatters.values():
            f = formatter()
            f.add_argument_group(parser)
        return parser

    def output(self, arguments, column_names, data):
        self.formatter = self.formatters[arguments.formatter]()
        self.produce_output(arguments, column_names, data)

    def produce_output(self, arguments, column_names, data):
        pass

    def _generate_columns_and_selector(self, arguments, column_names):
        if not arguments.columns:
            columns_to_include = column_names
            selector = None
        else:
            columns_to_include = [c for c in column_names if c in arguments.columns]
            if not columns_to_include:
                raise InvalidCommandlineArgument('No recognized column names in %s. Recognized columns are %s.'
                                                 % (str(arguments.columns), str(column_names)))

            selector = [(c in columns_to_include) for c in column_names]
        return columns_to_include, selector

    @staticmethod
    def _compress_iterable(iterable, selectors):
        return compress(iterable, selectors)

##############################################################################


class ListOutputter (BaseOutputter):

    formatters = {'table': TableFormatter,
                  'csv': CSVFormatter,
                  'json': JSONFormatter,
                  'yaml': YAMLFormatter,
                  'value': ValueFormatter,
                  }

    formatter_default = 'table'

    def add_argument_group(self, parser):
        parser = super(ListOutputter, self).add_argument_group(parser)
        group = self._formatter_group
        group.add_argument('--sort-column',
                           action='append',
                           default=[],
                           dest='sort_columns',
                           metavar='SORT_COLUMN',
                           help=("specify the column(s) to sort the data (columns specified "
                                 "first have a priority, non-existing columns are ignored), "
                                 "can be repeated"))
        return parser

    def produce_output(self, arguments, column_names, data):
        if arguments.sort_columns:
            indexes = [column_names.index(c) for c in arguments.sort_columns if c in column_names]
            if indexes:
                data = sorted(data, key=operator.itemgetter(*indexes))
        (columns_to_include, selector) = self._generate_columns_and_selector(arguments, column_names)
        if selector:
            data = (list(self._compress_iterable(row, selector)) for row in data)

        formatter = self.formatters[arguments.formatter]()
        formatter.emit_list(columns_to_include, data, sys.stdout, arguments)

##############################################################################


class SingleOutputter (BaseOutputter):

    formatters = {'table': TableFormatter,
                  'json': JSONFormatter,
                  'shell': ShellFormatter,
                  'yaml': YAMLFormatter,
                  'value': ValueFormatter,
                  }

    formatter_default = 'table'

    def produce_output(self, arguments, column_names, data):
        (columns_to_include, selector) = self._generate_columns_and_selector(arguments, column_names)
        if selector:
            data = list(self._compress_iterable(data, selector))

        formatter = self.formatters[arguments.formatter]()
        formatter.emit_one(columns_to_include, data, sys.stdout, arguments)

##############################################################################
# THE END
