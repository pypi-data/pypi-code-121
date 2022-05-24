# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
from enum import Enum
import importlib
import inspect
import os
import re
import typing
import jinja2
import json

import shapelets.dsl as dsl
from shapelets.dsl import (
    dsl_op,
    collapse_into_graph,
    NodeReturnType,
    ensure_iterable
)
from shapelets.model import (
    FunctionDescription,
    FunctionParameter,
    FunctionParametersDescription,
    FunctionType,
    ReplicatedParam
)
from shapelets.services.py2backend_type_adapter import (
    TransformMode,
    transform_type
)
from shapelets.services.base_service import BaseService
from shapelets.services.execution_service import Endpoint as ExecutionEndpoint


def generate_python_worker(
        function_body: str,
        function_name: str,
        parameters: typing.List[FunctionParameter],
        reducer_repl_input_indices: typing.List[int],
        function_type: str,
        return_types: typing.List[str]):
    return jinja2.Template(_wrap_custom_function(function_name, function_body)).render({
        "function_name": function_name,
        "argument_list": parameters,
        "result_types": return_types,
        "reducer_repl_input_indices": reducer_repl_input_indices,
        "function_type": function_type
    })


class Endpoint(Enum):
    DSL_OP = f"{ExecutionEndpoint.EXECUTIONS.value}/pythonDSL"
    USER_FUNCTIONS = "api/functions"
    USER_FUNCTION_NAMES = f"{USER_FUNCTIONS}/###name###"
    REGISTER_REGULAR = f"{USER_FUNCTIONS}/registerfunction"
    REGISTER_SPLITTER = f"{USER_FUNCTIONS}/registersplitter"
    REGISTER_REDUCER = f"{USER_FUNCTIONS}/registerreducer"

    def replace(self, name: str):
        template = str(self.value)
        return template.replace("###name###", name)


_REGISTER_FUNCTION_ENDPOINTS = {
    FunctionType.REGULAR: Endpoint.REGISTER_REGULAR.value,
    FunctionType.SPLITTER: Endpoint.REGISTER_SPLITTER.value,
    FunctionType.REDUCER: Endpoint.REGISTER_REDUCER.value
}


class FunctionsService(BaseService):

    def register_custom_function(self,
                                 custom_function: typing.Callable,
                                 description: FunctionDescription = None,
                                 force: bool = True,
                                 persist_results: bool = True):
        """
        This function registers a new function in the system.
        :param custom_function: The function to be registered.
        :param description: The description of hte function.
        :param force: Force overwriting the function if there is one function with this name already registered.
        :param persist_results: Indicates if the results of the function has to be cached.
        """
        self._register_function(
            FunctionType.REGULAR, custom_function, description, force, persist_results)

    def register_custom_splitter(self,
                                 custom_function: typing.Callable,
                                 description: FunctionDescription = None,
                                 force: bool = True,
                                 persist_results: bool = True):
        """
        This function registers a new Splitter user function in the system.
        :param custom_function: The function to be registered.
        :param description: The description of hte function.
        :param force: Force overwriting the function if there is one function with this name already registered.
        :param persist_results: Indicates if the results of the function has to be cached.
        """
        self._register_function(
            FunctionType.SPLITTER, custom_function, description, force, persist_results)

    def register_custom_reducer(self,
                                custom_function: typing.Callable,
                                description: FunctionDescription = None,
                                force: bool = True,
                                persist_results: bool = True):
        """
        This function registers a new User function in the system.
        :param custom_function: The function to be registered.
        :param description: The description of hte function.
        :param force: Force overwriting the function if there is one function with this name already registered.
        :param persist_results: Indicates if the results of the function has to be cached.
        """
        self._register_function(
            FunctionType.REDUCER, custom_function, description, force, persist_results)

    def register_flow(self,
                      name: str,
                      documentation: str,
                      output_nodes: NodeReturnType,
                      output_names: typing.Optional[typing.List[str]],
                      persist_results: bool = True):
        """
        This function registers a new Flow  in the system.
        :param name: The function name to be registered.
        :param documentation: The doc string of the function.
        :param output_nodes: The output nodes of the function.
        :param output_names: The names of the output nodes of the function (in the same order).
        :param persist_results: Indicates if the results of the function has to be cached.
        """
        self.__register(name,
                        documentation,
                        output_nodes,
                        output_names,
                        ExecutionEndpoint.EXECUTIONS_FLOW.value,
                        "flowName",
                        persist_results)

    def register_analysis(self,
                          name: str,
                          documentation: str,
                          output_nodes: NodeReturnType,
                          output_names: typing.Optional[typing.List[str]],
                          persist_results: bool = True):
        """
        This function registers a new Analysis  in the system.
        :param name: The function name to be registered.
        :param output_nodes: The output nodes of the function.
        :param output_names: The names of the output nodes of the function (in the same order).
        :param persist_results: Indicates if the results of the function has to be cached.
        """
        self.__register(name,
                        documentation,
                        output_nodes,
                        output_names,
                        ExecutionEndpoint.EXECUTIONS_ANALYSIS.value,
                        "analysisName",
                        persist_results)

    def delete_analysis(self, name: str):
        self.request_delete(ExecutionEndpoint.EXECUTIONS_ANALYSIS_BY_NAME.replace_name(name))
        self.download_dsl()

    def delete_all_analysis(self):
        self.request_delete(ExecutionEndpoint.EXECUTIONS_ANALYSIS.value)
        self.download_dsl()

    def download_dsl(self):
        dsl_str = self.request_get(Endpoint.DSL_OP.value, raw_content=True).decode("utf-8")
        output_folder = os.path.dirname(dsl_op.__file__)
        if not os.access(output_folder, os.W_OK):
            raise PermissionError("pyShapelets doesn't have writing permissions in the lib folder")
        output_path = os.path.join(output_folder, "dsl_op.py")
        with open(output_path, "w") as text_file:
            text_file.write(dsl_str)
        importlib.reload(dsl_op)

    def get_function_parameters(self, name: str = None):
        if name is not None:
            url = Endpoint.USER_FUNCTION_NAMES.replace(name)
            response = json.loads(self.request_get(url, raw_content=True))
            return FunctionParametersDescription.from_dict(response)
        else:
            url = Endpoint.USER_FUNCTIONS.value
            description_list = []
            function_list = json.loads(self.request_get(url, raw_content=True))
            for function in function_list:
                description_list.append(FunctionParametersDescription.from_dict(function))
            return description_list


    def __register(self,
                   name: str,
                   documentation: str,
                   output_nodes: NodeReturnType,
                   output_names: typing.Optional[typing.List[str]],
                   api_endpoint: str,
                   param_name: str,
                   persist_results: bool = True):
        nodes = ensure_iterable(output_nodes)
        if not output_names:
            output_names = [f"output{i}" for i in range(len(nodes))]
        graph_dict = collapse_into_graph(nodes, output_names).to_dict()
        self.request_post(
            api_endpoint,
            {
                param_name: name,
                "documentation": documentation,
                "graph": graph_dict,
                "force": True,
                "cacheableResults": persist_results
            }
        )
        self.download_dsl()

    def _register_function(self,
                           function_type: FunctionType,
                           custom_function: typing.Callable,
                           description: FunctionDescription = None,
                           force: bool = True,
                           persist_results: bool = True):
        function_name = custom_function.__name__
        param_annotations = _param_annotations(custom_function)

        doc_extracted = inspect.getdoc(custom_function)
        if doc_extracted is None:
            documentation = "Documentation not available for this function."
        else:
            documentation = doc_extracted

        backend_output_types, worker_output_types = _return_annotations(custom_function)
        self.request_post(
            _REGISTER_FUNCTION_ENDPOINTS[function_type],
            {
                "algorithmSpecMessage": _algorithmic_spec(
                    function_name,
                    documentation,
                    param_annotations,
                    backend_output_types,
                    description,
                    persist_results
                ),
                "functionImplementation": _base64_encode(generate_python_worker(
                    function_body=inspect.getsource(custom_function),
                    function_name=function_name,
                    parameters=_parameters(param_annotations, TransformMode.SHAPELETS_WORKER),
                    reducer_repl_input_indices=_replicated_input_indices(function_type, param_annotations),
                    function_type=function_type.value,
                    return_types=worker_output_types)),
                "force": force
            })
        self.download_dsl()


