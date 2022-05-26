# encoding: utf-8
from __future__ import absolute_import
from rapyuta_io.utils.utils import create_auth_header, prepend_bearer_to_auth_token


# Base class for Client connection configuration


class ConnectionConfig(object):
    def __init__(self, auth_token, project):
        self._auth_token = prepend_bearer_to_auth_token(auth_token)
        self._project = project
        self._headers = create_auth_header(self._auth_token,
                                           self._project)

    def set_project(self, project):
        self._project = project
        self._headers = create_auth_header(self._auth_token,
                                           self._project)


class CatalogConfig(ConnectionConfig):
    def __init__(self, catalog_api_host, auth_token, project):
        super(CatalogConfig, self).__init__(auth_token, project)
        self._catalog_api_host = catalog_api_host

    def _get_api_path(self):
        return self._catalog_api_host
