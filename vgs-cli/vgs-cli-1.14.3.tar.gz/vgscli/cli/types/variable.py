from typing import Any

import click


class Variable:
    """
    A parsed "name=value" pair.
    """

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value


class VariableParamType(click.ParamType):
    name = 'name=value'

    def convert(self, value: str, param, ctx) -> Variable:
        tokens = value.split('=', 2)
        return Variable(tokens[0], tokens[1])