from ast import literal_eval

from arm64_tester.parameters import ArrayParameter as Array
from arm64_tester.parameters import NumericParameter as Numeric
from arm64_tester.parameters import StringParameter as String
from arm64_tester.subroutines.subroutine import Subroutine
from arm64_tester.util.type_casting import cast_to_output


class ArraySubroutine(Subroutine):
    """Subroutine that returns one or more arrays"""

    def __init__(self, name, parameters, outputs):
        super().__init__(name, parameters)
        self.outputs = outputs

    def get_nr_outputs(self):
        return len(self.outputs)

    def build_test_call(self):
        return '{} {} {} printf("\\n");'.format(\
            # Declare output variables beforehand, so we have access to them after subroutine call
            ''.join([parameter.get_test_declaration_representation() for parameter in self.parameters]),\
            # Actually make subroutine call
            '{}({});'.format(self.name, ','.join([parameter.get_test_call_representation() for parameter in self.parameters])),\
            # Access previously declared variables to print their final values
            'printf("\\n");'.join(filter(lambda x: x != '', [parameter.get_test_call_output_representation() for parameter in self.parameters])))

    def process_parameters(self, parameters):
        for idx, parameter in enumerate(parameters):
            if parameter == 'string':
                self.parameters.append(String(idx, True if idx >= (
                    len(parameters) - len(self.outputs)) else False))
            elif 'array' in parameter:
                self.parameters.append(Array(idx, parameter.replace('array', '').strip(
                ), True if idx >= (len(parameters) - len(self.outputs)) else False))
            else:  # numeric
                self.parameters.append(Numeric(idx, parameter))

    def compare_outputs(self, expected, real, precision):
        if(len(expected) != len(real)):
            return False
        for out_type, exp, re in zip(self.outputs, expected, real):
            if out_type == 'string':
                return exp == re
            else:  # Array
                arr_type = out_type.replace('array', '').strip()
                re.replace('-nan', 'None').replace('+nan',
                                                   'None').replace('nan', 'None')
                re_arr = literal_eval(re)
                if(len(exp) != len(re_arr)):
                    return False
                for exp_el, re_el in zip(exp, re_arr):
                    if (arr_type == 'int' or arr_type == 'long') and exp_el != re_el:
                        return False
                    elif abs(exp_el-re_el) > precision:
                        return False

        return True

    def convert_outputs(self, real):
        outputs = []

        for type, output in zip(self.outputs, real):
            if type == 'string':
                outputs.append(output)
            else:
                array_output = []

                arr_type = type.replace('array', '').strip()

                re_arr.replace('-nan', 'None').replace('+nan',
                                                       'None').replace('nan', 'None')
                re_arr = literal_eval(output)

                for array_element in zip(re_arr):
                    if arr_type == 'int' or arr_type == 'long':
                        array_output.append(
                            cast_to_output('integer', array_element))
                    else:
                        array_output.append(
                            cast_to_output('float', array_element))

        return outputs