def _wrap_custom_function(function_name: str, source: str) -> str:
    jinja_arguments = "{{ argument_list | map(attribute='name') | join(', ') }}"
    fun = re.sub(f"def\\s+{function_name}.*?\\(.*?\\).*?:",
                 f"def {function_name}_wrapped({jinja_arguments}):",
                 source,
                 flags=re.MULTILINE | re.DOTALL)
    fun = re.sub("import shapelets.model.Sequence", "", fun)
    with open(f"{os.path.dirname(dsl.__file__)}/resources/function_impl_tpt.jinja", 'r') as file:
        template_function = file.read()
    return template_function + fun


def _base64_encode(text: str) -> str:
    return base64.b64encode(bytes(text, encoding="utf-8")).decode("utf-8")


def _return_annotations(function: typing.Callable) -> typing.Tuple[typing.List[str], typing.List[str]]:
    ret = inspect.getfullargspec(function).annotations["return"]
    if (isinstance(ret, typing._GenericAlias) and  # pylint: disable=W0212
            ret.__origin__ == typing.Tuple.__origin__):
        args = ret.__args__
    else:
        args = [ret]
    backend_output_types = [transform_type(arg, TransformMode.KOTLIN) for arg in args]
    worker_output_types = [transform_type(arg, TransformMode.SHAPELETS_WORKER) for arg in args]
    return backend_output_types, worker_output_types


InputParamAnnotations = typing.List[typing.Tuple[str, type]]


def _algorithmic_spec(function_name: str,
                      documentation: str,
                      param_annotations: InputParamAnnotations,
                      outputs: typing.List[str],
                      description: FunctionDescription = None,
                      persist_results: bool = True) -> typing.Dict:
    if description is None:
        description = FunctionDescription(function_name, documentation, cacheable_result=persist_results)
    description.inputs = _parameters(param_annotations, TransformMode.KOTLIN)
    description.outputs = outputs
    return description.to_dict()


def _param_annotations(function: typing.Callable) -> InputParamAnnotations:
    full_arg_spec = inspect.getfullargspec(function)
    function_param_annotations = full_arg_spec.annotations
    function_param_names = full_arg_spec.args
    return [(name, function_param_annotations[name]) for name in function_param_names]


def _parameters(param_annotations: InputParamAnnotations,
                mode: TransformMode) -> typing.List[FunctionParameter]:
    return [FunctionParameter(name, transform_type(param, mode)) for name, param in param_annotations]


def _replicated_input_indices(function_type: FunctionType, param_annotations: InputParamAnnotations):
    replicated_input_indices = []
    if function_type == FunctionType.REDUCER:
        for i, param in enumerate(param_annotations):
            if (isinstance(param[1], typing._GenericAlias) and  # pylint: disable=W0212
                    param[1].__origin__ is ReplicatedParam):
                replicated_input_indices.append(i)
    return replicated_input_indices
