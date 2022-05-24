from copy import deepcopy
from requests import Response
from typing import List, Union
from urllib.parse import urljoin

from dnastack.client.base_client import BaseServiceClient
from dnastack.client.collections.model import Collection
from dnastack.client.data_connect import DATA_CONNECT_TYPE_V1_0
from dnastack.client.service_registry.models import ServiceType
from dnastack.configuration.models import ServiceEndpoint
from dnastack.exceptions import ServiceException

# Feature: Support the service registry integration
# Feature: Using both root and "singular" soon-to-be-deprecated per-collection data connect endpoints
STANDARD_COLLECTION_SERVICE_TYPE_V1_0 = ServiceType(group='com.dnastack',
                                                    artifact='collection-service',
                                                    version='1.0.0')

# Feature: No support for service registry integration
# Feature: Only using "plural" per-collection data connect endpoint
EXPLORER_COLLECTION_SERVICE_TYPE_V1_0 = ServiceType(group='com.dnastack.explorer',
                                                    artifact='collection-service',
                                                    version='1.0.0')


def _raise_error(url: str, res: Response, primary_reason: str):
    summary = f'Unexpected Error: HTTP {res.status_code}'
    detail = primary_reason

    if res.status_code == 401:
        summary = "Authentication Required"
    elif res.status_code == 403:
        summary = "Access Denied"
    elif res.status_code == 404:
        summary = "Not Found"
    else:
        response_json = res.json()
        if 'message' in response_json:
            # Handle a generic error response from the service.
            detail += f' ({response_json["message"]})'
        elif "errors" in response_json and response_json['errors'] and 'title' in response_json['errors'][0]:
            detail += f' ({", ".join([e["title"] for e in response_json["errors"]])})'
        else:
            detail += f' ({response_json})'

    raise ServiceException(msg=f'{summary}: {detail}', url=url)


class CollectionServiceClient(BaseServiceClient):
    """Client for Collection API"""

    @staticmethod
    def get_adapter_type() -> str:
        return 'collections'

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        return [
            EXPLORER_COLLECTION_SERVICE_TYPE_V1_0,
            STANDARD_COLLECTION_SERVICE_TYPE_V1_0,
        ]

    def _get_single_collection_url(self, id_or_slug_name: str, extended_path: str = ''):
        return urljoin(self.url, f'collection/{id_or_slug_name}{extended_path}')

    def _get_resource_url(self, id_or_slug_name: str, short_service_type: str):
        return self._get_single_collection_url(id_or_slug_name, f'/{short_service_type}')

    def get(self, id_or_slug_name: str) -> Collection:
        """ Get a collection by ID or slug name """
        with self.create_http_session() as session:
            get_response = session.get(self._get_single_collection_url(id_or_slug_name))
            if not get_response.ok:
                _raise_error(self.url, get_response, 'Collection not found')

            return Collection(**get_response.json())

    def list_collections(self) -> List[Collection]:
        """ List all available collections """
        with self.create_http_session() as session:
            res = session.get(urljoin(self.url, 'collections'))

            if not res.ok:
                _raise_error(self.url, res, "Unable to list collections")

            return [Collection(**raw_collection) for raw_collection in res.json()]

    def data_connect_endpoint(self, collection: Union[str, Collection, None] = None) -> ServiceEndpoint:
        """
        Get the URL to the corresponding Data Connect endpoint

        :param collection: The collection or collection ID. It is optional and only used by the explorer.
        """
        sub_endpoint = ServiceEndpoint(**deepcopy(self._endpoint.dict()))
        sub_endpoint.type = DATA_CONNECT_TYPE_V1_0

        if sub_endpoint.authentication:
            auth_type = sub_endpoint.authentication.get('type')

            # Override the resource URL
            if not auth_type or auth_type == 'oauth2':
                # NOTE: Generally, we want to restrict the access only to tables within the scope of the requested
                #       collection. However, due to the recent requirements where the client needs to have access to
                #       "/data-connect/table/system/metadata/catalogs" and the upcoming deprecation of per-collection
                #       data connect controller, the client code will now ask for authorization for the whole service.
                sub_endpoint.authentication['resource_url'] = self._endpoint.url

                # Reset the scope.
                if 'scope' in sub_endpoint.authentication:
                    del sub_endpoint.authentication['scope']

        if self._endpoint.model_version == 2.0 and self._get_service_type() == STANDARD_COLLECTION_SERVICE_TYPE_V1_0:
            sub_endpoint.url = urljoin(self._endpoint.url, '/data-connect/')
        else:
            # noinspection PyUnusedLocal
            collection_id = None

            if isinstance(collection, Collection):
                collection_id = collection.slugName
            elif isinstance(collection, str):
                collection_id = collection
            else:
                raise TypeError(f'For collection/{self._endpoint.model_version} ({self._endpoint.type}), the given '
                                f'collection must be either an instance of Collection or the ID/slug name of the '
                                f'collection (string). The given type of collection is {type(collection).__name__}.')

            sub_endpoint.url = self._get_single_collection_url(collection_id, '/data-connect/')

        return sub_endpoint

    def _get_service_type(self) -> ServiceType:
        return self._endpoint.type or self.get_supported_service_types()[0]


# Temporarily for backward compatibility
CollectionsClient = CollectionServiceClient
