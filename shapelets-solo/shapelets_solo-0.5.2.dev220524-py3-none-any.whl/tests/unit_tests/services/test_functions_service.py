# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
import json
import typing
import unittest
from unittest import mock

from shapelets.model import (
    ReplicatedParam,
    FunctionDescription,
    FunctionParameter
)

from shapelets.services.functions_service import FunctionsService


def my_function():
    pass


@mock.patch('inspect.getfullargspec')
@mock.patch('inspect.getsource')
@mock.patch('shapelets.services.functions_service.transform_type')
@mock.patch('shapelets.services.functions_service._wrap_custom_function')
@mock.patch('shapelets.services.functions_service.generate_python_worker')
@mock.patch('shapelets.services.functions_service.FunctionsService.download_dsl')
@mock.patch('requests.post')
class RegisterCustomFunctionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cookies = {"cookie1": "cookie1_value"}
        self.url_base = "url_base"
        self.service = FunctionsService(self.url_base, self.cookies)

    def set_up_mocks(self,
                     post_mock,
                     download_dsl_mock,
                     generate_python_worker_mock,
                     wrap_custom_function_mock,
                     transform_type,
                     get_source_mock,
                     arg_spec_mock):
        arg_spec_mock.return_value.annotations = {
            "param1": "param1_type",
            "param2": "param2_type",
            "return": "return_type"
        }
        arg_spec_mock.return_value.args = ["param1", "param2"]
        get_source_mock.return_value = "source"

        def transform_type_stub(input_type, mode):
            if input_type is int:
                transformed = "transformed_int"
            elif input_type is str:
                transformed = "transformed_str"
            elif (isinstance(input_type, typing._GenericAlias) and
                  input_type.__origin__ is typing.List.__origin__):
                transformed = "LIST"
            elif (isinstance(input_type, typing._GenericAlias) and
                  input_type.__origin__ is ReplicatedParam):
                transformed = "transformed_replicated"
            else:
                transformed = f"transformed_{input_type}"
            return transformed

        def download_dsl_stub():
            pass

        download_dsl_mock.side_effect = download_dsl_stub
        transform_type.side_effect = transform_type_stub
        wrap_custom_function_mock.return_value = "impl_function"
        generate_python_worker_mock.return_value = "worker_function"
        post_mock.return_value.status_code = 200

    def test_register(self,
                      post_mock,
                      download_dsl_mock,
                      generate_python_worker_mock,
                      wrap_custom_function_mock,
                      transform_type,
                      get_source_mock,
                      arg_spec_mock):
        self.set_up_mocks(post_mock,
                          download_dsl_mock,
                          generate_python_worker_mock,
                          wrap_custom_function_mock,
                          transform_type,
                          get_source_mock,
                          arg_spec_mock)
        self.service.register_custom_function(my_function, FunctionDescription("algo", "My algo description"), True)
        generate_python_worker_mock.asser_called_once()
        generate_worker_call = generate_python_worker_mock.call_args[1]
        self.assertEqual("source", generate_worker_call["function_body"])
        self.assertEqual(my_function.__name__, generate_worker_call["function_name"])
        self.assertTrue(
            FunctionParameter(
                "param1", "transformed_param1_type"
            ) in generate_worker_call["parameters"])
        self.assertTrue(
            FunctionParameter(
                "param2", "transformed_param2_type"
            ) in generate_worker_call["parameters"])
        self.assertTrue(isinstance(generate_worker_call["reducer_repl_input_indices"], list))
        self.assertEqual("REGULAR", generate_worker_call["function_type"])
        self.assertEqual(["transformed_return_type"], generate_worker_call["return_types"])
        self.assertEqual(
            post_mock.call_args[1]['url'],
            f"{self.service.base_url}/api/functions/registerfunction")
        self.assertEqual(post_mock.call_args[1]["cookies"], self.cookies)
        data = json.loads(post_mock.call_args[1]["data"])
        function_code = base64.b64decode(data["functionImplementation"]).decode("UTF-8")
        self.assertEqual("worker_function", function_code)
        algorithmSpec = data["algorithmSpecMessage"]
        self.assertEqual("algo", algorithmSpec["algorithmName"])
        self.assertEqual("algo_worker.py", algorithmSpec["implementationFile"])
        self.assertEqual("algo", algorithmSpec["function"])
        self.assertEqual([{"name": "param1", "type": "transformed_param1_type"},
                          {"name": "param2", "type": "transformed_param2_type"}],
                         algorithmSpec["algorithmInputs"])
        self.assertEqual([{"name": "output_0", "type": "transformed_return_type"}],
                         algorithmSpec["algorithmOutputs"])
        self.assertEqual(True, data["force"])

    def test_register_not_force(self,
                                post_mock,
                                download_dsl_mock,
                                generate_python_worker_mock,
                                wrap_custom_function_mock,
                                transform_type,
                                get_source_mock,
                                arg_spec_mock):
        self.set_up_mocks(post_mock,
                          download_dsl_mock,
                          generate_python_worker_mock,
                          wrap_custom_function_mock,
                          transform_type,
                          get_source_mock,
                          arg_spec_mock)
        self.service.register_custom_function(my_function, FunctionDescription("algo", "My algo description"), False)
        data = json.loads(post_mock.call_args[1]["data"])
        self.assertEqual(False, data["force"])

    def test_register_splitter(self,
                               post_mock,
                               download_dsl_mock,
                               generate_python_worker_mock,
                               wrap_custom_function_mock,
                               transform_type,
                               get_source_mock,
                               arg_spec_mock):
        self.set_up_mocks(post_mock,
                          download_dsl_mock,
                          generate_python_worker_mock,
                          wrap_custom_function_mock,
                          transform_type,
                          get_source_mock,
                          arg_spec_mock)
        arg_spec_mock.return_value.annotations = {
            "param1": "param1_type",
            "param2": "param2_type",
            "return": typing.Tuple[int, str]
        }
        self.service.register_custom_splitter(my_function, FunctionDescription("algo", "My algo description"), True)
        generate_python_worker_mock.asser_called_once()
        generate_worker_call = generate_python_worker_mock.call_args[1]
        self.assertEqual("source", generate_worker_call["function_body"])
        self.assertEqual(my_function.__name__, generate_worker_call["function_name"])
        self.assertTrue(
            FunctionParameter(
                "param1", "transformed_param1_type"
            ) in generate_worker_call["parameters"])
        self.assertTrue(
            FunctionParameter(
                "param2", "transformed_param2_type"
            ) in generate_worker_call["parameters"])
        self.assertTrue(isinstance(generate_worker_call["reducer_repl_input_indices"], list))
        self.assertEqual("SPLITTER", generate_worker_call["function_type"])
        self.assertEqual(
            ["transformed_int", "transformed_str"], generate_worker_call["return_types"])
        self.assertEqual(
            post_mock.call_args[1]['url'], f"{self.service.base_url}/api/functions/registersplitter")
        self.assertEqual(post_mock.call_args[1]["cookies"], self.cookies)
        data = json.loads(post_mock.call_args[1]["data"])
        function_code = base64.b64decode(data["functionImplementation"]).decode("UTF-8")
        self.assertEqual("worker_function", function_code)
        algorithmSpec = data["algorithmSpecMessage"]
        self.assertEqual("algo", algorithmSpec["algorithmName"])
        self.assertEqual("algo_worker.py", algorithmSpec["implementationFile"])
        self.assertEqual("algo", algorithmSpec["function"])
        self.assertEqual([{"name": "param1", "type": "transformed_param1_type"},
                          {"name": "param2", "type": "transformed_param2_type"}],
                         algorithmSpec["algorithmInputs"])
        self.assertEqual([{"name": "output_0", "type": "transformed_int"},
                          {"name": "output_1", "type": "transformed_str"}],
                         algorithmSpec["algorithmOutputs"])
        self.assertEqual(True, data["force"])

    def test_register_reducer(self,
                              post_mock,
                              download_dsl_mock,
                              generate_python_worker_mock,
                              wrap_custom_function_mock,
                              transform_type,
                              get_source_mock,
                              arg_spec_mock):
        self.set_up_mocks(post_mock,
                          download_dsl_mock,
                          generate_python_worker_mock,
                          wrap_custom_function_mock,
                          transform_type,
                          get_source_mock,
                          arg_spec_mock)
        arg_spec_mock.return_value.annotations = {
            "param1": "param1_type",
            "param3": ReplicatedParam[str],
            "param2": ReplicatedParam[int],
            "return": "return_type"
        }
        arg_spec_mock.return_value.args = ["param1", "param2", "param3"]
        self.service.register_custom_reducer(my_function, FunctionDescription("algo", "My algo description"), True)
        generate_python_worker_mock.asser_called_once()
        generate_worker_call = generate_python_worker_mock.call_args[1]
        self.assertEqual("source", generate_worker_call["function_body"])
        self.assertEqual(my_function.__name__, generate_worker_call["function_name"])
        self.assertTrue(FunctionParameter("param1", "transformed_param1_type") in generate_worker_call["parameters"])
        self.assertTrue(FunctionParameter("param2", "transformed_replicated") in generate_worker_call["parameters"])
        self.assertTrue(FunctionParameter("param3", "transformed_replicated") in generate_worker_call["parameters"])
        self.assertEqual([1, 2], generate_worker_call["reducer_repl_input_indices"])
        self.assertEqual("REDUCER", generate_worker_call["function_type"])
        self.assertEqual(["transformed_return_type"], generate_worker_call["return_types"])
        self.assertEqual(post_mock.call_args[1]['url'], f"{self.service.base_url}/api/functions/registerreducer")
        self.assertEqual(post_mock.call_args[1]["cookies"], self.cookies)
        data = json.loads(post_mock.call_args[1]["data"])
        function_code = base64.b64decode(data["functionImplementation"]).decode("UTF-8")
        self.assertEqual("worker_function", function_code)
        algorithmSpec = data["algorithmSpecMessage"]
        self.assertEqual("algo", algorithmSpec["algorithmName"])
        self.assertEqual("algo_worker.py", algorithmSpec["implementationFile"])
        self.assertEqual("algo", algorithmSpec["function"])
        self.assertEqual([{"name": "param1", "type": "transformed_param1_type"},
                          {"name": "param2", "type": "transformed_replicated"},
                          {"name": "param3", "type": "transformed_replicated"}],
                         algorithmSpec["algorithmInputs"])
        self.assertEqual([{"name": "output_0", "type": "transformed_return_type"}],
                         algorithmSpec["algorithmOutputs"])
        self.assertEqual(True, data["force"])

    def test_register_exception(self,
                                post_mock,
                                download_dsl_mock,
                                generate_python_worker_mock,
                                wrap_custom_function_mock,
                                transform_type,
                                get_source_mock,
                                arg_spec_mock):
        self.set_up_mocks(
            post_mock,
            download_dsl_mock,
            generate_python_worker_mock,
            wrap_custom_function_mock,
            transform_type,
            get_source_mock,
            arg_spec_mock)
        post_mock.return_value.status_code = 500
        self.service.register_custom_function(my_function, FunctionDescription("algo", "My algo description"), False)
        post_mock.return_value.raise_for_status.assert_called_once()
