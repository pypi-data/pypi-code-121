#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Author: Komal Thareja (kthare10@renci.org)
import enum
from datetime import datetime
from typing import Tuple, Union, List

from fim.user import GraphFormat

from fabric_cf.orchestrator import swagger_client
from fim.user.topology import ExperimentTopology, AdvertizedTopology

from fabric_cf.orchestrator.swagger_client import Sliver, Slice


class OrchestratorProxyException(Exception):
    """
    Orchestrator Exceptions
    """
    pass


class SliceState(enum.Enum):
    Nascent = enum.auto()
    Configuring = enum.auto()
    StableError = enum.auto()
    StableOK = enum.auto()
    Closing = enum.auto()
    Dead = enum.auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def state_from_str(state: str):
        if state is None:
            return state

        for t in SliceState:
            if state == str(t):
                return t

        return None

    @staticmethod
    def state_list_to_str_list(states: list):
        if states is None:
            return states

        result = []
        for t in states:
            result.append(str(t))

        return result


@enum.unique
class Status(enum.Enum):
    OK = 1
    INVALID_ARGUMENTS = 2
    FAILURE = 3

    def interpret(self, exception=None):
        interpretations = {
            1: "Success",
            2: "Invalid Arguments",
            3: "Failure"
          }
        if exception is None:
            return interpretations[self.value]
        else:
            return str(exception) + ". " + interpretations[self.value]


