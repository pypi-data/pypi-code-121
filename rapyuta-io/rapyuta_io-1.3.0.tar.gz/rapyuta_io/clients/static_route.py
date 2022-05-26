from __future__ import absolute_import
from rapyuta_io.utils import ObjDict
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils import RestClient


class StaticRoute(ObjDict):
    """
    StaticRoute class represents an instance of a static route. It contains methods to delete static route.

    :ivar CreatedAt: Date of creation
    :ivar DeletedAt: Date of deletion
    :ivar ID: ID of the static route
    :ivar creator: User guid who created the static route
    :ivar metadata: Metadata associated with the static route
    :ivar projectGUID: GUID of the project the static route is to be created in
    :ivar urlPrefix: Prefix/subdomain of the static route
    :ivar urlString: Full static route URL
    """

    STATIC_ROUTE_PATH = '/api/staticroute'

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)

    def delete(self):
        """
        Delete static route

        :return: True or False
        :rtype: bool

        Following example demonstrates how to delete a static route

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> static_route = client.get_all_static_routes()[0]
            >>> result = static_route.delete()
        """
        url = self._core_api_host + self.STATIC_ROUTE_PATH + '/delete'
        headers = create_auth_header(self._auth_token, self._project)
        payload = {"guid": self.guid}
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute(payload)
        response_data = get_api_response_data(response, parse_full=True)
        if response_data['success']:
            self.clear()
            return True
        return False
