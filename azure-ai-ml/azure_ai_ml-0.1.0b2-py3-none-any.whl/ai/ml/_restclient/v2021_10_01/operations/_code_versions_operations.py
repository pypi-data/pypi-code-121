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
    order_by = kwargs.pop('order_by', None)  # type: Optional[str]
    top = kwargs.pop('top', None)  # type: Optional[int]
    skip = kwargs.pop('skip', None)  # type: Optional[str]

    api_version = "2021-10-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions')
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
    if order_by is not None:
        query_parameters['$orderBy'] = _SERIALIZER.query("order_by", order_by, 'str')
    if top is not None:
        query_parameters['$top'] = _SERIALIZER.query("top", top, 'int')
    if skip is not None:
        query_parameters['$skip'] = _SERIALIZER.query("skip", skip, 'str')

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
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions/{version}')
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
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions/{version}')
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
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions/{version}')
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
class CodeVersionsOperations(object):
    """CodeVersionsOperations operations.

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
        order_by=None,  # type: Optional[str]
        top=None,  # type: Optional[int]
        skip=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable["_models.CodeVersionResourceArmPaginatedResult"]
        """List versions.

        List versions.

        :param name: Container name. This is case-sensitive.
        :type name: str
        :param resource_group_name: The name of the resource group. The name is case insensitive.
        :type resource_group_name: str
        :param workspace_name: Name of Azure Machine Learning workspace.
        :type workspace_name: str
        :param order_by: Ordering of list.
        :type order_by: str
        :param top: Maximum number of records to return.
        :type top: int
        :param skip: Continuation token for pagination.
        :type skip: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either CodeVersionResourceArmPaginatedResult or the
         result of cls(response)
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.mgmt.machinelearningservices.models.CodeVersionResourceArmPaginatedResult]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.CodeVersionResourceArmPaginatedResult"]
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
                    order_by=order_by,
                    top=top,
                    skip=skip,
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
                    order_by=order_by,
                    top=top,
                    skip=skip,
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        def extract_data(pipeline_response):
            deserialized = self._deserialize("CodeVersionResourceArmPaginatedResult", pipeline_response)
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
    list.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions'}  # type: ignore

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

    delete.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions/{version}'}  # type: ignore


    @distributed_trace
    def get(
        self,
        name,  # type: str
        version,  # type: str
        resource_group_name,  # type: str
        workspace_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> "_models.CodeVersionData"
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
        :return: CodeVersionData, or the result of cls(response)
        :rtype: ~azure.mgmt.machinelearningservices.models.CodeVersionData
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.CodeVersionData"]
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

        deserialized = self._deserialize('CodeVersionData', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    get.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions/{version}'}  # type: ignore


    @distributed_trace
    def create_or_update(
        self,
        name,  # type: str
        version,  # type: str
        resource_group_name,  # type: str
        workspace_name,  # type: str
        body,  # type: "_models.CodeVersionData"
        **kwargs  # type: Any
    ):
        # type: (...) -> "_models.CodeVersionData"
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
        :type body: ~azure.mgmt.machinelearningservices.models.CodeVersionData
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: CodeVersionData, or the result of cls(response)
        :rtype: ~azure.mgmt.machinelearningservices.models.CodeVersionData
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.CodeVersionData"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        content_type = kwargs.pop('content_type', "application/json")  # type: Optional[str]

        _json = self._serialize.body(body, 'CodeVersionData')

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
            deserialized = self._deserialize('CodeVersionData', pipeline_response)

        if response.status_code == 201:
            deserialized = self._deserialize('CodeVersionData', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    create_or_update.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/workspaces/{workspaceName}/codes/{name}/versions/{version}'}  # type: ignore

