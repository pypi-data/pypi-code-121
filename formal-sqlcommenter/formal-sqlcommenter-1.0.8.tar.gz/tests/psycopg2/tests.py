#!/usr/bin/python
#
# Copyright 2021 Formal
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase

import psycopg2.extensions
from forbiddenfruit import curse
from formal.sqlcommenter.psycopg2.extension import CommenterCursorFactory

from ..compat import mock


class Psycopg2TestCase(TestCase):

    def assertSQL(self, sql, endUserID=""):
        def execute(self, sql, args=None):
            pass
        mocked_execute = mock.create_autospec(execute, return_value=endUserID)
        curse(psycopg2.extensions.cursor, 'execute', mocked_execute)
        cursor = CommenterCursorFactory()
        self.assertIn(cursor.execute(
            None, 'SELECT 1;', endUserID), endUserID)
        if (endUserID == ""):
            mocked_execute.assert_called_with(
                None, sql, None)
        else:
            mocked_execute.assert_called_with(
                None, "/*formal_role_id:{0}*/ ".format(endUserID) + sql, None)


class Tests(Psycopg2TestCase):

    def test_no_args(self):
        self.assertSQL('SELECT 1;')

    def test_with_endUserID(self):
        self.assertSQL("SELECT 1;", "1234")
