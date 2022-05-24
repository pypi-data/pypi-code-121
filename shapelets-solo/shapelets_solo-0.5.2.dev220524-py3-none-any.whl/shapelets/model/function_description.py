# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum


class FunctionComplexity(Enum):
    CONSTANT = "CONSTANT"
    LINEAR = "LINEAR"
    LINEAR_LOGARITHMIC = "LINEARLOGARITHMIC"
    LOGARITHMIC = "LOGARITHMIC"
    QUADRATIC = "QUADRATIC"
    CUBIC = "CUBIC"


class AttributeNames(Enum):
    ALGORITHM_INPUTS = 'algorithmInputs'
    ALGORITHM_NAME = 'algorithmName'
    ALGORITHM_DOC = 'documentation'
    ALGORITHM_OUTPUTS = 'algorithmOutputs'
    CACHEABLE_RESULT = 'cacheableResult'
    CPU_ACTIVATION = 'cpuActivation'
    CPU_CORES = 'cpuCores'
    FUNCTION = 'function'
    GPU_ACTIVATION = 'gpuActivation'
    IMPLEMENTATION_FILE = 'implementationFile'
    MEMORY_COMPLEXITY = 'memoryComplexity'
    NAME = "name"
    PYTHON = "PYTHON"
    TIME_COMPLEXITY = 'timeComplexity'
    TYPE = "type"


class FunctionDescription:
    def __init__(self,
                 algorithm_name,
                 documentation,
                 implementation_file=None,
                 function_name=None,
                 inputs=None,
                 outputs=None,
                 time_complexity=FunctionComplexity.LINEAR.value,
                 memory_complexity=FunctionComplexity.LINEAR.value,
                 cpu_cores=1,
                 cacheable_result=True,
                 cpu_activation=AttributeNames.PYTHON.value,
                 gpu_activation=None):
        self.algorithm_name = algorithm_name
        if implementation_file:
            self.implementation_file = implementation_file
        else:
            self.implementation_file = f"{algorithm_name}_worker.py"
        self.function_name = function_name if function_name else algorithm_name
        self.documentation=documentation
        self.time_complexity = time_complexity
        self.memory_complexity = memory_complexity
        self.cpu_cores = cpu_cores
        self.cacheable_result = cacheable_result
        self.cpu_activation = cpu_activation
        self.gpu_activation = gpu_activation
        self.inputs = inputs
        self.outputs = outputs

    def to_dict(self):
        res = {
            AttributeNames.ALGORITHM_NAME.value: self.algorithm_name,
            AttributeNames.ALGORITHM_DOC.value: self.documentation,
            AttributeNames.IMPLEMENTATION_FILE.value: self.implementation_file,
            AttributeNames.FUNCTION.value: self.function_name,
            AttributeNames.TIME_COMPLEXITY.value: self.time_complexity,
            AttributeNames.MEMORY_COMPLEXITY.value: self.memory_complexity,
            AttributeNames.CPU_CORES.value: self.cpu_cores,
            AttributeNames.CACHEABLE_RESULT.value: self.cacheable_result,
            AttributeNames.CPU_ACTIVATION.value: self.cpu_activation,
            AttributeNames.GPU_ACTIVATION.value: self.gpu_activation,
            AttributeNames.ALGORITHM_INPUTS.value: self.__extract_inputs(),
            AttributeNames.ALGORITHM_OUTPUTS.value: self.__extract_outputs()
        }
        return res

    def __extract_inputs(self):
        return [{AttributeNames.NAME.value: input.name, AttributeNames.TYPE.value: input.param_type} for input in self.inputs]

    def __extract_outputs(self):
        return [{AttributeNames.NAME.value: f"output_{i}", AttributeNames.TYPE.value: output} for i, output in enumerate(self.outputs)]
