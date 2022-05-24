from formal.sqlcommenter import generate_sql_comment
import psycopg2.extensions
import psycopg2
import logging
# !/usr/bin/python
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


# This integration extends psycopg2.extensions.cursor
# by implementing a custom execute method.
def CommenterCursorFactory():

    class CommenterCursor(psycopg2.extensions.cursor):
        def execute(self, sql, endUserID="", args=None):
            sql = generate_sql_comment(endUserID) + sql
            return psycopg2.extensions.cursor.execute(self, sql, args)

    return CommenterCursor
