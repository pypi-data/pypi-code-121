# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import json
import typing

from shapelets.dsl import (
    SupportedTypes,
    ArgumentTypeEnum,
    ArgumentValue,
    Connection,
    collapse_into_graph,
    ensure_iterable,
    ordered_output_connections,
    NodeReturnType
)
from shapelets.model import Sequence
from shapelets.services.base_service import BaseService
from shapelets.services.sequences_service import Endpoint as SequenceEndpoint
from shapelets.services.exceptions import ExecutionException


class TaskOutput:
    def __init__(self, connection: Connection, value: typing.Any):
        self.connection = connection
        self.value = value


class Endpoint(Enum):
    EXECUTIONS = "api/executions"
    RUN = f"{EXECUTIONS}/run"
    RUN_ASYNC = f"{EXECUTIONS}/runAsync"
    JOB_RESULT_BY_ID = f"{EXECUTIONS}/jobs/###job_id###/result"
    ANALYSIS = f"{EXECUTIONS}/analysis"
    EXECUTIONS_FLOW = f"{EXECUTIONS}/flow"
    EXECUTIONS_ANALYSIS = f"{EXECUTIONS}/analysis"
    EXECUTIONS_ANALYSIS_BY_NAME = f"{EXECUTIONS_ANALYSIS}/###analysis-name###"

    def replace(self, job_id: int) -> str:
        template = str(self.value)
        return template.replace("###job_id###", str(job_id))

    def replace_name(self, analysis_name: str) -> str:
        template = str(self.value)
        return template.replace("###analysis-name###", analysis_name)


class ExecutionService(BaseService):

    def run_and_wait_for_all(self, output_nodes: NodeReturnType) -> SupportedTypes:
        task_response = self.__run_graph(Endpoint.RUN.value, output_nodes)
        result = task_response["result"]
        task_response = json.loads(result)
        return self.__generate_task_response(task_response["outputs"])

    def run_async(self, output_nodes: NodeReturnType) -> int:
        return self.__run_graph(Endpoint.RUN_ASYNC.value, output_nodes)["id"]

    def wait_for_result(self, job_id: int) -> SupportedTypes:
        task_response = self.request_get(
            Endpoint.JOB_RESULT_BY_ID.replace(job_id),
            ExecutionException,
            timeout_seconds=1000000)
        result = task_response["result"]
        task_response = json.loads(result)
        return self.__generate_task_response(task_response["outputs"])

    def get_all_analysis(self) -> typing.List[str]:
        response = self.request_get(
            Endpoint.ANALYSIS.value,
            ExecutionException,
            timeout_seconds=1000000)
        analysis_names = []
        for analysis in response:
            analysis_names.append(analysis["name"])
        return analysis_names

    def __generate_task_response(self, task_outputs: typing.List[TaskOutput]):
        if len(task_outputs) == 1:
            return self.__extract_output_from_task(task_outputs[0])
        return [self.__extract_output_from_task(x) for x in task_outputs]

    def __extract_output_from_task(self, output: ArgumentValue) -> SupportedTypes:
        if output["type"] == ArgumentTypeEnum.SEQUENCE.value:
            seq_id = output["sequence"]["id"]
            sequence = self.request_get(SequenceEndpoint.SEQUENCE_BY_ID.replace(seq_id))
            return Sequence.from_dict(sequence)
        if output["type"] == ArgumentTypeEnum.MATCH.value:
            seq_id = output["match"]["view"]["sequence_id"]
            del output["match"]["view"]["sequence_id"]
            sequence = self.request_get(SequenceEndpoint.SEQUENCE_BY_ID.replace(seq_id))
            output["match"]["view"]["sequence"] = Sequence.from_dict(sequence)
        if output["type"] == ArgumentTypeEnum.VIEW.value:
            seq_id = output["view"]["sequence_id"]
            del output["view"]["sequence_id"]
            sequence = self.request_get(SequenceEndpoint.SEQUENCE_BY_ID.replace(seq_id))
            output["view"]["sequence"] = Sequence.from_dict(sequence)
        if output["type"] == ArgumentTypeEnum.LIST.value:
            return [self.__extract_output_from_task(inner) for inner in output["list"]]
        return ArgumentValue.from_dict(output).arg_value

    def __run_graph(self, api_endpoint: str, output_nodes: NodeReturnType) -> \
            typing.Dict[str, SupportedTypes]:
        nodes = ensure_iterable(output_nodes)
        graph_dict = collapse_into_graph(nodes).to_dict()
        output_connections = ordered_output_connections(nodes)
        return self.request_post(
            api_endpoint,
            {
                "graph": graph_dict,
                "connections_order": output_connections
            },
            ExecutionException,
            timeout_seconds=1000000)
