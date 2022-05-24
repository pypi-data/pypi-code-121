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

# import logging

import django
from django.db import connection

from formal.sqlcommenter import generate_sql_comment
# from django.db.backends.utils import CursorDebugWrapper

django_version = django.get_version()
# logger = logging.getLogger(__name__)

class FormalSqlCommenter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user:
            # retrieve value from db before requiring every database request to require it (causing a recursive loop)
            _user_authenticated = request.user.is_authenticated  
        with connection.execute_wrapper(QueryWrapper(request)):
            return self.get_response(request)


class QueryWrapper:
    def __init__(self, request):
        self.request = request

    def __call__(self, execute, sql, params, many, context):
        endUserId = ""

        if self.request.user:
            if self.request.user.is_authenticated:
                if self.request.user.email:
                    endUserId = self.request.user.email
                else:
                    endUserId = self.request.user.id

            # Check for override w context
            endUserIdKey = "formalEndUserId"
            if endUserIdKey in context:
                endUserId = context[endUserIdKey]

            sql = generate_sql_comment(endUserId) + sql
        return execute(sql, params, many, context)
