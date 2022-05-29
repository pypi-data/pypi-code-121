# imports ---------------------------------
from typing import Any, Callable
import time
import asyncio
# -----------------------------------------

class ResultState: # class for result state

    """
    It's class for result state

    result: bool variable which shows is the case passed or not
    text: string variable with text representation of result

    __init__: method for creating ResultState object with result and text as arguments
    __str__: method for giving text representation of result
    """

    result: bool = None
    text: str = ""

    def __init__(self, result: bool, text: str):
        self.result = result
        self.text = text

    def __str__(self) -> str:
        return self.text

class ResultStates: # class with result states

    """
    It's class with basic result states

    passed: ResultState object which means that test passed
    failed: ResultState object which means that test failed by answer
    error: ResultSatet object which means that test failed by some error
    time: ResultSatet object which means that test was runned to check time
    """

    passed: ResultState = ResultState(True, "PASSED")
    failed: ResultState = ResultState(False, "FAILED")
    error: ResultState = ResultState(False, "ERROR")
    time: ResultState = ResultState(True, "TIME")

class Unit: # class with unit

    """
    It's class with unit

    callback: variable with Callable value with unit callback
    name: string variable with callback name
    asynchronous: bool variable which means is the callback asynchronous

    __init__: method for creating Unit object with callback and asynchronous as arguments
    __str__: method for giving name of callback
    """

    callback: Callable[..., Any] = None
    name: str = ""
    asynchronous: bool = False

    def __init__(self, callback: Callable[...,  Any], asynchronous: bool = False) -> None:
        self.callback = callback
        self.name = callback.__name__
        self.asynchronous = asynchronous

    def __str__(self):
        return self.name

class TestCase: # class with test case

    """
    It's class with test case

    arguments: dictionary with arguments for test case
    answer: correct answer for test case

    __init__: method for creating TestCase object with arguments and answer as arguments
    __str__: method for giving text representation of TestCase object
    """

    arguments: dict = {}
    answer: Any = None

    def __init__(self, arguments: dict, answer: Any) -> None:
        self.arguments = arguments
        self.answer = answer

    def __str__(self) -> str:
        return f"Agruments: {self.arguments}\nCorrect answer: {self.answer}"

class TestGroup: # class with test group

    """
    It's class with test group

    unit: Unit object which will be tested
    cases: list of TestCase objects which will be used for testing unit
    only_errors: bool variable which means will be only testing on errors(without comparing with answer) or general one
    only_time: bool variable which means will be only testing on time(without comparing with answer) or general one
    no_print: bool variable which means will be printing or not

    __init__: method for creating TestGroup object with unit, cases, only_errors and no_print as arguments
    """

    unit: Unit = None
    cases: list[TestCase] = []
    only_errors: bool = False
    only_time: bool = False
    no_print: bool = False

    def __init__(self, unit: Unit,
                 cases: list[TestCase],
                 only_errors: bool = False,
                 only_time: bool = False,
                 no_print: bool = False) -> None:
        self.unit = unit
        self.cases = cases
        self.only_errors = only_errors
        self.only_time = only_time
        self.no_print = no_print

class TestCaseResult(TestCase): # class with test case result

    """
    It's class with test case result bases on TestCase class

    unit: Unit object which was be tested
    returned: variable with value with unit returned
    work_time: time of unit working
    result: ResultState object with testing result

    __init__: method for creating TestCaseResult object with unti, case, returned, result and work_time as arguments
    __str__: method with text representation of TestCaseResult object
    """

    unit: Unit = None
    returned: Any = None
    work_time: str = ""
    result: ResultState = None

    def __init__(self, unit: Unit, 
                 case: TestCase, 
                 returned: Any,
                 result: ResultState,
                 work_time: str) -> None:
        self.unit = unit
        self.arguments = case.arguments
        self.answer = case.answer
        self.returned = returned
        self.result = result
        self.work_time = work_time

    def __str__(self) -> str:
        return f"Unit: {self.unit}\nAgruments: {self.arguments}\nCorrect answer: {self.answer}\nReturned answer: {self.returned}\nResult: {self.result.text}\nTime: {self.work_time}"

