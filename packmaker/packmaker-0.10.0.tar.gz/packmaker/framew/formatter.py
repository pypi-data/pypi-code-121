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

__all__ = ['CSVFormatter', 'TableFormatter', ]

import argparse
import csv
import json
import os
import prettytable
import yaml

from .baseobject import BaseObject

##############################################################################


class BaseFormatter (BaseObject):
    def add_argument_group(self, parser):
        pass


class ListFormatter (BaseFormatter):
    def emit_list(self, column_names, data, stdout, arguments):
        pass


class SingleFormatter (BaseFormatter):
    def emit_one(self, column_names, data, stdout, arguments):
        pass

##############################################################################


class CSVFormatter (ListFormatter):

    QUOTE_MODES = {'all': csv.QUOTE_ALL,
                   'minimal': csv.QUOTE_MINIMAL,
                   'nonnumeric': csv.QUOTE_NONNUMERIC,
                   'none': csv.QUOTE_NONE
                   }

    def add_argument_group(self, parser):
        group = parser.add_argument_group('CSV formatter')
        group.add_argument('--quote',
                           choices=sorted(self.QUOTE_MODES.keys()),
                           dest='quote_mode',
                           default='nonnumeric',
                           help='when to include quotes, default to nonnumeric')

    def emit_list(self, column_names, data, stdout, arguments):
        writer_kwargs = dict(quoting=self.QUOTE_MODES[arguments.quote_mode],
                             lineterminator=os.linesep,
                             escapechar='\\')

        writer = csv.writer(stdout, **writer_kwargs)
        writer.writerow(column_names)
        for row in data:
            writer.writerow([c for c in row])

##############################################################################


class TableFormatter (ListFormatter, SingleFormatter):

    ALIGNMENTS = {int: 'r',
                  str: 'l',
                  float: 'r'
                  }
    try:
        ALIGNMENTS[unicode] = 'l'
    except NameError:
        pass

    def add_argument_group(self, parser):
        group = parser.add_argument_group('Table formatter')
        group.add_argument('--max-width',
                           metavar='<integer>',
                           default=int(os.environ.get('MAX_TERM_WIDTH', 0)),
                           type=int,
                           help=('maximum display width, <1 to disable. You cal also '
                                 'use the MAX_DISPLAY_WIDTH environment variable, '
                                 'but the parameter takes precedence.'))
        group.add_argument('--fit-width',
                           action='store_true',
                           default=bool(int(os.environ.get('FIT_WIDTH', 0))),
                           help=('Fit the table to the display width. '
                                 'Implied if --max-width greater than 0. '
                                 'Set the environment variable FIT_WIDTH=1 '
                                 'to always enable'))
        group.add_argument('--print-empty',
                           action='store_true',
                           help='Print empty table iof there is no data to show.')

    def emit_list(self, column_names, data, stdout, arguments):
        x = prettytable.PrettyTable(column_names, print_empty=arguments.print_empty)
        x.padding_width = 1

        if data:
            self.add_rows(x, column_names, data)

        min_width = 0
        self._assign_max_widths(stdout, x, int(arguments.max_width), min_width, arguments.fit_width)

        formatted = x.get_string()
        stdout.write(formatted)
        stdout.write('\n')

    def emit_one(self, column_names, data, stdout, arguments):
        x = prettytable.PrettyTable(field_names=('Field', 'Value'),
                                    print_empty=False)
        x.padding_width = 1
        x.align['Field'] = 'l'
        x.align['Value'] = 'l'
        for name, value in zip(column_names, data):
            x.add_row(self._format_row((name, value)))

        min_width = 16
        self._assign_max_widths(stdout, x, int(arguments.max_width), min_width, arguments.fit_width)

        formatted = x.get_string()
        stdout.write(formatted)
        stdout.write('\n')

    def add_rows(self, table, column_names, data):
        data_iter = iter(data)
        try:
            first_row = next(data_iter)
        except StopIteration:
            pass
        else:
            for value, name in zip(first_row, column_names):
                alignment = self.ALIGNMENTS.get(type(value), 'l')
                table.align[name] = alignment
            table.add_row(self._format_row(first_row))
            for row in data_iter:
                table.add_row(self._format_row(row))

    @staticmethod
    def _assign_max_widths(stdout, x, max_width, min_width=0, fit_width=False):
        pass

    @staticmethod
    def _format_row(row):
        new_row = []
        for r in row:
            new_row.append(r)
        return new_row

##############################################################################


class JSONFormatter (ListFormatter, SingleFormatter):

    def add_argument_group(self, parser):
        group = parser.add_argument_group(title='json formatter')
        group.add_argument('--noindent',
                           action='store_true',
                           dest='noindent',
                           help='whether to disable indenting the JSON')

    def emit_list(self, column_names, data, stdout, arguments):
        items = []
        for item in data:
            items.append({n: (i) for n, i in zip(column_names, item)})
        indent = None if arguments.noindent else 2
        json.dump(items, stdout, indent=indent)
        stdout.write('\n')

    def emit_one(self, column_names, data, stdout, arguments):
        one = {n: (i) for n, i in zip(column_names, data)}
        indent = None if arguments.noindent else 2
        json.dump(one, stdout, indent=indent)
        stdout.write('\n')

##############################################################################


class ShellFormatter (SingleFormatter):

    def add_argument_group(self, parser):
        group = parser.add_argument_group(title='shell formatter',
                                          description='a format a UNIX shell can parse (variable="value")')
        group.add_argument('--variable',
                           action='append',
                           default=[],
                           dest='variables',
                           metavar='VARIABLE',
                           help=argparse.SUPPRESS)
        group.add_argument('--prefix',
                           action='store',
                           default='',
                           dest='prefix',
                           help='add a prefix to all variable names')

    def emit_one(self, column_names, data, stdout, arguments):
        variable_names = [c.lower().replace(' ', '_') for c in column_names]
        desired_columns = arguments.variables
        for name, value in zip(variable_names, data):
            if name in desired_columns or not desired_columns:
                value = str(value)
                value = value.replace('"', '\\"')
                name = name.replace(':', '_')
                name = name.replace('-', '_')

                stdout.write('%s%s="%s"\n' % (arguments.prefix, name, value))

##############################################################################


class ValueFormatter (ListFormatter, SingleFormatter):

    def emit_list(self, column_names, data, stdout, arguments):
        for row in data:
            stdout.write(' '.join(str(c) for c in row) + u'\n')

    def emit_one(self, column_names, data, stdout, arguments):
        for value in data:
            stdout.write('%s\n' % value)

##############################################################################


class YAMLFormatter (ListFormatter, SingleFormatter):

    def emit_list(self, column_names, data, stdout, arguments):
        items = []
        for item in data:
            items.append({n: (i) for n, i in zip(column_names, item)})
        yaml.safe_dump(items, stream=stdout, default_flow_style=False)

    def emit_one(self, column_names, data, stdout, arguments):
        for key, value in zip(column_names, data):
            dict_data = {key: (value)}
            yaml.safe_dump(dict_data, stream=stdout, default_flow_style=False)

##############################################################################
# THE END
