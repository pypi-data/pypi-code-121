import abc
import typing as t
from suanpan.components import Arguments
from suanpan.stream.objects import Context
from suanpan.interfaces import HasArguments

if t.TYPE_CHECKING:
    from suanpan.stypes import ArgumentT


class MessageHandler(HasArguments):
    def __init__(self):
        self._inputs = []
        self._outputs = []
        self._params = []
        self._context = Context()

    def init_params(self):
        args_dict = self.getArgsDict()
        _params = self.loadFormatArguments(self.params, args_dict)
        _args = Arguments.froms(*_params)
        self._context = Context.froms(args=_args)

    @property
    def context(self):
        return self._context

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def params(self):
        return self._params

    def add_input(self, argument: 'ArgumentT'):
        self._inputs.append(argument)

    def add_output(self, argument: 'ArgumentT'):
        self._outputs.append(argument)

    def add_param(self, argument: 'ArgumentT'):
        self._params.append(argument)

    def beforeInit(self):
        ...

    def afterInit(self, context):
        ...

    def beforeCall(self, context):
        ...

    def afterCall(self, context):
        ...

    def initialize(self):
        """initialize before message loop"""
        ...

    @abc.abstractmethod
    def run(self, context):
        """run message loop"""
        ...

    def getArguments(self, *args, **kwargs):
        ...