class Test: # main class for testing

    """
    It's main class which could be used for testing

    groups: list with TestGroup objects

    __output_line: method for outputing mark line
    __output_unit: method for outputing unit
    __output_case: method for outputing case

    test: method for testing test group with TestGroup object and output as arguments
    test_async: async version of test method
    mark_test_unit: method, which should be used as decorator, for marking test unit with TestCase object, asynchronous, only_errors, only_time and no_print as arguments and it returns register function
    register: function for registration test group with callback as argument and it returns callback(for working this callback in future)
    add_test_unit: method, same as mark_test_unit, but can't be used as decorator
    test_all: method for running testing all groups with file_name as optional argument and it returns dictionary with TestCaseResult objects connected to their units
    test_all_async: async version of test_all method
    """
    
    groups: list[TestGroup] = []

    def __output_line(self, char: str, output: Callable[..., Any] = print) -> None:
        output(char * 100 + ("\n" if output != print else ""))

    def __output_unit(self, unit: Unit, output: Callable[..., Any] = print) -> None:
        output(f"UNIT: {unit.name}" + ("\n" if output != print else ""))

    def __output_case(self, ind: int, case: TestCaseResult, only_errors: bool = False, only_time: bool = False, output: Callable[..., Any] = print) -> None:
        if only_errors or only_time:
            output(f"CASE {ind}: {case.result.text}" + ("\n" if output != print else ""))
        else:
            output(f"CASE {ind}:" + ("\n" if output != print else ""))
            output(f"    Agruments: {case.arguments}" + ("\n" if output != print else ""))
            output(f"    Correct answer: {case.answer}" + ("\n" if output != print else ""))
            output(f"    Returned answer: {case.returned}" + ("\n" if output != print else ""))
            output(f"    Result: {case.result.text}" + ("\n" if output != print else ""))
            output(f"    Time: {case.work_time if case.work_time >= 1 else case.work_time * 1000} {'s' if case.work_time >= 1 else 'ms'}" + ("\n" if output != print else ""))

    def test(self, group: TestGroup, output: Callable[..., Any]) -> list[TestCaseResult]:
        results: list[TestCaseResult] = []
        if not group.no_print:
            self.__output_line("*", output)
            self.__output_unit(group.unit, output)
        ind = 0
        if group.only_errors and group.only_time:
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                start_time = time.time()
                try:
                    if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                    else:
                        loop = asyncio.new_event_loop()
                        returned = loop.run_until_complete(group.unit.callback(**case.arguments))
                        loop.close()
                    work_time = time.time() - start_time
                    result = TestCaseResult(group.unit, case, None, ResultState(True, f"PASSED, TIME ( {work_time if work_time >= 1 else work_time * 1000} {'s' if work_time >= 1 else 'ms'} )"), work_time)
                    results.append(result)
                except Exception as err:
                    work_time = time.time() - start_time
                    result = TestCaseResult(group.unit, case, None, ResultState(False, f"ERROR ( {err} ), TIME ( {work_time if work_time >= 1 else work_time * 1000} {'s' if work_time >= 1 else 'ms'} )"), work_time)
                    results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        elif group.only_errors:
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                try:
                    if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                    else:
                        loop = asyncio.new_event_loop()
                        returned = loop.run_until_complete(group.unit.callback(**case.arguments))
                        loop.close()
                    result = TestCaseResult(group.unit, case, None, ResultStates.passed, None)
                    results.append(result)
                except Exception as err:
                    result = TestCaseResult(group.unit, case, None, ResultState(False, f"ERROR ( {err} )"), None)
                    results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        elif group.only_time:
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                start_time = time.time()
                if not group.unit.asynchronous:
                    returned = group.unit.callback(**case.arguments)
                else:
                    loop = asyncio.new_event_loop()
                    returned = loop.run_until_complete(group.unit.callback(**case.arguments))
                    loop.close()
                work_time = time.time() - start_time
                result = TestCaseResult(group.unit, case, None, ResultState(True, f"TIME ( {work_time if work_time >= 1 else work_time * 1000} {'s' if work_time >= 1 else 'ms'} )"), work_time)
                results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        else:    
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                start_time = time.time()
                returned: Any = None
                error: Exception = None
                try:
                    if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                    else:
                        loop = asyncio.new_event_loop()
                        returned = loop.run_until_complete(group.unit.callback(**case.arguments))
                        loop.close()
                except Exception as err:
                    error = err
                work_time = time.time() - start_time
                if error != None:
                    result = TestCaseResult(group.unit, case, returned, ResultState(False, f"ERROR ( {error} )"), work_time)
                    results.append(result)
                elif returned == case.answer:
                    result = TestCaseResult(group.unit, case, returned, ResultStates.passed, work_time)
                    results.append(result)
                else:
                    result = TestCaseResult(group.unit, case, returned, ResultStates.failed, work_time)
                    results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        if not group.no_print:
            self.__output_line("-", output)
        return results

    async def test_async(self, group: TestGroup, output: Callable[..., Any]) -> list[TestCaseResult]:
        results: list[TestCaseResult] = []
        if not group.no_print:
            self.__output_line("*", output)
            self.__output_unit(group.unit, output)
        ind = 0
        if group.only_errors and group.only_time:
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                start_time = time.time()
                try:
                    if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                    else:
                        returned = await group.unit.callback(**case.arguments)
                    work_time = time.time() - start_time
                    result = TestCaseResult(group.unit, case, None, ResultState(True, f"PASSED, TIME ( {work_time if work_time >= 1 else work_time * 1000} {'s' if work_time >= 1 else 'ms'} )"), work_time)
                    results.append(result)
                except Exception as err:
                    work_time = time.time() - start_time
                    result = TestCaseResult(group.unit, case, None, ResultState(False, f"ERROR ( {err} ), TIME ( {work_time if work_time >= 1 else work_time * 1000} {'s' if work_time >= 1 else 'ms'} )"), work_time)
                    results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        elif group.only_errors:
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                try:
                    if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                    else:
                        returned = await group.unit.callback(**case.arguments)
                    result = TestCaseResult(group.unit, case, None, ResultStates.passed, None)
                    results.append(result)
                except Exception as err:
                    result = TestCaseResult(group.unit, case, None, ResultState(False, f"ERROR ( {err} )"), None)
                    results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        elif group.only_time:
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                start_time = time.time()
                if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                else:
                    returned = await group.unit.callback(**case.arguments)
                work_time = time.time() - start_time
                result = TestCaseResult(group.unit, case, None, ResultState(True, f"TIME ( {work_time if work_time >= 1 else work_time * 1000} {'s' if work_time >= 1 else 'ms'} )"), work_time)
                results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        else:    
            for case in group.cases:
                if not group.no_print:
                    self.__output_line("-", output)
                start_time = time.time()
                returned: Any = None
                error: Exception = None
                try:
                    if not group.unit.asynchronous:
                        returned = group.unit.callback(**case.arguments)
                    else:
                        returned = await group.unit.callback(**case.arguments)
                except Exception as err:
                    error = err
                work_time = time.time() - start_time
                if error != None:
                    result = TestCaseResult(group.unit, case, returned, ResultState(False, f"ERROR ( {error} )"), work_time)
                    results.append(result)
                elif returned == case.answer:
                    result = TestCaseResult(group.unit, case, returned, ResultStates.passed, work_time)
                    results.append(result)
                else:
                    result = TestCaseResult(group.unit, case, returned, ResultStates.failed, work_time)
                    results.append(result)
                if not group.no_print:
                    self.__output_case(ind, result, group.only_errors, group.only_time, output)
                ind += 1
        if not group.no_print:
            self.__output_line("-", output)
        return results

    def mark_test_unit(self, cases: list[TestCase], asynchronous: bool = False, only_errors: bool = False, only_time: bool = False, no_print: bool = False) -> Callable[..., Any]:
        def register(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.groups.append(TestGroup(Unit(callback, asynchronous), cases, only_errors, only_time, no_print))
            return callback
        return register

    def add_test_unit(self, callback: Callable[..., Any], cases: list[TestCase], asynchronous: bool = False, only_errors: bool = False, only_time: bool = False, no_print: bool = False) -> None:
        self.groups.append(TestGroup(Unit(callback, asynchronous), cases, only_errors, only_time, no_print))

    def test_all(self, file_name: str = "") -> dict:
        results: dict = {}
        output: Callable[..., Any] = print
        all_passed: bool = True
        if file_name != "":
            file = open(file_name, 'w')
            output = file.write
        for group in self.groups:
            result: list[TestCaseResult] = self.test(group, output)
            for res in result:
                all_passed &= res.result.result
            results[result[0].unit.name] = result
        self.__output_line("*", output)
        if all_passed:
            output("ALL CASES PASSED :)" + ("\n" if output != print else ""))
        else:
            output("NOT ALL TESTS PASSED :(" + ("\n" if output != print else ""))
        self.__output_line("*", output)
        if file_name != "":
            file.close()
        return results

    async def test_all_async(self, file_name: str = "") -> dict:
        results: dict = {}
        output: Callable[..., Any] = print
        all_passed: bool = True
        if file_name != "":
            file = open(file_name, 'w')
            output = file.write
        for group in self.groups:
            result: list[TestCaseResult] = await self.test_async(group, output)
            for res in result:
                all_passed &= res.result.result
            results[result[0].unit.name] = result
        self.__output_line("*", output)
        if all_passed:
            output("ALL CASES PASSED :)" + ("\n" if output != print else ""))
        else:
            output("NOT ALL TESTS PASSED :(" + ("\n" if output != print else ""))
        self.__output_line("*", output)
        if file_name != "":
            file.close()
        return results

"""
Examples of using is in examples.py file
"""