class OrchestratorProxy:
    """
    Orchestrator Proxy; must specify the orchestrator host details when instantiating the proxy object
    """
    PROP_AUTHORIZATION = 'Authorization'
    PROP_BEARER = 'Bearer'
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"

    def __init__(self, orchestrator_host: str):
        self.host = orchestrator_host
        self.tokens_api = None
        if orchestrator_host is not None:
            # create_slices an instance of the API class
            configuration = swagger_client.configuration.Configuration()
            configuration.verify_ssl = False
            configuration.host = f"http://{orchestrator_host}/"
            api_instance = swagger_client.ApiClient(configuration)
            self.slices_api = swagger_client.SlicesApi(api_client=api_instance)
            self.slivers_api = swagger_client.SliversApi(api_client=api_instance)
            self.resources_api = swagger_client.ResourcesApi(api_client=api_instance)

    def __set_tokens(self, *, token: str):
        """
        Set tokens
        @param token token
        """
        # Set the tokens
        self.slices_api.api_client.configuration.api_key[self.PROP_AUTHORIZATION] = token
        self.slices_api.api_client.configuration.api_key_prefix[self.PROP_AUTHORIZATION] = self.PROP_BEARER

    def create(self, *, token: str, slice_name: str, ssh_key: str, topology: ExperimentTopology = None,
               slice_graph: str = None, lease_end_time: str = None) -> Tuple[Status, Union[Exception, List[Sliver]]]:
        """
        Create a slice
        @param token fabric token
        @param slice_name slice name
        @param ssh_key SSH Key
        @param topology Experiment topology
        @param slice_graph Slice Graph string
        @param lease_end_time Lease End Time
        @return Tuple containing Status and Exception/Json containing slivers created
        """
        if token is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token} must be specified")

        if slice_name is None:
            return Status.INVALID_ARGUMENTS, \
                   OrchestratorProxyException(f"Slice Name {slice_name} must be specified")

        if (topology is None and slice_graph is None) or (topology is not None and slice_graph is not None):
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Either topology {topology} or "
                                                                        f"slice graph {slice_graph} must "
                                                                        f"be specified")

        if lease_end_time is not None:
            try:
                datetime.strptime(lease_end_time, self.TIME_FORMAT)
            except Exception as e:
                return Status.INVALID_ARGUMENTS, OrchestratorProxyException(
                    f"Lease End Time {lease_end_time} should be in format: {self.TIME_FORMAT}")

        try:
            # Set the tokens
            self.__set_tokens(token=token)

            if topology is not None:
                slice_graph = topology.serialize()

            response = None
            if lease_end_time is not None:
                slivers = self.slices_api.slices_create_post(name=slice_name, body=slice_graph, ssh_key=ssh_key,
                                                             lease_end_time=lease_end_time)
            else:
                slivers = self.slices_api.slices_create_post(name=slice_name, body=slice_graph, ssh_key=ssh_key)

            return Status.OK, slivers.data if slivers.data is not None else []
        except Exception as e:
            return Status.FAILURE, e

    def delete(self, *, token: str, slice_id: str) -> Tuple[Status, Union[Exception, None]]:
        """
        Delete a slice
        @param token fabric token
        @param slice_id slice id
        @return Tuple containing Status and Exception/Json containing deletion status
        """
        if token is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token} must be specified")

        if slice_id is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Slice Id {slice_id} must be specified")

        try:
            # Set the tokens
            self.slices_api.api_client.configuration.api_key['Authorization'] = token
            self.slices_api.api_client.configuration.api_key_prefix['Authorization'] = 'Bearer'

            self.slices_api.slices_delete_slice_id_delete(slice_id=slice_id)
            return Status.OK, None
        except Exception as e:
            return Status.FAILURE, e

    def slices(self, *, token: str, includes: List[SliceState] = None, excludes: List[SliceState] = None,
               name: str = None, limit: int = 20, offset: int = 0) -> Tuple[Status, Union[Exception, List[Slice]]]:
        """
        Get slices
        @param token fabric token
        @param includes list of the slice state used to include the slices in the output
        @param excludes list of the slice state used to exclude the slices from the output
        @param name name of the slice
        @param limit maximum number of slices to return
        @param offset offset of the first slice to return
        @return Tuple containing Status and Exception/Json containing slices
        """
        if token is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token} must be specified")

        try:
            # Set the tokens
            self.__set_tokens(token=token)

            states = [SliceState.StableError, SliceState.StableOK, SliceState.Nascent,
                      SliceState.Configuring, SliceState.Closing, SliceState.Dead]
            if includes is not None:
                states = includes

            if excludes is not None:
                for x in excludes:
                    if x in states:
                        states.remove(x)

            if name is not None:
                slices = self.slices_api.slices_get(states=SliceState.state_list_to_str_list(states), name=name,
                                                    limit=limit, offset=offset)
            else:
                slices = self.slices_api.slices_get(states=SliceState.state_list_to_str_list(states), limit=limit,
                                                    offset=offset)

            return Status.OK, slices.data if slices.data is not None else []
        except Exception as e:
            return Status.FAILURE, e

    def get_slice(self, *, token: str, slice_id: str = None,
                  graph_format: GraphFormat = GraphFormat.GRAPHML) -> Tuple[Status,
                                                                            Union[Exception, ExperimentTopology, dict]]:
        """
        Get slice
        @param token fabric token
        @param slice_id slice id
        @param graph_format
        @return Tuple containing Status and Exception/Json containing slice
        """
        if token is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token} must be specified")

        if slice_id is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Slice Id {slice_id} must be specified")

        try:
            # Set the tokens
            self.__set_tokens(token=token)

            slice_details = self.slices_api.slices_slice_id_get(slice_id=slice_id, graph_format=graph_format.name)

            model = slice_details.data[0].model if slice_details.data is not None else None
            topology = None
            if model is not None:
                topology = ExperimentTopology()
                topology.load(graph_string=model)

            return Status.FAILURE, topology
        except Exception as e:
            return Status.FAILURE, e

    def slivers(self, *, token: str, slice_id: str,
                sliver_id: str = None) -> Tuple[Status, Union[Exception, List[Sliver]]]:
        """
        Get slivers
        @param token fabric token
        @param slice_id slice id
        @param sliver_id slice sliver_id
        @return Tuple containing Status and Exception/Json containing Sliver(s)
        """
        if token is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token} must be specified")

        if slice_id is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Slice Id {slice_id} must be specified")

        try:
            # Set the tokens
            self.__set_tokens(token=token)

            if sliver_id is None:
                slivers = self.slivers_api.slivers_get(slice_id=slice_id)
            else:
                slivers = self.slivers_api.slivers_sliver_id_get(slice_id=slice_id, sliver_id=sliver_id)

            return Status.OK, slivers.data if slivers.data is not None else []
        except Exception as e:
            return Status.FAILURE, e

    def resources(self, *, token: str, level: int = 1) -> Tuple[Status, Union[Exception, AdvertizedTopology]]:
        """
        Get resources
        @param token fabric token
        @param level level
        @return Tuple containing Status and Exception/Json containing Resources
        """

        if token is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token} must be specified")

        try:
            # Set the tokens
            self.__set_tokens(token=token)

            resources = self.resources_api.resources_get(level=level)
            graph_string = resources.data[0].model
            substrate = None
            if graph_string is not None:
                substrate = AdvertizedTopology()
                substrate.load(graph_string=graph_string)

            return Status.OK, substrate
        except Exception as e:
            return Status.FAILURE, e

    def portal_resources(self, *, graph_format: GraphFormat = GraphFormat.JSON_NODELINK) -> Tuple[Status, Union[Exception, AdvertizedTopology]]:
        """
        Get resources for portal
        @param graph_format Graph Format
        @return Tuple containing Status and Exception/Json containing Resources
        """

        try:
            resources = self.resources_api.portalresources_get(graph_format=graph_format.name)

            graph_string = resources.data[0].model
            substrate = None
            if graph_string is not None:
                substrate = AdvertizedTopology()
                substrate.load(graph_string=graph_string)

            return Status.OK, substrate
        except Exception as e:
            return Status.FAILURE, e

    def renew(self, *, token: str, slice_id: str,
              new_lease_end_time: str) -> Tuple[Status, Union[Exception, List, None]]:
        """
        Renew a slice
        @param token fabric token
        @param slice_id slice_id
        @param new_lease_end_time new_lease_end_time
        @return Tuple containing Status and List of Reservation Id failed to extend
        """
        if token is None or slice_id is None or new_lease_end_time is None:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Token {token}, Slice Id: {slice_id}, "
                                                                        f"New Lease End Time {new_lease_end_time} "
                                                                        f"must be specified")

        try:
            datetime.strptime(new_lease_end_time, self.TIME_FORMAT)
        except Exception as e:
            return Status.INVALID_ARGUMENTS, OrchestratorProxyException(f"Lease End Time {new_lease_end_time} should "
                                                                        f"be in format: {self.TIME_FORMAT}")

        try:
            # Set the tokens
            self.__set_tokens(token=token)

            self.slices_api.slices_renew_slice_id_post(slice_id=slice_id, lease_end_time=new_lease_end_time)

            return Status.OK, None
        except Exception as e:
            return Status.FAILURE, e
