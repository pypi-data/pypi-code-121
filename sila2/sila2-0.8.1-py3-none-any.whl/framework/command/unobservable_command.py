from typing import Generic, TypeVar

from sila2.framework.command.command import Command

ParametersNamedTuple = TypeVar("ParametersNamedTuple")
ResponsesNamedTuple = TypeVar("ResponsesNamedTuple")


class UnobservableCommand(Command, Generic[ParametersNamedTuple, ResponsesNamedTuple]):
    """Represents an observable command"""

    pass
