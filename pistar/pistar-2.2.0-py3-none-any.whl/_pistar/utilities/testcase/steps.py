"""
description: this module provides the function for teststeps, including the decorator
             and timeout function.
"""
import attr
import functools
import inspect
import threading
from typing import List, Dict, TYPE_CHECKING, Optional, Callable
from _pistar.terminal import TerminalWriter
from _pistar.config.cmdline import hookimpl
from _pistar.node import Node
from _pistar.utilities.condition.condition import ConditionDef
from _pistar.utilities.condition.condition import ConditionLookUpError
from _pistar.utilities.condition.condition import ConditionManager
from _pistar.utilities.constants import TESTCASE_EXECUTION_STATUS
from _pistar.utilities.exceptions import DuplicatedTestStepNameException
from _pistar.utilities.exceptions import UnsupportedStartTypeException
from _pistar.utilities.parameters.parameters import ParametersLookUpError
from _pistar.utilities.testcase.repr import LocationRepr
from _pistar.utilities.testcase.repr import BaseRepr
from _pistar.utilities.testcase.thread_status import Status
from _pistar.utilities.testcase.exception import dedent
from _pistar.utilities.testcase.exception import ExcInfoFormatter

if TYPE_CHECKING:
    from _pistar.utilities.testcase.case import TestCase


def has_teststep(cls):
    """
    description: this function is used to
                 check whether a testcase has teststep.
    arguments:
        Class:
            type: type
    return:
        type: bool
    """

    for member in cls.__dict__.values():
        if hasattr(member, "start") and hasattr(member, "end"):
            return True
    return False


def is_teststep(function):
    """
    description: this function is used to check whether a function is teststep.
    arguments:
        function:
            type: any
            assertion: callable
    return:
        type: bool
        description: if the function is a teststep, return True,
                     else return False.
    """
    return (
            hasattr(function, "start") and hasattr(function, "end") and callable(function)
    )


def teststep(test_function=None, *, start=None, skip: bool = None, mark: str = None, timeout: int = None,
             description: str = None):
    """
    description: decorate of teststep, parse actual teststep arguments
                 and run the step
    arguments:
        start:
            description: indicate teststep when to run
            type: str
            default: None
        skip:
            description: set the teststep not to run
            type: bool
        mark:
            description: set mark to teststep, specific mark step
        description:
            description: set the teststep description info
    return:
        type: TestStep
        description: actual step function results
    """
    teststep_obj = TestStep(start=start, skip=skip, mark=mark, timeout=timeout, description=description)
    if test_function:
        return teststep_obj(test_function)

    return teststep_obj


class TestStep:
    """
    description: teststep decorate class, generate schedule strategy based on
                 testcase class
    attribute:
        start:
            description: indicate teststep when to run
            type: str
            default: None
        skip:
            description: set the teststep not to run
            type: bool
        mark:
            description: set mark to teststep,  specific mark step
    """

    start = None
    skip = None
    mark = None
    description = None

    __status_dictionary = {
        key: value
        for key, value in TESTCASE_EXECUTION_STATUS.__dict__.items()
        if not key.startswith("__")
    }
    __teststep_list = None

    def __get_previous_teststep(self):
        caller_frame = inspect.currentframe()
        while True:
            if not caller_frame.f_code.co_filename == __file__:
                break
            caller_frame = caller_frame.f_back

        member_name_list = list(caller_frame.f_locals.keys())
        for member_name in member_name_list[::-1]:
            last_member = caller_frame.f_locals[member_name]

            if is_teststep(last_member):
                self.__teststep_list.append(last_member)

        if self.__teststep_list:
            return self.__teststep_list[0]
        return None

    def __init__(self, start=None, skip=None, mark=None, timeout=None, description=None):
        self.skip = skip
        self.mark = mark
        self.timeout = timeout
        self.description = description
        self.__teststep_list = list()

        if skip and not isinstance(skip, bool):
            raise TypeError("the decorator teststep parameter skip type exception")
        if timeout and not isinstance(timeout, (int, float)):
            raise TypeError("the decorator teststep parameter timeout type exception")
        if mark and not isinstance(mark, str):
            raise TypeError("the decorator teststep parameter mark type exception")
        if description and not isinstance(description, str):
            raise TypeError("the decorator teststep parameter description type exception")
        previous_teststep = self.__get_previous_teststep()
        if start is None:
            if previous_teststep:
                self.start = previous_teststep.end
            else:
                self.start = Status(True)
        elif not isinstance(start, Status):
            raise UnsupportedStartTypeException(start)
        else:
            self.start = start

    def __execute(self, function, testcase, **kwargs):
        function(testcase, **kwargs)

    def __call__(self, function, **kwargs):
        if function.__name__ in [item.__name__ for item in self.__teststep_list]:
            raise DuplicatedTestStepNameException(function.__name__)
        function = Timeout(self.timeout)(function)

        @functools.wraps(function, **kwargs)
        def wrapper(*args, **kwargs):
            testcase = args[0]
            function.__globals__.update(**self.__status_dictionary)
            if self.skip:
                pass
            elif not self.mark:
                self.__execute(function, testcase, **kwargs)
            elif not wrapper.marks:
                self.__execute(function, testcase, **kwargs)
            elif self.mark not in wrapper.marks:
                pass
            else:
                self.__execute(function, testcase, **kwargs)
            wrapper.end.value = True

        wrapper.start = self.start
        wrapper.description = self.description
        wrapper.end = Status(False)
        wrapper.marks = list()
        return wrapper


