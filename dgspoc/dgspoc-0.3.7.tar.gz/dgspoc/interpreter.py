"""Module containing the logic for describe-get-system to interpret
user describing problem"""


import re
import operator
# import yaml
from datetime import datetime

from textwrap import indent
from textwrap import dedent
from textwrap import wrap

from dgspoc.utils import DotObject
from dgspoc.utils import Misc
# from dgspoc.utils import File
# from dgspoc.utils import Text

from dgspoc.constant import FWTYPE

# from dgspoc import parser
from dgspoc.parser import ParsedOperation
from dgspoc.parser import CheckStatement

from dgspoc.exceptions import NotImplementedFrameworkError
from dgspoc.exceptions import ComparisonOperatorError
from dgspoc.exceptions import ConnectDeviceStatementError
from dgspoc.exceptions import DisconnectDeviceStatementError
from dgspoc.exceptions import ReleaseDeviceStatementError
from dgspoc.exceptions import WaitForStatementError
from dgspoc.exceptions import PerformerStatementError
from dgspoc.exceptions import VerificationStatementError

from dgspoc.exceptions import ScriptBuilderError


class ScriptInfo(DotObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices_vars = dict()
        self._enabled_testing = False

    @property
    def is_testing_enabled(self):
        return self._enabled_testing

    def enable_testing(self):
        self._enabled_testing = True

    def disable_testing(self):
        self._enabled_testing = False

    def get_class_name(self):   # noqa
        return 'TestClass'

    def reset_devices_vars(self):
        self.devices_vars = dict()

    def get_device_var(self, device_name):

        for var_name, var_val in self.devices_vars.items():
            if var_val == device_name:
                return var_name
        else:
            return 'NOT_FOUND_VARIABLE_%s' % device_name


SCRIPTINFO = ScriptInfo()


class Statement:
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):

        self.is_logger = is_logger
        self.data = data
        self.prev = None
        self.next = None
        self.current = None
        self.parent = parent
        self.framework = str(framework).strip()
        self._children = []
        self._name = ''
        self._is_parsed = False

        self._stmt_data = ''
        self._remaining_data = ''

        self._prev_spacers = ''
        self._spacers = ''
        self._level = 0
        self.indentation = indentation

        self.spacer_pattern = r'(?P<spacers> *)[^ ].*'

        self.validate_framework()
        self.prepare()

    def __len__(self):
        return 1 if self.name != '' else 0

    @property
    def is_parsed(self):
        return self._is_parsed

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def children(self):
        return self._children

    @property
    def level(self):
        return self._level

    @property
    def is_unittest(self):
        return self.framework == FWTYPE.UNITTEST

    @property
    def is_pytest(self):
        return self.framework == FWTYPE.PYTEST

    @property
    def is_robotframework(self):
        return self.framework == FWTYPE.ROBOTFRAMEWORK

    @property
    def is_not_robotframework(self):
        return not self.is_robotframework

    @property
    def is_empty(self):
        return self.data.strip() == ''

    @property
    def is_statement(self):
        return self._name != ''

    @property
    def statement_data(self):
        return self._stmt_data

    @property
    def remaining_data(self):
        return self._remaining_data

    @property
    def is_setup_statement(self):
        pattern = r'setup *$'
        is_matched = self.is_matched_statement(pattern)
        return is_matched

    @property
    def is_teardown_statement(self):
        pattern = r'teardown *$'
        is_matched = self.is_matched_statement(pattern)
        return is_matched

    @property
    def is_setup_or_teardown_statement(self):
        return self.is_setup_statement or self.is_teardown_statement

    @property
    def is_parent_setup_or_teardown_statement(self):
        chk = isinstance(self.parent, (SetupStatement, TeardownStatement))
        return chk

    @property
    def is_ancestor_setup_or_teardown_for_unittest(self):
        if not self.is_unittest or not self.parent:
            return False

        node = self.parent

        while isinstance(node, Statement):
            if node.is_setup_or_teardown_statement:
                return True
            node = node.parent
        return False

    @property
    def is_ancestor_base_statement(self):
        if not self.parent:
            return False

        chk_lst = (SetupStatement, SectionStatement, TeardownStatement)

        node = self.parent

        while isinstance(node, Statement):
            if isinstance(node, chk_lst):
                return True
            node = node.parent
        return False

    @property
    def is_ancestor_section_statement(self):
        if not self.parent:
            return False

        node = self.parent

        while isinstance(node, Statement):
            if isinstance(node, SectionStatement):
                return True
            node = node.parent
        return False

    @property
    def is_ancestor_setup_statement(self):
        if not self.parent:
            return False

        if isinstance(self.parent, SetupStatement):
            return True

        node = self.parent

        while isinstance(node, Statement):
            if isinstance(node, SetupStatement):
                return True
            node = node.parent
        return False

    @property
    def is_ancestor_teardown_statement(self):
        if not self.parent:
            return False

        if isinstance(self.parent, TeardownStatement):
            return True

        node = self.parent

        while isinstance(node, Statement):
            if isinstance(node, TeardownStatement):
                return True
            node = node.parent
        return False

    @property
    def is_section_statement(self):
        pattern = r'section'
        is_matched = self.is_matched_statement(pattern)
        return is_matched

    @property
    def is_base_statement(self):
        is_base_stmt = self.is_setup_statement
        is_base_stmt |= self.is_section_statement
        is_base_stmt |= self.is_teardown_statement
        return is_base_stmt

    def is_matched_statement(self, pat, data=None):
        data = data or [self.name, self.statement_data]
        lst = data if Misc.is_list(data) else [data]
        is_matched = any(bool(re.match(pat, str(item), re.I)) for item in lst)
        return is_matched

    def substitute_new_format(self, fmt):
        replacing = '{_replace_}'

        is_ancestor_setup_or_teardown = self.is_ancestor_setup_statement
        is_ancestor_setup_or_teardown |= self.is_ancestor_teardown_statement
        is_ancestor_base_statement = self.is_ancestor_base_statement

        if self.is_unittest or self.is_pytest:
            replaced = ''
            if is_ancestor_base_statement:
                if self.is_unittest and is_ancestor_setup_or_teardown:
                    replaced = 'cls'
                else:
                    replaced = 'self'

            lst = fmt.split(replacing)
            if len(lst) == 1:
                return fmt

            for index, item in enumerate(lst[1:], 1):
                if replaced == '' and item.startswith('.'):
                    lst[index] = item[1:]
            new_fmt = replaced.join(lst)
            return new_fmt
        else:
            if self.parent:
                return fmt
            else:
                lines = fmt.splitlines()
                last_line = lines[-1] if lines else ''
                if re.search('(?i)set +global +variable ', last_line):
                    new_fmt = '\n'.join(lines[:-1])
                    return new_fmt
                else:
                    return fmt

    def prepare(self):
        if self.is_empty:
            self._stmt_data = ''
            self._remaining_data = ''
        else:
            lst = self.data.splitlines()
            for index, line in enumerate(lst):
                line = str(line).rstrip()
                if line.strip():
                    match = re.match(self.spacer_pattern, line)
                    if match:
                        self._spacers = match.group('spacers')
                        length = len(self._spacers)
                        if length == 0:
                            self.set_level(level=0)
                        else:
                            if self.parent:
                                chk_lst = ['setup', 'teardown', 'section']
                                if self.parent.name in chk_lst:
                                    self.set_level(level=1)
                                else:
                                    self.increase_level()
                            else:
                                if self._prev_spacers > self._spacers:
                                    self.increase_level()

                    self._prev_spacers = self._spacers
                    self._stmt_data = line
                    self._remaining_data = '\n'.join(lst[index+1:])

                    if self.is_base_statement:
                        self.set_level(level=0)
                        self._spacers = ''

                    return

    def add_child(self, child):
        if isinstance(child, Statement):
            self._children.append(child)
            if isinstance(child.parent, Statement):
                child.set_level(level=self.level+1)

    def set_level(self, level=0):
        self._level = level

    def increase_level(self):
        self.set_level(level=self.level+1)

    def update_level_from_parent(self):
        if isinstance(self.parent, Statement):
            self.set_level(level=self.parent.level+1)

    def get_next_statement_data(self):
        for line in self.remaining_data.splitlines():
            if line.strip():
                return line
        else:
            return ''

    def has_next_statement(self):
        next_stmt_data = self.get_next_statement_data()
        return next_stmt_data.strip() != ''

    def check_next_statement(self, op):
        op = str(op).strip().lower()
        if op not in ['eq', 'le', 'lt', 'gt', 'ge', 'ne']:
            failure = 'Operator MUST BE eq, ne, le, lt, ge, or gt'
            raise ComparisonOperatorError(failure)

        if not self.has_next_statement():
            return False
        next_stmt_data = self.get_next_statement_data()
        match = re.match(self.spacer_pattern, next_stmt_data)
        spacers = match.group('spacers') if match else ''

        result = getattr(operator, op)(spacers, self._spacers)
        return result

    def is_next_statement_sibling(self):
        result = self.check_next_statement('eq')
        return result

    def is_next_statement_children(self):
        result = self.check_next_statement('gt')
        return result

    def is_next_statement_ancestor(self):
        result = self.check_next_statement('lt')
        return result

    def validate_framework(self):

        if self.framework.strip() == '':
            failure = 'framework MUST be "unittest", "pytest", or "robotframework"'
            raise NotImplementedFrameworkError(failure)

        is_valid_framework = self.is_unittest
        is_valid_framework |= self.is_pytest
        is_valid_framework |= self.is_robotframework

        if not is_valid_framework:
            fmt = ('{!r} framework is not implemented.  It MUST be '
                   '"unittest", "pytest", or "robotframework"')
            raise NotImplementedFrameworkError(fmt.format(self.framework))

    def indent_data(self, data, lvl):
        new_data = indent(data, ' ' * lvl * self.indentation)
        return new_data

    def get_display_method(self, level='info'):
        level = str(level).strip().lower()
        chk_lst = ['debug', 'info', 'warning', 'error', 'fatal', 'critical']
        level = level if level in chk_lst else 'info'
        if self.is_logger:
            if self.is_ancestor_base_statement:
                if self.is_ancestor_section_statement:
                    return 'self.logger.%s' % level
                else:
                    if self.is_unittest:
                        return 'cls.logger.%s' % level
                    else:
                        return 'self.logger.%s' % level
        return 'print'

    def render_display_message(self, message):
        message = getattr(self, 'message', message)
        if not message:
            return ''

        if not self.is_robotframework:
            return message

        message = str(message)
        lst = []
        index = 0
        item = None
        for item in re.finditer(r' +', message):
            lst.append(message[index:item.start()])
            spacers = item.group()
            total = len(spacers)
            lst.append(' ' if total == 1 else '${SPACE * %s}' % total)
            index = item.end()
        else:
            if item:
                lst.append(message[item.end():])
        return ''.join(lst) if lst else message

    def get_display_statement(self, message=''):
        message = self.render_display_message(message)
        method_name = self.get_display_method()
        if self.is_unittest or self.is_pytest:
            stmt = '%s(%r)' % (method_name, message)
        else:   # i.e ROBOTFRAMEWORK
            stmt = 'log   %s' % message

        level = self.parent.level + 1 if self.parent else self.level
        stmt = self.indent_data(stmt, level)
        return stmt

    def get_assert_statement(self, expected_result, assert_only=False):
        is_eresult_number, eresult = Misc.try_to_get_number(expected_result)
        if Misc.is_boolean(eresult):
            eresult = int(eresult)

        if self.is_robotframework:
            fmt1 = 'should be true   True == %s'
            fmt2 = ('${total_count}=   get length ${result}\nshould be '
                    'true   ${result} == %s')
        else:
            if self.is_unittest and self.is_ancestor_section_statement:
                fmt1 = 'self.assertTrue(True == %s)'
                fmt2 = 'total_count = len(result)\nself.assertTrue(total_count == %s)'
            else:
                fmt1 = 'assert True == %s'
                fmt2 = 'total_count = len(result)\nassert total_count == %s'

        fmt = fmt1 if assert_only else fmt2
        eresult = expected_result if assert_only else eresult
        level = self.parent.level + 1 if self.parent else self.level
        stmt = self.indent_data(fmt % eresult, level)
        return stmt

    def try_to_get_base_statement(self):
        if self.is_base_statement:
            tbl = dict(setup=SetupStatement,
                       teardown=TeardownStatement)
            key = self.statement_data.lower().strip()
            cls = tbl.get(key, SectionStatement)
            stmt = cls(self.data, framework=self.framework,
                       indentation=self.indentation,
                       is_logger=self.is_logger)
            return stmt if isinstance(stmt, Statement) else self

        else:
            return self


class DummyStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)
        self.case = ''
        self.message = ''
        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        fmt = 'DUMMY {} - {}'
        expected_result = True if self.case.lower() == 'pass' else False

        message = fmt.format(self.case.upper(), self.message)
        displayed_stmt = self.get_display_statement(message=message)
        assert_stmt = self.get_assert_statement(expected_result, assert_only=True)
        return '{}\n{}'.format(displayed_stmt, assert_stmt)

    def parse(self):
        pattern = ' *dummy[_. -]*(?P<case>pass|fail) *[^a-z0-9]*(?P<message> *.+) *$'
        match = re.match(pattern, self.statement_data, re.I)
        if match:
            self._is_parsed = True
            self.case = match.group('case').lower()
            self.message = match.group('message')
            self.name = 'dummy'
        else:
            self._is_parsed = False


class SetupStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        if self.is_unittest:
            lst.append('@classmethod')
            lst.append('def setUpClass(cls):')
        elif self.is_pytest:
            lst.append('def setup_class(self):')
        else:   # i.e ROBOTFRAMEWORK
            lst.append('setup')

        for child in self.children:
            lst.append(child.snippet)

        level = 0 if self.is_robotframework else 1
        script = self.indent_data('\n'.join(lst), level)
        return script

    def parse(self):
        if self.is_setup_statement:
            self.name = 'setup'
            self._is_parsed = True
            if self.is_next_statement_children():
                node = self.create_child(self)
                self.add_child(node)
                while node and node.is_next_statement_sibling():
                    node = self.create_child(node)
                    self.add_child(node)
                if self.children:
                    last_child = self._children[-1]
                    self._remaining_data = last_child.remaining_data
            if not self.children:
                kwargs = dict(framework=self.framework,
                              indentation=self.indentation,
                              is_logger=self.is_logger)
                data = 'dummy_pass - Dummy Setup'
                dummy_stmt = DummyStatement(data, **kwargs, parent=self)
                self.add_child(dummy_stmt)
        else:
            self._is_parsed = False

    def create_child(self, node):
        kwargs = dict(framework=self.framework,
                      indentation=self.indentation,
                      is_logger=self.is_logger)
        next_line = node.get_next_statement_data()

        if CheckStatement.is_child_connect_device_statement(next_line):
            other = ConnectDeviceStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_dummy_statement(next_line):
            other = DummyStatement(node.remaining_data, **kwargs)
        else:
            return None

        other.prev = node
        # node.next = other
        if isinstance(node, self.__class__):
            other.parent = node
            other.update_level_from_parent()
        else:
            other.parent = node.parent
            other.update_level_from_parent()
        return other


class ConnectDeviceStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.devices_vars = dict()
        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        if not self.has_devices_variables():
            fmt = 'Failed to generate invalid connect device statement - {}'
            failure = fmt.format(self.statement_data)
            raise ConnectDeviceStatementError(failure)

        lst = []
        for var_name, device_name in self.devices_vars.items():
            kwargs = dict(v1=var_name, v2=device_name)
            if self.is_robotframework:
                fmt = ("${%(v1)s}=   connect device   %(v2)s\n"
                       "set global variable   ${%(v1)s}")
                new_fmt = self.substitute_new_format(fmt)
                stmt = new_fmt % kwargs
            else:
                fmt = "{_replace_}.%(v1)s = ta.connect_device(%(v2)r)"
                new_fmt = self.substitute_new_format(fmt)
                stmt = new_fmt % kwargs
            lst.append(stmt)

        level = self.parent.level + 1 if self.parent else self.level
        connect_device_statements = self.indent_data('\n'.join(lst), level)

        return connect_device_statements

    def parse(self):
        pattern = r'(?i) *connect +device +(?P<devices_info>.+) *$'
        match = re.match(pattern, self.statement_data)
        if not match:
            self._is_parsed = False
            return

        devices_info = match.group('devices_info').strip()
        devices_info = devices_info.replace('{', '').replace('}', '')

        pattern = r'(?i)(?P<host>\S+)( +as +(?P<var_name>[a-z]\w*))?$'
        for device_info in devices_info.split(','):
            match = re.match(pattern, device_info.strip())
            if match:
                host, var_name = match.group('host'), match.group('var_name')
                self.reserve_data(host, var_name)
            else:
                fmt = 'Invalid connect device statement - {}'
                failure = fmt.format(self.statement_data)
                raise ConnectDeviceStatementError(failure)

        self.name = 'connect_device'
        self._is_parsed = True

    def reserve_data(self, host, var_name):
        devices_vars = SCRIPTINFO.get('devices_vars', dict())
        SCRIPTINFO.devices_vars = devices_vars

        pattern = r'device[0-9]+$'

        if var_name and str(var_name).strip():
            if var_name not in devices_vars:
                devices_vars[var_name] = host
                self.devices_vars[var_name] = host
            else:
                failure = 'Duplicate device variable - "{}"'.format(var_name)
                raise ConnectDeviceStatementError(failure)
        else:
            var_names = [k for k in devices_vars if re.match(pattern, k)]
            if var_names:
                for v in var_names:
                    if host == devices_vars[v]:
                        self.devices_vars[v] = host
                        return
                new_index = int(var_names[-1].strip('device')) + 1
                key = 'device{}'.format(new_index)
                devices_vars[key] = host
                self.devices_vars[key] = host
            else:
                devices_vars['device1'] = host
                self.devices_vars['device1'] = host

    def has_devices_variables(self):
        return bool(list(self.devices_vars))


class DisconnectStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.vars_lst = []
        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        if not self.vars_lst:
            fmt = 'Failed to generate invalid disconnect device statement - {}'
            failure = fmt.format(self.statement_data)
            raise DisconnectDeviceStatementError(failure)

        lst = []
        for var_name in self.vars_lst:
            kwargs = dict(v1=var_name)
            if self.is_robotframework:
                stmt = "disconnect device   ${%(v1)s}" % kwargs
            else:
                fmt = "ta.disconnect_device({_replace_}.%(v1)s)"
                new_fmt = self.substitute_new_format(fmt)
                stmt = new_fmt % kwargs
            lst.append(stmt)

        level = self.parent.level + 1 if self.parent else self.level
        disconnect_device_statements = self.indent_data('\n'.join(lst), level)

        return disconnect_device_statements

    def parse(self):
        pattern = r'(?i) *disconnect *(device)? +(?P<devices_info>.+) *$'
        match = re.match(pattern, self.statement_data)
        if not match:
            self._is_parsed = False
            return

        devices_info = match.group('devices_info').strip()
        devices_info = devices_info.replace('{', '').replace('}', '')

        pattern = r'(?i)(?P<host>\S+)$'
        for index, device_info in enumerate(devices_info.split(',')):
            match = re.match(pattern, device_info.strip())
            if match:
                host = match.group('host')
                self.reserve_data(host, index)
            else:
                fmt = 'Invalid disconnect device statement - {}'
                failure = fmt.format(self.statement_data)
                raise DisconnectDeviceStatementError(failure)

        self.name = 'disconnect_device'
        self._is_parsed = True

    def reserve_data(self, host, index):
        for var_name, host_name in SCRIPTINFO.devices_vars.items():
            if host == host_name:
                self.vars_lst.append(var_name)
                return

        self.vars_lst.append('device{}'.format(index + 1))


class ReleaseDeviceStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.vars_lst = []
        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        if not self.vars_lst:
            fmt = 'Failed to generate invalid release device statement - {}'
            failure = fmt.format(self.statement_data)
            raise ReleaseDeviceStatementError(failure)

        lst = []
        for var_name in self.vars_lst:
            kwargs = dict(v1=var_name)
            if self.is_robotframework:
                stmt = "release device   ${%(v1)s}" % kwargs
            else:
                fmt = "ta.release_device({_replace_}.%(v1)s)"
                new_fmt = self.substitute_new_format(fmt)
                stmt = new_fmt % kwargs
            lst.append(stmt)

        level = self.parent.level + 1 if self.parent else self.level
        release_device_statements = self.indent_data('\n'.join(lst), level)

        return release_device_statements

    def parse(self):
        pattern = r'(?i) *release +device +(?P<devices_info>.+) *$'
        match = re.match(pattern, self.statement_data)
        if not match:
            self._is_parsed = False
            return

        devices_info = match.group('devices_info').strip()
        devices_info = devices_info.replace('{', '').replace('}', '')

        pattern = r'(?i)(?P<host>\S+)$'
        for index, device_info in enumerate(devices_info.split(',')):
            match = re.match(pattern, device_info.strip())
            if match:
                host = match.group('host')
                self.reserve_data(host, index)
            else:
                fmt = 'Invalid release device statement - {}'
                failure = fmt.format(self.statement_data)
                raise ReleaseDeviceStatementError(failure)

        self.name = 'release_device'
        self._is_parsed = True

    def reserve_data(self, host, index):
        for var_name, host_name in SCRIPTINFO.devices_vars.items():
            if host == host_name:
                self.vars_lst.append(var_name)
                return

        self.vars_lst.append('device{}'.format(index + 1))


class TeardownStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        if self.is_unittest:
            lst.append('@classmethod')
            lst.append('def tearDownClass(cls):')
        elif self.is_pytest:
            lst.append('def teardown_class(self):')
        else:   # i.e ROBOTFRAMEWORK
            lst.append('teardown')

        for child in self.children:
            lst.append(child.snippet)

        level = 0 if self.is_robotframework else 1
        script = self.indent_data('\n'.join(lst), level)
        return script

    def parse(self):
        if self.is_teardown_statement:
            self.name = self.statement_data.strip().lower()
            self._is_parsed = True
            if self.is_next_statement_children():
                node = self.create_child(self)
                self.add_child(node)
                while node and node.is_next_statement_sibling():
                    node = self.create_child(node)
                    self.add_child(node)
                if self.children:
                    last_child = self._children[-1]
                    self._remaining_data = last_child.remaining_data
            if not self.children:
                kwargs = dict(framework=self.framework,
                              indentation=self.indentation,
                              is_logger=self.is_logger)
                data = 'dummy_pass - Dummy %s' % self.name.title()
                dummy_stmt = DummyStatement(data, **kwargs, parent=self)
                self.add_child(dummy_stmt)
        else:
            self._is_parsed = False

    def create_child(self, node):
        kwargs = dict(framework=self.framework,
                      indentation=self.indentation,
                      is_logger=self.is_logger)
        next_line = node.get_next_statement_data()

        if CheckStatement.is_child_disconnect_device_statement(next_line):
            other = DisconnectStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_release_device_statement(next_line):
            other = ReleaseDeviceStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_dummy_statement(next_line):
            other = DummyStatement(node.remaining_data, **kwargs)
        else:
            return None

        other.prev = node
        # node.next = other
        if isinstance(node, self.__class__):
            other.parent = node
            other.update_level_from_parent()
        else:
            other.parent = node.parent
            other.update_level_from_parent()
        return other


class SectionStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.description = ''
        self._method_name = ''
        self.parse()

    @property
    def method_name(self):
        return self._method_name

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        fmt = '%s' if self.is_robotframework else 'def %s(self):'
        lst.append(fmt % self.method_name)

        if self.description and self.description.strip():
            if self.is_robotframework:
                lst1 = wrap(self.description, width=56)
                for index, item in enumerate(lst1):
                    prefix = '[Documentation]' if index == 0 else '...'
                    lst1[index] = '{:18} {}'.format(prefix, item)

                method_doc = '\n'.join(lst1)
                lst.append(self.indent_data(method_doc, 1))
                pass
            else:
                method_doc = '"""%s"""' % self.description
                method_doc = '\n'.join(wrap(method_doc, width=70))
                lst.append(self.indent_data(method_doc, 1))

        for child in self.children:
            lst.append(child.snippet)

        level = 0 if self.is_robotframework else 1
        script = self.indent_data('\n'.join(lst), level)
        return script

    def parse(self):
        if not self.is_section_statement:
            self._is_parsed = False
            return

        pattern = r'(?i) *section([^a-z0-9]+)?(?P<description>\w+.+)?'
        match = re.match(pattern, self.statement_data)
        description = match.group('description') if match else 'test_default'
        self.parse_description(description)

        self.name = 'section'
        self._is_parsed = True
        if self.is_next_statement_children():
            node = self.create_child(self)
            self.add_child(node)
            while node and node.is_next_statement_sibling():
                node = self.create_child(node)
                self.add_child(node)
            if self.children:
                last_child = self._children[-1]
                self._remaining_data = last_child.remaining_data
        if not self.children:
            kwargs = dict(framework=self.framework,
                          indentation=self.indentation,
                          is_logger=self.is_logger)
            data = 'dummy_pass - Dummy for section'
            dummy_stmt = DummyStatement(data, **kwargs, parent=self)
            self.add_child(dummy_stmt)

    def parse_description(self, description):
        if not description or description == 'test_default':
            self.description = 'test default'
            self._method_name = 'test default' if self.is_robotframework else 'test_default'
        else:
            description = ' '.join(str(description).splitlines()).strip()
            pattern = r'(?i)(?P<desc>.+?)( +as +(?P<ref>[a-z]\w*( +\w+)?))?$'
            match = re.match(pattern, description)
            desc, ref = match.group('desc'), match.group('ref')
            ref = ref or desc
            ref = re.sub('(?i)[^a-z0-9]+', '_', ref).strip('_')

            self.description = desc

            if not ref.lower().startswith('test'):
                ref = 'test_%s' % ref

            if self.is_robotframework:
                self._method_name = ref.replace('_', ' ')
            else:
                if len(ref) > 60:
                    ref = wrap(ref.replace('_', ' '), width=60)[0].replace(' ', '_')
                self._method_name = ref

    def create_child(self, node):
        kwargs = dict(framework=self.framework,
                      indentation=self.indentation,
                      is_logger=self.is_logger)
        next_line = node.get_next_statement_data()

        if CheckStatement.is_child_verification_statement(next_line):
            other = VerificationStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_performer_statement(next_line):
            other = PerformerStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_connect_device_statement(next_line):
            other = ConnectDeviceStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_disconnect_device_statement(next_line):
            other = DisconnectStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_release_device_statement(next_line):
            other = ReleaseDeviceStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_pausing_statement(next_line):
            other = WaitForStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_iterative_statement(next_line):
            other = LoopStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_dummy_statement(next_line):
            other = DummyStatement(node.remaining_data, **kwargs)
        else:
            return None

        other.prev = node
        # node.next = other
        if isinstance(node, self.__class__):
            other.parent = node
            other.update_level_from_parent()
        else:
            other.parent = node.parent
            other.update_level_from_parent()
        return other


class LoopStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.ntimes = 0
        self.parse()

    @property
    def is_regular_iterative(self):
        result = CheckStatement.is_regular_iterative_statement(self.statement_data)
        return result

    @property
    def is_util_iterative(self):
        result = CheckStatement.is_until_iterative_statement(self.statement_data)
        return result

    @property
    def is_to_last_iterative(self):
        result = CheckStatement.is_to_last_iterative_statement(self.statement_data)
        return result

    @property
    def is_iterative_statement(self):
        result = self.is_regular_iterative
        result |= self.is_util_iterative
        result |= self.is_to_last_iterative
        return result

    @property
    def snippet(self):
        if self.is_regular_iterative:
            stmt = self.regular_iterative_snippet
            return stmt
        elif self.is_util_iterative:
            stmt = self.until_iterative_snippet
            return stmt
        else:
            stmt = self.to_last_iterative_snippet
            return stmt

    @property
    def regular_iterative_snippet(self):
        if not self.is_parsed:
            return ''
        if self.ntimes <= 0:
            return ''

        lst = []
        if self.is_robotframework:
            lst.append('${ntimes}=   set variable   %s' % self.ntimes)
            lst.append('@{indexes}=   evaluate   range(1, ${ntimes} + 1)')
            lst.append('FOR   ${index}   IN   @{indexes}')
            for child in self.children:
                if child.name == 'verification':
                    msg = 'Failed at iteration ${index}/${ntimes}'
                    child_snippet = child.render_assertion_message(msg)
                    lst.append(child_snippet)
                else:
                    lst.append(child.snippet)
            lst.append('END')
        else:
            lst.append('ntimes = %s' % self.ntimes)
            lst.append('indexes = range(1, times + 1)')
            lst.append('for index in indexes:')
            for child in self.children:
                if child.name == 'verification':
                    msg = "'Failed at iteration {}/{}'.format(index, ntimes)"
                    child_snippet = child.render_assertion_message(msg)
                    lst.append(child_snippet)
                else:
                    lst.append(child.snippet)

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    @property
    def until_iterative_snippet(self):
        if not self.is_parsed:
            return ''
        if self.ntimes <= 0:
            return ''

        lst = []
        if self.is_robotframework:
            lst.append('${ntimes}=   set variable   %s' % self.ntimes)
            lst.append('@{indexes}=   evaluate   range(1, ${ntimes} + 1)')
            lst.append('${is_passed}=   set variable   ${True}')
            lst.append('FOR   ${index}   IN   @{indexes}')
            for child in self.children:
                if child.name == 'verification':
                    msg = 'Failed at iteration ${index}/${ntimes}'
                    child_snippet = child.render_assertion_message(msg)
                    lst.append(child_snippet)
                else:
                    lst.append(child.snippet)

            lst.append(self.indent_data('exit for loop if   ${is_passed}', 1))
            lst.append('END')
        else:
            lst.append('ntimes = %s' % self.ntimes)
            lst.append('indexes = range(1, times + 1)')
            lst.append('is_passed = True')
            lst.append('for index in indexes:')
            for child in self.children:
                if child.name == 'verification':
                    msg = "'Failed at iteration {}/{}'.format(index, ntimes)"
                    child_snippet = child.render_assertion_message(msg)
                    lst.append(child_snippet)
                else:
                    lst.append(child.snippet)

            lst.append(self.indent_data('if is_passed:', 1))
            lst.append(self.indent_data('break', 2))

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    @property
    def to_last_iterative_snippet(self):
        if not self.is_parsed:
            return ''
        if self.ntimes <= 0:
            return ''

        lst = []
        if self.is_robotframework:
            lst.append('${ntimes}=   set variable   %s' % self.ntimes)
            lst.append('@{indexes}=   evaluate   range(1, ${ntimes} + 1)')
            lst.append('${is_passed}=   set variable   ${True}')
            lst.append('FOR   ${index}   IN   @{indexes}')
            for child in self.children:
                if child.name == 'verification':
                    addition = '${is_passed}=   evaluate   ${is_passed} and ${check}'
                    child_snippet = child.convert_assertion_to_check(addition=addition)
                    lst.append(child_snippet)
                else:
                    lst.append(child.snippet)
            lst.append(('run keyword if   ${is_passed} == False   Log   '
                        'failed verification(s) at iteration '
                        '${index}/${ntimes}   WARN'))
            lst.append('END')
            lst.append('should be true   ${is_passed}')
        else:
            lst.append('ntimes = %s' % self.ntimes)
            lst.append('indexes = range(1, times + 1)')
            lst.append('is_passed = True')
            lst.append('for index in indexes:')
            for child in self.children:
                if child.name == 'verification':
                    addition = 'is_passed = is_passed and check'
                    child_snippet = child.convert_assertion_to_check(addition=addition)
                    lst.append(child_snippet)
                else:
                    lst.append(child.snippet)

            lst.append(self.indent_data('if not is_passed:', 1))
            warned_msg = "'Warning: failed verification(s) at iteration {}/{}'.format(index, ntimes)"
            lst.append(self.indent_data('print(%s)' % warned_msg, 2))

            if self.is_unittest and self.is_ancestor_section_statement:
                lst.append('self.assertTrue(is_passed)')
            else:
                lst.append('assert is_passed')

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    def parse(self):
        if not self.is_iterative_statement:
            self._is_parsed = False
            return

        pattern = r'(?i) *loop +(?P<ntimes>[0-9]+) +'
        match = re.match(pattern, self.statement_data)
        self.ntimes = int(match.group('ntimes'))

        if self.is_next_statement_children():
            node = self.create_child(self)
            self.add_child(node)
            while node and node.is_next_statement_sibling():
                node = self.create_child(node)
                self.add_child(node)
            if self.children:
                last_child = self._children[-1]
                self._remaining_data = last_child.remaining_data
        if not self.children:
            kwargs = dict(framework=self.framework,
                          indentation=self.indentation,
                          is_logger=self.is_logger)
            data = 'dummy_pass - Dummy iterative statement'
            dummy_stmt = DummyStatement(data, **kwargs, parent=self)
            self.add_child(dummy_stmt)

        self.name = 'loop'
        self._is_parsed = True
        self.update_level_from_parent()

    def create_child(self, node):
        kwargs = dict(framework=self.framework,
                      indentation=self.indentation,
                      is_logger=self.is_logger)
        next_line = node.get_next_statement_data()

        if CheckStatement.is_child_verification_statement(next_line):
            other = VerificationStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_performer_statement(next_line):
            other = PerformerStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_connect_device_statement(next_line):
            other = ConnectDeviceStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_disconnect_device_statement(next_line):
            other = DisconnectStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_release_device_statement(next_line):
            other = ReleaseDeviceStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_pausing_statement(next_line):
            other = WaitForStatement(node.remaining_data, **kwargs)
        elif CheckStatement.is_child_dummy_statement(next_line):
            other = DummyStatement(node.remaining_data, **kwargs)
        else:
            return None

        other.prev = node
        # node.next = other
        if isinstance(node, self.__class__):
            other.parent = node
            other.update_level_from_parent()
        else:
            other.parent = node.parent
            other.update_level_from_parent()
        return other


class PerformerStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.result = None
        self.parse()

    @property
    def snippet(self):
        if self.name == 'execution':
            stmt = self.execution_snippet
            return stmt
        elif self.name == 'configuration':
            stmt = self.configuration_snippet
            return stmt
        elif self.name == 'reload':
            stmt = self.reload_snippet
            return stmt

    @property
    def execution_snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        result = self.result

        if self.is_robotframework:
            for device_name in result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)
                if result.has_select_statement:
                    fmt = '${output}=   execute   ${%s}   cmdline=%s'
                    lst.append(fmt % (var_name, result.operation_ref))
                    if result.is_template:
                        fmt = ('convert_and_filter\n'
                               '...   ${output}   convertor=%s   template_ref=%s\n'
                               '...   select_statement=%s')
                        stmt = fmt % (result.convertor, result.convertor_arg,
                                      result.select_statement)
                        lst.append(stmt)
                    else:
                        fmt = ('convert_and_filter\n'
                               '...   ${output}   convertor=%s\n'
                               '...   select_statement=%s')
                        stmt = fmt % (result.convertor, result.select_statement)
                        lst.append(stmt)
                else:
                    fmt = 'execute   ${%s}   cmdline=%s'
                    lst.append(fmt % (var_name, self.result.operation_ref))
        else:
            for device_name in self.result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)

                if result.has_select_statement:
                    fmt = 'output = ta.execute({_replace_}.%s, cmdline=%r)'
                    new_fmt = self.substitute_new_format(fmt)
                    lst.append(new_fmt % (var_name, result.operation_ref))
                    if result.is_template:
                        fmt = ('ta.convert_and_filter(\n'
                               '    output, convertor=%r, template_ref=%r,\n'
                               '    select_statement=%r\n'
                               ')')
                        fmt = fmt.replace('    ', ' ' * self.indentation)
                        stmt = fmt % (result.convertor, result.convertor_arg,
                                      result.select_statement)
                        lst.append(stmt)
                    else:
                        fmt = ('ta.convert_and_filter(\n'
                               '    output, convertor=%r,\n'
                               '    select_statement=%r\n'
                               ')')
                        fmt = fmt.replace('    ', ' ' * self.indentation)
                        stmt = fmt % (result.convertor, result.select_statement)
                        lst.append(stmt)
                else:
                    fmt = 'ta.execute({_replace_}.%s, cmdline=%r)'
                    new_fmt = self.substitute_new_format(fmt)
                    lst.append(new_fmt % (var_name, result.operation_ref))

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    @property
    def configuration_snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        result = self.result

        if self.is_robotframework:
            for device_name in result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)
                fmt = 'configure   ${%s}   cfg=%s'
                lst.append(fmt % (var_name, self.result.operation_ref))
        else:
            for device_name in self.result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)

                fmt = 'ta.configure({_replace_}.%s, cfg=%r)'
                new_fmt = self.substitute_new_format(fmt)
                lst.append(new_fmt % (var_name, result.operation_ref))

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    @property
    def reload_snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        result = self.result

        if self.is_robotframework:
            for device_name in result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)
                fmt = 'reload   ${%s}   cmdline=%s'
                lst.append(fmt % (var_name, self.result.operation_ref))
        else:
            for device_name in self.result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)

                fmt = 'ta.reload({_replace_}.%s, cmdline=%r)'
                new_fmt = self.substitute_new_format(fmt)
                lst.append(new_fmt % (var_name, result.operation_ref))

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    def parse(self):
        if not CheckStatement.is_performer_statement(self.statement_data):
            self._is_parsed = False
            return

        result = ParsedOperation(self.statement_data)
        self.result = result
        self._is_parsed = result.is_parsed
        self.name = self.result.name
        self.update_level_from_parent()

        if result.error:
            raise PerformerStatementError(result.error)


class VerificationStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)

        self.result = None
        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        lst = []

        result = self.result

        if self.is_robotframework:
            for device_name in result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)

                fmt = '${output}=   execute   ${%s}   cmdline=%s'
                lst.append(fmt % (var_name, result.operation_ref))
                if result.is_template:
                    fmt = ('${result}=   convert_and_filter\n'
                           '...   ${output}   convertor=%s   template_ref=%s\n'
                           '...   select_statement=%s')
                    stmt = fmt % (result.convertor, result.convertor_arg,
                                  result.select_statement)
                    lst.append(stmt)
                else:
                    fmt = ('${result}=   convert_and_filter\n'
                           '...   ${output}   convertor=%s\n'
                           '...   select_statement=%s')
                    stmt = fmt % (result.convertor, result.select_statement)
                    lst.append(stmt)

                lst.append('${total_count}=  get length   ${result}')
                fmt = 'should be true   ${total_count} %s %s'
                lst.append(fmt % (result.condition_symbol, result.expected_condition))

        else:
            for device_name in self.result.devices_names:
                var_name = SCRIPTINFO.get_device_var(device_name)

                fmt = 'output = ta.execute({_replace_}.%s, cmdline=%r)'
                new_fmt = self.substitute_new_format(fmt)
                lst.append(new_fmt % (var_name, result.operation_ref))
                if result.is_template:
                    fmt = ('result = ta.convert_and_filter(\n'
                           '    output, convertor=%r, template_ref=%r,\n'
                           '    select_statement=%r\n'
                           ')')
                    fmt = fmt.replace('    ', ' ' * self.indentation)
                    stmt = fmt % (result.convertor, result.convertor_arg,
                                  result.select_statement)
                    lst.append(stmt)
                else:
                    fmt = ('result = ta.convert_and_filter(\n'
                           '    output, convertor=%r,\n'
                           '    select_statement=%r\n'
                           ')')
                    fmt = fmt.replace('    ', ' ' * self.indentation)
                    stmt = fmt % (result.convertor, result.select_statement)
                    lst.append(stmt)

                lst.append('total_count = len(result)')
                if self.is_unittest and self.is_ancestor_section_statement:
                    fmt = 'self.assertTrue(total_count %s %s)'
                    lst.append(fmt % (result.condition_symbol, result.expected_condition))
                else:
                    fmt = 'assert total_count %s %s'
                    lst.append(fmt % (result.condition_symbol, result.expected_condition))

        stmt = self.indent_data('\n'.join(lst), self.level)
        return stmt

    def render_assertion_message(self, msg):
        if not self.snippet:
            return ''

        lines = dedent(self.snippet).splitlines()
        pattern = '(?i)(?P<case1>should be true)|(?P<case2>self[.])?assert(True)?'

        lst = []
        for line in lines:
            match = re.match(pattern, line)
            if match:
                txt = line
                if match.group('case1'):
                    fmt = '%s   %s'
                elif match.group('case2'):
                    fmt = '%s, msg=%s)'
                    txt = line[-1]
                else:
                    fmt = '%s, %s'
                new_line = fmt % (txt, msg)
                lst.append(new_line)
            else:
                lst.append(line)

        new_snippet = self.indent_data('\n'.join(lst), self.level)
        return new_snippet

    def convert_assertion_to_check(self, addition=''):
        if not self.snippet:
            return ''

        lines = dedent(self.snippet).splitlines()
        pattern = ('(?i)(?P<case>(should be true)|(self[.])?assert(True)?) *'
                   '(?P<val>[^ ].*[^ ]?) *$')

        lst = []
        for index, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                val = match.group('val').strip()
                if self.is_robotframework:
                    lst.append('${check}=   evaluate   %s' % val)
                else:
                    val = val.lstrip('(').rstrip(')')
                    lst.append('check = %s' % val)
                addition and lst.append(addition)
            else:
                lst.append(line)

        new_snippet = self.indent_data('\n'.join(lst), self.level)
        return new_snippet

    def parse(self):
        if not CheckStatement.is_execute_cmdline(self.statement_data):
            self._is_parsed = False
            return

        result = ParsedOperation(self.statement_data)
        self.result = result
        self._is_parsed = result.is_parsed
        self.name = 'verification'
        self.update_level_from_parent()

        if result.error:
            raise PerformerStatementError(result.error)

        if not self.result.is_verification:
            fmt = 'Invalid verification statement format\n %s'
            raise VerificationStatementError(fmt % self.statement_data)


class WaitForStatement(Statement):
    def __init__(self, data, parent=None, framework='',
                 indentation=4, is_logger=False):
        super().__init__(data, parent=parent, framework=framework,
                         indentation=indentation, is_logger=is_logger)
        self.total_seconds = 0
        self.parse()

    @property
    def snippet(self):
        if not self.is_parsed:
            return ''

        fmt = 'wait for   %s' if self.is_robotframework else 'ta.wait_for(%s)'
        stmt = self.indent_data(fmt % self.total_seconds, self.level)
        return stmt

    def parse(self):
        pattern = r'(?i) *((wait +for)|sleep) +(?P<capture_data>[0-9].+) *$'
        match = re.match(pattern, self.statement_data)
        if not match:
            self._is_parsed = False
            return

        capture_data = match.group('capture_data').strip()

        pattern = ('(?P<val>([0-9]*[.])?[0-9]+) *'
                   '(?P<unit>h((ou)?rs?)?|m(in(utes?)?)?|'
                   's(ec(onds?)?)?|d(ays?)?)?')
        match = re.match(pattern, capture_data, re. I)
        if not match:
            failure = 'Invalid wait for statement format'
            raise WaitForStatementError(failure)

        result = DotObject(match.groupdict())
        tbl = dict(s=1, m=60, h=60 * 60, d=60 * 60 * 24)
        multiplier = tbl.get(str(result.unit).lower()[:1], 1)
        seconds = float(result.val) * multiplier
        self.total_seconds = int(seconds) if int(seconds) == seconds else seconds
        self._is_parsed = True
        self.name = 'wait_for'
        self.update_level_from_parent()


