from arm64_tester.parameters.parameter import Parameter


class NumericParameter(Parameter):
    """Numeric subroutine parameter"""

    def __init__(self, idx, num_type):
        super().__init__(idx)
        self.num_type = num_type

    def get_prototype_representation(self):
        return '{} arg{}'.format(self.num_type, self.idx)

    def get_test_declaration_representation(self):
        # Not applicable to numeric parameters (they're always only input)
        return ''

    def get_test_call_representation(self):
        return '{}'

    def get_literal_representantion(self, value):
        return str(value)

    def get_test_call_output_representation(self):
        # Not applicable to numeric parameters (when they are output they can be incorporated with the subroutine call)
        return ''
