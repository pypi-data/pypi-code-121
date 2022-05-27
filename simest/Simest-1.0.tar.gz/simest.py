import typing as t
import logging
from time import time

__version__ = "1.0"


class Value:
    def __init__(self, value: t.Any, passed: bool, expected: t.Any, func: t.Any, **kwargs: t.Any) -> None:
        self.value: t.Any = value
        self.passed: bool = passed
        self.expected: t.Any = expected
        self.func: t.Any = func
        self.kwargs: t.Any = kwargs

        pass

class Tester:
    def __init__(self, title: t.Optional[str] = "Test") -> None:
        self.title: str = title
        self.values: t.List[Value] = list()

        #logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.debug)
        pass

    def __outputCheck__(self, val: Value) -> None:
        if (val.passed): print(f"✔ Function '{val.func.__name__}' returned expected value")
        else: print(f"❌ Function '{val.func.__name__}' did not return expected value.\n\tReturned Value: {val.value}\n\tExpected Value: {val.expected}\n\tArguments Passed: {val.kwargs.items()}")

    def __outputCheckTime__(self, val: Value) -> None:
        if (val.passed): print(f"✔ Function '{val.func.__name__}' completed in {val.value} seconds")
        else: print(f"❌ Function '{val.func.__name__}' did not complete in {val.expected[0]}-{val.expected[1]} seconds.\n\tTime Taken: {val.value}\n\tMin Time Taken: {val.expected[0]}\n\tMax Time Taken: {val.expected[1]}\n\tArguments Passed: {val.kwargs.items()}")

    def equalCheck(self, expect: t.Any, func: t.Any, **kwargs: t.Any) -> bool:
        val: bool = func(**kwargs)
        self.values.append(Value(val, val == expect, expect, func=func, kwargs=kwargs))
        self.__outputCheck__(self.values[-1])

        return self.values[-1].passed
    
    def ruleCheck(self, rule: str, expect: t.Any, func: t.Any, **kwargs: t.Any) -> bool:
        """
        **Unsafe with user-provided string due to usage of `eval`**
        ## Syntax:

         - `&r` - return value
         - `&e` - expected value
        """

        val: bool = func(**kwargs)
        result: str = rule.replace("&r", str(val)).replace("&e", str(expect))

        self.values.append(Value(val, eval(result), expect, func=func, kwargs=kwargs))
        self.__outputCheck__(self.values[-1])

        return self.values[-1].passed

    def timeCheck(self, func: t.Any, max: t.Union[int, float], min: t.Optional[t.Union[int, float]] = 0, **kwargs) -> bool:
        start: float = time()
        func(**kwargs)

        end: float = time()
        taken: float = end - start

        self.values.append(Value(taken, ((taken >= min) & (taken <= max)), (min, max), func=func, kwargs=kwargs))
        self.__outputCheckTime__(self.values[-1])

        return self.values[-1].passed