class TimeoutLookUpError(LookupError):
    """teststep run timeout error."""

    def __init__(self, step: Callable, msg: str = None):
        super().__init__(msg)
        self.msg = msg
        self.call = step

    def format_repr(self) -> "TimeoutLookUpRepr":
        trace_line: List[str] = list()
        real_call = inspect.unwrap(self.call)
        fspath = inspect.getfile(real_call)
        sources, lineno = inspect.findsource(real_call)
        inspect.getsource(real_call)
        lines = dedent([line.rstrip() for line in sources])

        for line in lines[lineno:]:
            trace_line.append(f"{line.rstrip()}")
            if line.lstrip().startswith("def"):
                break

        location = LocationRepr(path=fspath, lineno=lineno + 1, exception="")
        return TimeoutLookUpRepr(location, msg=self.msg, lines=trace_line)


@attr.s(eq=False, auto_attribs=True)
class TimeoutLookUpRepr(BaseRepr):
    location: "LocationRepr"
    msg: str
    lines: List[str]

    def gen_repr(self, writer: TerminalWriter):
        self.location.gen_repr(writer)
        for line in self.lines:
            writer.line(line.rstrip())

        writer.line(f"{ExcInfoFormatter.error_marker}      {self.msg.strip()}")


class TimeoutException(Exception):
    """
    description: if a function is timeout, raise this exception.
    """

    def __init__(self, function_name, timeout):
        super().__init__(
            f"TimeoutException: teststep '{function_name}' execution time exceeds "
            f"the set timeout time {timeout} seconds"
        )


class Timeout:
    """
    description: this class is used to wrap a function with timeout limit.
    """

    timeout = None

    def __init__(self, timeout=None):
        self.timeout = timeout

    def __call__(self, function):
        if self.timeout is None:
            return function

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            results = [
                TimeoutException(function_name=function.__name__, timeout=self.timeout)
            ]

            def thread_function():
                try:
                    results[0] = function(*args, **kwargs)
                except BaseException as exception:
                    results[0] = exception

            thread = threading.Thread(target=thread_function)
            thread.daemon = True

            thread.start()
            thread.join(self.timeout)
            if isinstance(results[0], Exception):
                raise TimeoutLookUpError(function, str(results[0]))

            return results[0]

        return wrapper


class Step(Node):
    """
    The class is used to bind variables and conditions.
    It is responsible for executing conditions and test_step.
    param name:
        The step name is the test step function name.
    param parent:
        The parent Node. This is the class of this test step.
    param obj:
        The origin test step object.
    param args:
        The args of the test step. it contains the parameters and condition_name.
    """

    def __init__(self, name: str, parent: "TestCase", obj: TestStep):
        super().__init__(
            name=name,
            parent=parent,
            fspath=parent.fspath,
            config=parent.config,
            session=parent.session,
        )
        self.hook = self.config.hook
        self.stepobj: TestStep = obj
        self.args: List = list(inspect.signature(obj).parameters)
        self.condition_manager: ConditionManager = parent.condition_manager
        self.condition_defs: List[ConditionDef] = []
        self.condition_return_value: Dict[str, object] = {}
        self.condition_result_cache: Dict[str, object] = {}
        self.condition_exception: Optional[BaseException] = None
        self.parameters_exception: Optional[BaseException] = None

    @classmethod
    def from_case_and_teststep(cls, case: "TestCase", step: TestStep):
        return super().from_parent(parent=case, name=step.__name__, obj=step)

    @staticmethod
    def judge_parameters(args: list, step: Callable):
        """
        Judging two abnormal scenarios in parameters:
        1. arg_names does not match the formal parameters in the teststep
        2. s set of arg_values does not match the number of arg_names
        """
        param_arg_names = getattr(step, "param_arg_names", "")
        if isinstance(param_arg_names, str):
            param_arg_names = {param_arg_names}
        lost_param = set(args) - set(param_arg_names) or set(param_arg_names) - set(
            args
        )
        if lost_param:
            raise ParametersLookUpError(name=",".join(lost_param), step=step)

        parameters_list = getattr(step, "parameters", [])
        for parameter in parameters_list:
            lost_param = set(args) - (set(args) & parameter.keys())
            if lost_param:
                par_values = map(str, parameter.values())
                raise ParametersLookUpError(
                    name=",".join(lost_param), step=step, value=" ".join(par_values)
                )

    def get_con_defs(self):
        """
        this method distinguishes parameters and conditions based on indirect parameters
        if condition get all the condition_defs in the args of the test step
        if it is parameters, judge the legality of parameters
        """

        indirect = getattr(self.stepobj, "indirect", None)
        if indirect is False:
            try:
                self.judge_parameters(self.args, self.stepobj)
            except ParametersLookUpError as e:
                self.parameters_exception = e
            else:
                self.condition_defs = []
                return
        else:
            for arg in self.args:
                try:
                    con_def = self.condition_manager.get_con_def(
                        arg, self.parent.nodeid, self.stepobj
                    )
                except ConditionLookUpError as e:
                    self.condition_exception = e
                    break
                else:
                    self.condition_defs.append(con_def)

    def setup(self):
        """
        the function is used to execute the conditions and store the return value and
        the execution result of the condition_defs.
        """
        self.get_con_defs()
        if not self.condition_defs:
            return
        for con_def in self.condition_defs:
            result = self.hook.pistar_condition_setup(condition_def=con_def)
            self.condition_result_cache[con_def.name] = result
            if result[1]:
                self.condition_exception = result[1]
            else:
                self.condition_return_value[con_def.name] = result[0]

    def execute(self):
        self.hook.pistar_step_call(step=self)


@hookimpl
def pistar_step_call(step: Step):
    if step.parameters_exception:
        raise step.parameters_exception
    elif step.condition_exception:
        raise step.condition_exception
    else:
        step.stepobj(**step.condition_return_value)