class ScriptBuilder:
    def __init__(self, data, framework='', indentation=4, is_logger=False,
                 username='', email='', company='',):
        self.data = data
        self.framework = str(framework).strip()
        self.indentation = indentation
        self.is_logger = is_logger
        self.username = str(username).strip()
        self.email = str(email).strip()
        self.company = str(company).strip() or self.username

        self.setup_statement = None
        self.teardown_statement = None
        self.section_statements = []
        self.build()

    @property
    def testscript(self):
        if self.setup_statement and self.teardown_statement:
            lst = [self.import_library_code,
                   '',
                   self.setup_teardown_code,
                   '',
                   self.sections_code]
            script = '\n'.join(lst).strip()

            if self.framework == FWTYPE.UNITTEST:
                spacer = ' ' * self.indentation
                addition = '\n'.join([
                    "if __name__ == '__main__':",
                    '%s%s' % (spacer, 'unittest.main('),
                    '%s%s' % (spacer * 2, 'testRunner=XMLTestRunner(output="report"),'),
                    '%s%s' % (spacer * 2, 'failfast=False, buffer=False, catchbreak=False'),
                    '%s%s' % (spacer, ')')
                ])
                script = '%s\n\n%s' % (script, addition)

            return script + '\n'
        else:
            if self.setup_statement:
                failure = 'CANT build script without Setup statement'
            elif self.teardown_statement:
                failure = 'CANT build test script without Teardown statement'
            else:
                failure = 'CANT build script without Setup and Teardown statements'
            raise ScriptBuilderError(failure)

    @property
    def get_logger_function(self):
        func_text = dedent('''
            def get_logger(name='TATestScript'):
                """This function only creates logger instance with
                basic logging configuration.
                ==================================================
                PLEASE UPDATE your get_logger function.
                ==================================================
                """
                import logging
                logging.basicConfig(
                    level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[
                        logging.FileHandler('%s.log' % name.lower()),
                        logging.StreamHandler()
                    ]
                )
                logger = logging.getLogger(name)
                return logger
        ''').strip()

        func_text = func_text.replace('    ', ' ' * self.indentation)
        return func_text

    @property
    def intro_code(self):
        fmt = '# {} script is generated by Describe-Get-System Proof of Concept'
        user_fmt = '# Created by  : {0.username}'
        email_fmt = '# Email       : {0.email}'
        company_fmt = '# Company     : {0.company}'
        datetime_str = '# Created date: {:%Y-%m-%d}'.format(datetime.now())
        lst = [fmt.format(self.framework.lower())]
        self.username and lst.append(user_fmt.format(self))
        self.email and lst.append(email_fmt.format(self))
        self.company and lst.append(company_fmt.format(self))
        not SCRIPTINFO.is_testing_enabled and lst.append(datetime_str)

        intro = '\n'.join(['#' * 80] + lst + ['#' * 80])
        return intro

    @property
    def import_library_code(self):
        lst = [self.intro_code, '']

        is_unittest = self.framework == FWTYPE.UNITTEST

        if self.framework == FWTYPE.ROBOTFRAMEWORK:
            lst += [
                '*** Settings ***',
                'Library          BuiltIn',
                'Library          Collections',
                'Library          dgspoc.robotframeworklib',
                'Suite Setup      {}'.format(self.setup_statement.name),
                'Suite Teardown   {}'.format(self.teardown_statement.name),
            ]
        else:
            cls_name = SCRIPTINFO.get_class_name()
            inherit = '(unittest.TestCase)' if is_unittest else ''
            lst.append('import unittest' if is_unittest else '# import pytest')
            lst.append('import dgspoc as ta')
            is_unittest and lst.append('from xmlrunner import XMLTestRunner')
            lst.append('\n')
            if self.is_logger:
                lst.append(self.get_logger_function)
                lst.append('\n')
            lst.append('class %s%s:' % (cls_name, inherit))
            if self.is_logger:
                lst.append(' ' * self.indentation + 'logger = get_logger()')

        import_lib_txt = '\n'.join(lst)
        return import_lib_txt

    @property
    def setup_teardown_code(self):

        lst = [self.setup_statement.snippet,
               '',
               self.teardown_statement.snippet]
        if self.framework == FWTYPE.ROBOTFRAMEWORK:
            lst.insert(0, '*** Keywords ***')

        setup_teardown_txt = '\n'.join(lst)
        return setup_teardown_txt

    @property
    def sections_code(self):
        is_robotframework = self.framework == FWTYPE.ROBOTFRAMEWORK
        lst = []
        fmt = 'test %03i ' if is_robotframework else 'def test_%03i_'
        replacing = 'test ' if is_robotframework else 'def test_'

        for index, stmt in enumerate(self.section_statements, 1):
            lst.append('')
            if stmt.snippet:
                lst.append(stmt.snippet.replace(replacing, fmt % index, 1))

        if lst:
            if is_robotframework:
                lst[0] = '*** Test Cases ***'
            not lst[0] and lst.pop(0)

        sections_code_txt = '\n'.join(lst)
        return sections_code_txt

    def build(self):
        data = self.data
        count = 2000

        while data.strip() and count > 0:
            stmt = Statement(data, framework=self.framework,
                             indentation=self.indentation,
                             is_logger=self.is_logger)
            stmt = stmt.try_to_get_base_statement()
            self.add_statement(stmt)
            data = stmt.remaining_data
            count -= 1

    def add_statement(self, stmt):
        if stmt.is_setup_statement:
            if not self.setup_statement:
                self.setup_statement = stmt
            else:
                self.warn_duplicate_statement(stmt)
        elif stmt.is_teardown_statement:
            if not self.teardown_statement:
                self.teardown_statement = stmt
            else:
                self.warn_duplicate_statement(stmt)
        elif stmt.is_section_statement:
            if self.is_uniq_section_statement(stmt):
                self.section_statements.append(stmt)
            else:
                self.warn_duplicate_statement(stmt)
        else:
            self.warn_not_implement_statement(stmt)

    def is_uniq_section_statement(self, stmt):
        if not self.section_statements:
            return True

        chk = stmt.snippet
        is_duplicate = any(chk == k.snippet for k in self.section_statements)
        return not is_duplicate

    def warn_duplicate_statement(self, stmt):
        fmt = 'IncompleteTask - Need to implement warn_duplicate_statement\n{}'
        raise NotImplementedError(fmt.format(stmt.statement_data))

    def warn_not_implement_statement(self, stmt):
        fmt = 'IncompleteTask - Need to implement warn_not_implement_statement\n{}'
        raise NotImplementedError(fmt.format(stmt.statement_data))
