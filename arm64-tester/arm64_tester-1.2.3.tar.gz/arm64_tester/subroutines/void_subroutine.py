from ast import literal_eval

from arm64_tester.parameters import ArrayParameter as Array
from arm64_tester.parameters import NumericParameter as Numeric
from arm64_tester.parameters import StringParameter as String
from arm64_tester.subroutines.subroutine import Subroutine


class VoidSubroutine(Subroutine):
    """Subroutine that does not return anything, directly or indirectly (i.e., all output is printed directly in assembly)"""

    def __init__(self, name, parameters):
        super().__init__(name, parameters)

    def get_nr_outputs(self):
        return 0

    def build_test_call(self):
        return '{}({}); printf("\\n");'.format(self.name, ','.join([parameter.get_test_call_representation() for parameter in self.parameters]))

    def process_parameters(self, parameters):
        for idx, parameter in enumerate(parameters):
            if parameter == 'string':
                self.parameters.append(String(idx, False))
            elif 'array' in parameter:
                self.parameters.append(
                    Array(idx, parameter.replace('array', '').strip(), False))
            else:  # numeric
                self.parameters.append(Numeric(idx, parameter))

    def compare_outputs(self, expected, real, _):
        truth_values = [exp == re for exp, re in zip(expected, real)]
        return all(truth_values)
