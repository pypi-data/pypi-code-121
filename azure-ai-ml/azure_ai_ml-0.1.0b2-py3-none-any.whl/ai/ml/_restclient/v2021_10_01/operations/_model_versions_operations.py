# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import functools
from typing import TYPE_CHECKING
import warnings

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.mgmt.core.exceptions import ARMErrorFormat
from msrest import Serializer

from .. import models as _models
from .._vendor import _convert_request, _format_url_section

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, Iterable, Optional, TypeVar, Union
    T = TypeVar('T')
    ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False
# fmt: off

def build_list_request(
    name,  # type: str
    subscription_id,  # type: str
    resource_group_name,  # type: str
    workspace_name,  # type: str
    **kwargs  # type: Any
):
    # type: (...) -> HttpRequest
    skip = kwargs.pop('skip', None)  # type: Optional[str]
    order_by = kwargs.pop('order_by', None)  # type: Optional[str]
    top = kwargs.pop('top', None)  # type: Optional[int]
    version = kwargs.pop('version', None)  # type: Optional[str]
    description = kwargs.pop('description', None)  # type: Optional[str]
    offset = kwargs.pop('offset', None)  # type: Optional[int]
    tags = kwargs.pop('tags', None)  # type: Optional[str]
    properties = kwargs.pop('properties', None)  # type: Optional[str]
    feed = kwargs.pop('feed', None)  # type: Optional[str]
    list_view_type = kwargs.pop('list_view_type', None)  # type: Optional[Union[str, "_models.ListViewType"]]

    api_version = "2021-10-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions')
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str', min_length=1),
        "resourceGroupName": _SERIALIZER.url("resource_group_name", resource_group_name, 'str', max_length=90, min_length=1),
        "workspaceName": _SERIALIZER.url("workspace_name", workspace_name, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')
    if skip is not None:
        query_parameters['$skip'] = _SERIALIZER.query("skip", skip, 'str')
    if order_by is not None:
        query_parameters['$orderBy'] = _SERIALIZER.query("order_by", order_by, 'str')
    if top is not None:
        query_parameters['$top'] = _SERIALIZER.query("top", top, 'int')
    if version is not None:
        query_parameters['version'] = _SERIALIZER.query("version", version, 'str')
    if description is not None:
        query_parameters['description'] = _SERIALIZER.query("description", description, 'str')
    if offset is not None:
        query_parameters['offset'] = _SERIALIZER.query("offset", offset, 'int')
    if tags is not None:
        query_parameters['tags'] = _SERIALIZER.query("tags", tags, 'str')
    if properties is not None:
        query_parameters['properties'] = _SERIALIZER.query("properties", properties, 'str')
    if feed is not None:
        query_parameters['feed'] = _SERIALIZER.query("feed", feed, 'str')
    if list_view_type is not None:
        query_parameters['listViewType'] = _SERIALIZER.query("list_view_type", list_view_type, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="GET",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )


def build_delete_request(
    name,  # type: str
    version,  # type: str
    subscription_id,  # type: str
    resource_group_name,  # type: str
    workspace_name,  # type: str
    **kwargs  # type: Any
):
    # type: (...) -> HttpRequest
    api_version = "2021-10-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions/{version}')
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, 'str'),
        "version": _SERIALIZER.url("version", version, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str', min_length=1),
        "resourceGroupName": _SERIALIZER.url("resource_group_name", resource_group_name, 'str', max_length=90, min_length=1),
        "workspaceName": _SERIALIZER.url("workspace_name", workspace_name, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="DELETE",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )


def build_get_request(
    name,  # type: str
    version,  # type: str
    subscription_id,  # type: str
    resource_group_name,  # type: str
    workspace_name,  # type: str
    **kwargs  # type: Any
):
    # type: (...) -> HttpRequest
    api_version = "2021-10-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions/{version}')
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, 'str'),
        "version": _SERIALIZER.url("version", version, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str', min_length=1),
        "resourceGroupName": _SERIALIZER.url("resource_group_name", resource_group_name, 'str', max_length=90, min_length=1),
        "workspaceName": _SERIALIZER.url("workspace_name", workspace_name, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="GET",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )


def build_create_or_update_request(
    name,  # type: str
    version,  # type: str
    subscription_id,  # type: str
    resource_group_name,  # type: str
    workspace_name,  # type: str
    **kwargs  # type: Any
):
    # type: (...) -> HttpRequest
    content_type = kwargs.pop('content_type', None)  # type: Optional[str]

    api_version = "2021-10-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions/{version}')
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, 'str', pattern=r'^[a-zA-Z0-9][a-zA-Z0-9\-_]{0,254}$'),
        "version": _SERIALIZER.url("version", version, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str', min_length=1),
        "resourceGroupName": _SERIALIZER.url("resource_group_name", resource_group_name, 'str', max_length=90, min_length=1),
        "workspaceName": _SERIALIZER.url("workspace_name", workspace_name, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    if content_type is not None:
        header_parameters['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="PUT",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )

# fmt: on
class ModelVersionsOperations(object):
    """ModelVersionsOperations operations.

    You should not instantiate this class directly. Instead, you should create a Client instance that
    instantiates it for you and attaches it as an attribute.

    :ivar models: Alias to model classes used in this operation group.
    :type models: ~azure.mgmt.machinelearningservices.models
    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = _models

    def __init__(self, client, config, serializer, deserializer):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    @distributed_trace
    def list(
        self,
        name,  # type: str
        resource_group_name,  # type: str
        workspace_name,  # type: str
        skip=None,  # type: Optional[str]
        order_by=None,  # type: Optional[str]
        top=None,  # type: Optional[int]
        version=None,  # type: Optional[str]
        description=None,  # type: Optional[str]
        offset=None,  # type: Optional[int]
        tags=None,  # type: Optional[str]
        properties=None,  # type: Optional[str]
        feed=None,  # type: Optional[str]
        list_view_type=None,  # type: Optional[Union[str, "_models.ListViewType"]]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable["_models.ModelVersionResourceArmPaginatedResult"]
        """List model versions.

        List model versions.

        :param name: Model name. This is case-sensitive.
        :type name: str
        :param resource_group_name: The name of the resource group. The name is case insensitive.
        :type resource_group_name: str
        :param workspace_name: Name of Azure Machine Learning workspace.
        :type workspace_name: str
        :param skip: Continuation token for pagination.
        :type skip: str
        :param order_by: Ordering of list.
        :type order_by: str
        :param top: Maximum number of records to return.
        :type top: int
        :param version: Model version.
        :type version: str
        :param description: Model description.
        :type description: str
        :param offset: Number of initial results to skip.
        :type offset: int
        :param tags: Comma-separated list of tag names (and optionally values). Example:
         tag1,tag2=value2.
        :type tags: str
        :param properties: Comma-separated list of property names (and optionally values). Example:
         prop1,prop2=value2.
        :type properties: str
        :param feed: Name of the feed.
        :type feed: str
        :param list_view_type: View type for including/excluding (for example) archived entities.
        :type list_view_type: str or ~azure.mgmt.machinelearningservices.models.ListViewType
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either ModelVersionResourceArmPaginatedResult or the
         result of cls(response)
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.mgmt.machinelearningservices.models.ModelVersionResourceArmPaginatedResult]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.ModelVersionResourceArmPaginatedResult"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                
                request = build_list_request(
                    name=name,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=resource_group_name,
                    workspace_name=workspace_name,
                    skip=skip,
                    order_by=order_by,
                    top=top,
                    version=version,
                    description=description,
                    offset=offset,
                    tags=tags,
                    properties=properties,
                    feed=feed,
                    list_view_type=list_view_type,
                    template_url=self.list.metadata['url'],
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)

            else:
                
                request = build_list_request(
                    name=name,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=resource_group_name,
                    workspace_name=workspace_name,
                    skip=skip,
                    order_by=order_by,
                    top=top,
                    version=version,
                    description=description,
                    offset=offset,
                    tags=tags,
                    properties=properties,
                    feed=feed,
                    list_view_type=list_view_type,
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        def extract_data(pipeline_response):
            deserialized = self._deserialize("ModelVersionResourceArmPaginatedResult", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.ErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

            return pipeline_response


        return ItemPaged(
            get_next, extract_data
        )
    list.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions'}  # type: ignore

    @distributed_trace
    def delete(
        self,
        name,  # type: str
        version,  # type: str
        resource_group_name,  # type: str
        workspace_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete version.

        Delete version.

        :param name: Container name. This is case-sensitive.
        :type name: str
        :param version: Version identifier. This is case-sensitive.
        :type version: str
        :param resource_group_name: The name of the resource group. The name is case insensitive.
        :type resource_group_name: str
        :param workspace_name: Name of Azure Machine Learning workspace.
        :type workspace_name: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        
        request = build_delete_request(
            name=name,
            version=version,
            subscription_id=self._config.subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            template_url=self.delete.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.ErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        if cls:
            return cls(pipeline_response, None, {})

    delete.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions/{version}'}  # type: ignore


    @distributed_trace
    def get(
        self,
        name,  # type: str
        version,  # type: str
        resource_group_name,  # type: str
        workspace_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> "_models.ModelVersionData"
        """Get version.

        Get version.

        :param name: Container name. This is case-sensitive.
        :type name: str
        :param version: Version identifier. This is case-sensitive.
        :type version: str
        :param resource_group_name: The name of the resource group. The name is case insensitive.
        :type resource_group_name: str
        :param workspace_name: Name of Azure Machine Learning workspace.
        :type workspace_name: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ModelVersionData, or the result of cls(response)
        :rtype: ~azure.mgmt.machinelearningservices.models.ModelVersionData
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.ModelVersionData"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        
        request = build_get_request(
            name=name,
            version=version,
            subscription_id=self._config.subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            template_url=self.get.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.ErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        deserialized = self._deserialize('ModelVersionData', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    get.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions/{version}'}  # type: ignore


    @distributed_trace
    def create_or_update(
        self,
        name,  # type: str
        version,  # type: str
        resource_group_name,  # type: str
        workspace_name,  # type: str
        body,  # type: "_models.ModelVersionData"
        **kwargs  # type: Any
    ):
        # type: (...) -> "_models.ModelVersionData"
        """Create or update version.

        Create or update version.

        :param name: Container name. This is case-sensitive.
        :type name: str
        :param version: Version identifier. This is case-sensitive.
        :type version: str
        :param resource_group_name: The name of the resource group. The name is case insensitive.
        :type resource_group_name: str
        :param workspace_name: Name of Azure Machine Learning workspace.
        :type workspace_name: str
        :param body: Version entity to create or update.
        :type body: ~azure.mgmt.machinelearningservices.models.ModelVersionData
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ModelVersionData, or the result of cls(response)
        :rtype: ~azure.mgmt.machinelearningservices.models.ModelVersionData
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.ModelVersionData"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        content_type = kwargs.pop('content_type', "application/json")  # type: Optional[str]

        _json = self._serialize.body(body, 'ModelVersionData')

        request = build_create_or_update_request(
            name=name,
            version=version,
            subscription_id=self._config.subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            content_type=content_type,
            json=_json,
            template_url=self.create_or_update.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 201]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.ErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        if response.status_code == 200:
            deserialized = self._deserialize('ModelVersionData', pipeline_response)

        if response.status_code == 201:
            deserialized = self._deserialize('ModelVersionData', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    create_or_update.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/models/{name}/versions/{version}'}  # type: ignore

