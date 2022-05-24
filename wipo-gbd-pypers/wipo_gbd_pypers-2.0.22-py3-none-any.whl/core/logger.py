"""
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """

from pypers.core.interfaces import db
from inspect import getframeinfo, stack


class Logger:

    # Expose logging levels

    types = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

    def __init__(self, run_id, collection, step_name, sub_step,
                 caller_name='pypers'):
        """
        Standard configuration for the logging service
        """
        self.run_id = run_id
        self.collection = collection
        self.step_name = step_name
        self.sub_step = sub_step
        self.db_logger = db.get_db_logger()
        self.caller_name = caller_name
        for type in self.types:
            setattr(self, type.lower(), self.build_logging_types(type))

    def build_logging_types(self, type_log):
        def func1(message, *args, **kwargs):
            caller = getframeinfo(stack()[1][0])
            line = caller.lineno
            fname = caller.filename.split('/')
            fname = '/'.join(fname[fname.index(self.caller_name):])
            self.db_logger.log_entry(self.run_id, self.collection, message,
                                     step=self.step_name,
                                     sub_step=self.sub_step,
                                     file=fname,
                                     position=line,
                                     type_log=type_log,
                                     reset=kwargs.get('reset', False))
        func1.__name__ = type_log.lower()
        return func1
