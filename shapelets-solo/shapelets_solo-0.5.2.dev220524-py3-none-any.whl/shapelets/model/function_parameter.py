# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import typing


class FunctionType(Enum):
    REGULAR = "REGULAR"
    SPLITTER = "SPLITTER"
    REDUCER = "REDUCER"


class AttributeNames(Enum):
    CORRELATION = "correlation"
    FUNCTION_NAME = "functionName"
    ID = "id"
    INPUTS = "inputs"
    MATCH = "Match"
    NAME = "name"
    OUTPUTS = "outputs"
    PROPERTIES = "properties"
    TYPE = "type"
    VIEW_GROUP_ENTRY = "ViewGroupEntry"


class FunctionParameter:
    def __init__(self, name: str, param_type: str):
        self.name = name
        self.param_type = param_type

    def __hash__(self):
        return hash((self.name, self.param_type))

    def __eq__(self, other):
        return (isinstance(other, FunctionParameter) and
                self.name == other.name and
                self.param_type == other.param_type)


class FunctionParametersDescription:
    def __init__(self, name: str,
                 inputs=None,
                 outputs=None
                 ):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs

    def to_dict(self):
        res = {
            AttributeNames.NAME.value: self.name,
            AttributeNames.INPUTS.value: self.__extract_inputs(),
            AttributeNames.OUTPUTS.value: self.__extract_outputs()
        }
        return res

    @staticmethod
    def generate_params(params) -> typing.List[FunctionParameter]:
        params_list = []
        for param in params:
            params_list.append(FunctionParameter(name=param[AttributeNames.NAME.value],
                                                 param_type=param[AttributeNames.TYPE.value]))
        return params_list

    @staticmethod
    def from_dict(dict_info):
        return FunctionParametersDescription(
            name=dict_info[AttributeNames.FUNCTION_NAME.value],
            inputs=FunctionParametersDescription.generate_params(dict_info[AttributeNames.INPUTS.value]),
            outputs=FunctionParametersDescription.generate_params(dict_info[AttributeNames.OUTPUTS.value])
        )

    def __extract_inputs(self):
        return [{{AttributeNames.NAME.value}: input.name,
                 {AttributeNames.TYPE.value}: input.param_type} for input in self.inputs]

    def __extract_outputs(self):
        return [{{AttributeNames.NAME.value}: f"output_{i}",
                 AttributeNames.TYPE.value: output} for i, output in enumerate(self.outputs)]
