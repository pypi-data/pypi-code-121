# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from os.path import abspath, dirname
from restclients_core.dao import DAO


class UWNetID_DAO(DAO):
    def service_name(self):
        return 'uwnetid'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _edit_mock_response(self, method, url, headers, body, response):
        if "POST" == method or "PUT" == method:
            if response.status != 200:
                path = "{0}/resources/uwnetid/file{1}.{2}".format(
                    abspath(dirname(__file__)), url, method)

                try:
                    handle = open(path)
                    response.data = handle.read()
                    response.status = 200
                except IOError:
                    response.status = 404
        elif "DELETE" == method:
            response.status = 200
