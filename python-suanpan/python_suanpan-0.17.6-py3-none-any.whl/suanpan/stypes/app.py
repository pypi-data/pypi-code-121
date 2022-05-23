import abc
import typing as t
from suanpan.objects import HasName

if t.TYPE_CHECKING:
    from suanpan.stypes.trigger import TriggerT
    from suanpan.stypes.argument import ArgumentT


class AppT(HasName):
    args: t.Annotated[t.Any, 'arguments of app']

    @property
    @abc.abstractmethod
    def trigger(self) -> 'TriggerT':
        """Get a trigger instance that can run task at periodic intervals."""
        ...

    @abc.abstractmethod
    def use(self, handlerClass):
        """Decorate a class to run.

        Arguments:
            handlerClass: The handler class to add.

        Example:
            >>> @app.use
            >>> class CustomCode(MessageHandler):
            ...     def run(self, context):
            ...     print('run ...')
        """
        ...

    @abc.abstractmethod
    def input(self, argument: ArgumentT):
        """Decorate a function to add an input argument.

        Arguments:
            argument: The input argument to add.

        Example:
            >>> @app.input(String(key="formula", default=""))
            >>> def SPFormula(context):
            ...     args = context.args
        """
        ...

    @abc.abstractmethod
    def output(self, argument):
        """Decorate a function to add an output argument.

        Arguments:
            argument: The output argument to add.

        Example:
            >>> @app.output(String(key="outputTable", required=True))
            >>> def SPHiveSql(context):
            ...     args = context.args
        """
        ...

    @abc.abstractmethod
    def param(self, argument):
        """Decorate a function to add an param argument.

        Arguments:
            argument: The param argument to add.

        Example:
            >>> @app.param(String(key="sql", required=True))
            >>> def SPHiveSql(context):
            ...     args = context.args
        """
        ...

    @abc.abstractmethod
    def column(self, argument):
        """alias name of :meth:`param`"""
        ...

    @abc.abstractmethod
    def beforeInit(self, hook):
        """run the `hook` function before call init function"""
        ...

    @abc.abstractmethod
    def afterInit(self, hook):
        """run the `hook` function after call init function"""
        ...

    @abc.abstractmethod
    def beforeCall(self, hook):
        """run the `hook` function before call stream process function"""
        ...

    @abc.abstractmethod
    def afterCall(self, hook):
        """run the `hook` function after call stream process function"""
        ...

    @abc.abstractmethod
    def beforeExit(self, hook):
        """run the `hook` function before stream process function"""
        ...

    @abc.abstractmethod
    def load(self, args, argsDict=None):
        """load `args` and `argsDict` into a new Arguments

        Returns:
            Arguments: The return value. True for success, False otherwise.
        """
        ...

    @abc.abstractmethod
    def send(self, results, queue=None, message=None, args=None):
        """send `message` to message queue"""
        ...

    @property
    @abc.abstractmethod
    def vars(self):
        """the variables of app"""
        ...

    @property
    @abc.abstractmethod
    def modules(self):
        """the modules of app"""
        ...
