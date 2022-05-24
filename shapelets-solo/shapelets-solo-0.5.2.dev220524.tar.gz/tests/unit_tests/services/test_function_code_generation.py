# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
from unittest import mock

from shapelets.model import FunctionParameter

from shapelets.services.functions_service import (
    generate_python_worker,
    _wrap_custom_function
)


class CodeGeneration(unittest.TestCase):
    @mock.patch('shapelets.services.functions_service._wrap_custom_function')
    @mock.patch('jinja2.Template')
    def test_generate_python_worker(self,
                                    mock_template,
                                    mock_wrap_custom_function):
        render_mock = mock.MagicMock(return_value="rendered")
        mock_template.return_value.render = render_mock
        mock_wrap_custom_function.return_value = "body"
        data = {
            "function_name": "name",
            "argument_list": [FunctionParameter("name", "type")],
            "result_types": ["type1", "type2"],
            "reducer_repl_input_indices": [2],
            "function_type": "func_type"
        }
        rendered = generate_python_worker(
            function_body="body",
            function_name=data["function_name"],
            parameters=data["argument_list"],
            reducer_repl_input_indices=data["reducer_repl_input_indices"],
            function_type=data["function_type"],
            return_types=data["result_types"]
        )
        self.assertEqual(rendered, "rendered")
        mock_template.assert_called_with("body")
        render_mock.assert_called_with(data)

    ###########################################################################

    def test_generate_implementation_function(self):
        with mock.patch('builtins.open', mock.mock_open(read_data="read")):
            generated = _wrap_custom_function("name", " empty")
        self.assertEqual(generated, "read empty")

    ###########################################################################

    def test_generate_implementation_function_with_all_replacements(self):
        source = """

import shapelets.model.Sequence
def name(input1: int, input2: int) -> str:
    pass 
        """
        expected = """read


def name_wrapped({{ argument_list | map(attribute='name') | join(', ') }}):
    pass 
        """
        with mock.patch('builtins.open', mock.mock_open(read_data="read")):
            generated = _wrap_custom_function("name", source)
        self.assertEqual(expected, generated)

    def test_generate_implementation_function_with_all_replacements_whitespaces(self):
        source = """

import shapelets.model.Sequence
def   name (  input1: int, input2: int)   -> str  :
    pass 
        """
        expected = """read


def name_wrapped({{ argument_list | map(attribute='name') | join(', ') }}):
    pass 
        """
        with mock.patch('builtins.open', mock.mock_open(read_data="read")):
            generated = _wrap_custom_function("name", source)
        self.assertEqual(expected, generated)

    ###########################################################################

    def test_generate_implementation_function_with_multiline(self):
        source = """

import shapelets.model.Sequence
def   name (  
            input1: int, 
            input2: int
            )   -> str  :
    pass 
        """
        expected = """read


def name_wrapped({{ argument_list | map(attribute='name') | join(', ') }}):
    pass 
        """
        with mock.patch('builtins.open', mock.mock_open(read_data="read")):
            generated = _wrap_custom_function("name", source)
        self.assertEqual(expected, generated)
