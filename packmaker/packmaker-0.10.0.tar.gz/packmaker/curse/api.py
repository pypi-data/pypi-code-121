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

import requests

from ..framew.baseobject import BaseObject

##############################################################################


class CurseAPI (BaseObject):

    max_pagesize = 50
    max_index = 10000

    def __init__(self):
        super(BaseObject, self).__init__()

    def _api_baseurl(self):
        raise NotImplementedError

    def _request_headers(self, authRequired):
        return None

    def _getrequest(self, url, params=None, authRequired=True):
        r = requests.get(self._api_baseurl() + url, params, timeout=60, headers=self._request_headers(authRequired))
        r.raise_for_status()
        return r

    def _postrequest(self, url, data, authRequired=True):
        r = requests.post(self._api_baseurl() + url, json=data, timeout=60, headers=self._request_headers(authRequired))
        r.raise_for_status()
        return r

    def get_addon(self, projectId):
        return self._getrequest('mods/{}'.format(projectId)).json()['data']

    def get_addon_file(self, projectId, fileId):
        return self._getrequest('mods/{}/files/{}'.format(projectId, fileId)).json()['data']

    def get_addons(self, projectIds):
        return self._postrequest('mods', {"modIds": projectIds}).json()['data']

    def get_addon_files(self, projectId, gameVersion=None, index=0, pageSize=50):
        url = 'mods/{}/files'.format(projectId)
        parameters = {"index": index,
                      "pageSize": pageSize
                      }
        if gameVersion is not None:
            parameters['gameVersion'] = gameVersion

        return self._getrequest(url, parameters).json()
        return self._getrequest('mods/{}/files'.format(projectId)).json()['data']

    def yield_addon_files(self, projectId, gameVersions=None, pageSize=50):
        if type(gameVersions) is not list:
            gameVersions = [gameVersions]

        if pageSize > self.max_pagesize:
            raise Exception("curse api limits pagesize to {}".format(self.max_pagesize))

        files_seen = []
        for gameVersion in gameVersions:
            index = 0
            done = False
            while not done:
                results = self.get_addon_files(projectId, gameVersion, index, pageSize)

                index += pageSize
                if len(results['data']) < pageSize:
                    done = True
                else:
                    if index + pageSize > self.max_index:
                        pageSize = self.max_index - index
                        if pageSize < 1:
                            done = True

                for file in results['data']:
                    if file['id'] not in files_seen:
                        yield file
                    files_seen.append(file['id'])

    def get_addons_by_criteria(self,
                               gameId,
                               classId=None,
                               categoryIds=None,
                               sort=1,
                               sortOrder="desc",
                               gameVersion=None,
                               index=0,
                               pageSize=50,
                               searchFilter=None):
        url = 'mods/search'
        parameters = {"gameId": gameId,
                      "sort": sort,
                      "sortOrder": sortOrder,
                      "index": index,
                      "pageSize": pageSize
                      }

        if classId is not None:
            parameters['classId'] = classId
        if categoryIds is not None:
            parameters['categoryId'] = categoryIds
        if gameVersion is not None:
            parameters['gameVersion'] = gameVersion
        if searchFilter is not None:
            parameters['searchFilter'] = searchFilter

        return self._getrequest(url, parameters).json()

    def yield_addons_by_criteria(self,
                                 gameId,
                                 classId=None,
                                 categoryIds=None,
                                 sort=1,
                                 sortDescending=True,
                                 gameVersions=None,
                                 pageSize=50,
                                 searchFilter=None):

        if type(gameVersions) is not list:
            gameVersions = [gameVersions]

        if pageSize > self.max_pagesize:
            raise Exception("curse api limits pagesize to {}".format(self.max_pagesize))

        addons_seen = []
        for gameVersion in gameVersions:
            index = 0
            done = False
            while not done:
                results = self.get_addons_by_criteria(gameId, classId, categoryIds,
                                                      sort, sortDescending, gameVersion,
                                                      index, pageSize, searchFilter)

                index += pageSize
                if len(results['data']) < pageSize:
                    done = True

                if index > self.max_index:
                    done = True
                else:
                    if index + pageSize > self.max_index:
                        pageSize = self.max_index - index
                        if pageSize < 1:
                            done = True

                for addon in results['data']:
                    if addon['id'] not in addons_seen:
                        yield addon
                    addons_seen.append(addon['id'])

    def get_modloader_timestamp(self):
        return self._getrequest('minecraft/modloader/timestamp').json()

    def get_modloader_list(self):
        return self._getrequest('minecraft/modloader').json()['data']

    def get_modloader_info(self, versionName):
        return self._getrequest('minecraft/modloader/{}'.format(versionName), authRequired=False).json()['data']

##############################################################################
# THE END
