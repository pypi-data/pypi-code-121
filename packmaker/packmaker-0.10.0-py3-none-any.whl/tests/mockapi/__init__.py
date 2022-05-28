# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2019 Mark Crewson <mark@crewson.net>
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

import importlib.resources as resources
import json
import requests

from packmaker.curse import api

##############################################################################


class MockApi (api.CurseAPI):

    def get_addon(self, projectId):
        try:
            resp = resources.read_text(self.__module__, 'get_addon_{}.json'.format(projectId))
            return json.loads(resp)
        except FileNotFoundError:
            raise requests.exceptions.HTTPError("not found")

    def get_addon_files(self, projectId, gameVersion=None, index=0, pageSize=50):
        resp = resources.read_text(self.__module__, 'get_addon_files_{}_{}.json'.format(projectId, index))
        return json.loads(resp)

    def get_addons_by_criteria(self, gameId, classId=None, categoryIds=None,
                               sort='Featured', sortDescending=True, gameVersions=None,
                               index=0, pageSize=50, searchFilter=None):
        try:
            resp = resources.read_text(self.__module__, 'get_addons_by_criteria_{}.json'.format(searchFilter))
            return json.loads(resp)
        except FileNotFoundError:
            return {"data": [], "pagination": {}}

##############################################################################
# THE END
