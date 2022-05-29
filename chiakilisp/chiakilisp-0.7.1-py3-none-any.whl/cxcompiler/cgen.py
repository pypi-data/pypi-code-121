# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring


class CPPCodeGenerator:

    """Helps to complete CPP code generation"""

    _source: list

    def __init__(self, source: list) -> None:

        """Initializes a CPPCodeGenerator instance"""

        self._source = source

    def source(self) -> list:

        """Returns holding source instance"""

        return self._source

    def generate(self) -> str:

        """Actually returns a complete CPP code string"""

        return '\n'.join([
            '#include <string>',  # <----- include string
            '#include <chiakilisp.hpp>',  # <---- runtime
            'int main()',  # <---- wrap program in main()
            '{',  # <---  block starting character in CPP
            *self._source,  # <-- include  generated code
            'return 0;',  # <-- always return 0 to system
            '}'  # <---- block finishing character in CPP
        ])
