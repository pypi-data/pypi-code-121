# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from copy import deepcopy
from typing import Any, Awaitable, Optional, TYPE_CHECKING

from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.mgmt.core import AsyncARMPipelineClient
from msrest import Deserializer, Serializer

from .. import models
from ._configuration import AzureMachineLearningWorkspacesConfiguration
from .operations import DeleteOperations, EventsOperations, ExperimentsOperations, MetricOperations, RunArtifactsOperations, RunOperations, RunsOperations, SpansOperations

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential

class AzureMachineLearningWorkspaces:
    """AzureMachineLearningWorkspaces.

    :ivar delete: DeleteOperations operations
    :vartype delete: azure.mgmt.machinelearningservices.aio.operations.DeleteOperations
    :ivar events: EventsOperations operations
    :vartype events: azure.mgmt.machinelearningservices.aio.operations.EventsOperations
    :ivar experiments: ExperimentsOperations operations
    :vartype experiments: azure.mgmt.machinelearningservices.aio.operations.ExperimentsOperations
    :ivar metric: MetricOperations operations
    :vartype metric: azure.mgmt.machinelearningservices.aio.operations.MetricOperations
    :ivar runs: RunsOperations operations
    :vartype runs: azure.mgmt.machinelearningservices.aio.operations.RunsOperations
    :ivar run_artifacts: RunArtifactsOperations operations
    :vartype run_artifacts:
     azure.mgmt.machinelearningservices.aio.operations.RunArtifactsOperations
    :ivar run: RunOperations operations
    :vartype run: azure.mgmt.machinelearningservices.aio.operations.RunOperations
    :ivar spans: SpansOperations operations
    :vartype spans: azure.mgmt.machinelearningservices.aio.operations.SpansOperations
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param base_url: Service URL. Default value is ''.
    :type base_url: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        credential: "AsyncTokenCredential",
        base_url: str = "",
        **kwargs: Any
    ) -> None:
        self._config = AzureMachineLearningWorkspacesConfiguration(credential=credential, **kwargs)
        self._client = AsyncARMPipelineClient(base_url=base_url, config=self._config, **kwargs)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._serialize.client_side_validation = False
        self.delete = DeleteOperations(self._client, self._config, self._serialize, self._deserialize)
        self.events = EventsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.experiments = ExperimentsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.metric = MetricOperations(self._client, self._config, self._serialize, self._deserialize)
        self.runs = RunsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.run_artifacts = RunArtifactsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.run = RunOperations(self._client, self._config, self._serialize, self._deserialize)
        self.spans = SpansOperations(self._client, self._config, self._serialize, self._deserialize)


    def _send_request(
        self,
        request: HttpRequest,
        **kwargs: Any
    ) -> Awaitable[AsyncHttpResponse]:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = await client._send_request(request)
        <AsyncHttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/python/protocol/quickstart

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """

        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, **kwargs)

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "AzureMachineLearningWorkspaces":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)
