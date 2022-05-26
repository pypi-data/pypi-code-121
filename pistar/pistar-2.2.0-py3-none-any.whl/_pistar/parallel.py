import inspect
import multiprocessing
from typing import Union, Sequence, Set, List

import dill
from _pistar.config.cmdline import hookimpl
from _pistar.config import Config
from _pistar import is_teststep
from _pistar.utilities.argument_parser import ArgumentTypeError
from _pistar.main import Session, get_report_info, generate_report_and_finish_file
from _pistar.utilities.testcase.case import TestCase

timeout = 2  # Queue operation timeout, unit: seconds


def parallel_option_type(_string):
    _string = _string.strip()
    if _string == "auto" or _string.isdigit() and int(_string) != 0:
        return _string
    else:
        raise ArgumentTypeError(f"invalid value: {_string}, (choose from 'auto' or a positive integer)")


@hookimpl
def pistar_add_option(config: Config):
    config.add_option(
        "-n",
        "--numprocesses",
        action="store",
        type=parallel_option_type,
        required=False,
        default=None,
        help="The number of tasks in parallel should be a positive integer, such as 3. "
             "Or use “auto”, the system will calculate the appropriate parallel"
             " number based on your physical CPU number",
    )


@hookimpl
def pistar_run_loop(session: Session):
    """
    Put all cases into the queue
    Start multiple child processes to pull tasks from the queue (do_execut) function
    Update the result queue to all_case_results
    """
    if session.config.collectonly:
        return None
    if not session.config.get_option("numprocesses"):
        return None
    dispatch_cases_with_parameters(session)
    process_count = get_process_count(session)
    testcase_queue_index, result_queue, cases_dict = init_parallel_queue(session)
    pool = multiprocessing.Pool(processes=process_count)
    for _ in range(process_count):
        pool.apply_async(do_execute, (testcase_queue_index, result_queue, cases_dict))
    pool.close()  # close the pool
    pool.join()  # block the main process
    while not result_queue.empty():
        session.all_case_results.update(result_queue.get())
    return session


def get_process_count(session):
    if session.config.get_option("numprocesses") == "auto":
        return min(multiprocessing.cpu_count(), len(session.cases))
    else:
        return int(session.config.get_option("numprocesses"))


def get_case_condition_names(case):
    args = list()
    for key in case.clazz.__dict__.keys():
        _clazz_attr = getattr(case.clazz, key)
        if not is_teststep(_clazz_attr):
            continue

        # if there is @parameters, indirect is False to not use condition
        indirect = getattr(_clazz_attr, "indirect", None)
        if indirect is False:
            continue
        _args = inspect.signature(_clazz_attr).parameters.keys()  # get the args  in the test step function
        args.extend(_args)
    return set(tuple(args))


def cross_conditions_cases(case: TestCase,
                           case_conditions: List[Set],
                           condition_cases: List[List[TestCase]],
                           cur_case_conditions: Set[str]):
    """
    According to the condition of the current use case,
    it is judged whether there is a dependency relationship with the existing use case condition group,
    and the use and condition with the dependency relationship are combined into one group
    eg:
    condition_cases = [["A", "D"], ["B", "E", "F"], ["C"]]
    case_conditions = [{1, 2}, {3, 4}, {5, 6}]
    case = "G"
    cur_case_conditions = {4, 5}

    ==>
    condition_cases = [["A", "D"], ["B", "E", "F", "C", "G"]]
    case_conditions = [{1, 2}, {3, 4, 5, 6}]
    """
    index_list = list()
    for _index, case_condition in enumerate(case_conditions):
        if case_condition & cur_case_conditions:
            index_list.append(_index)
        else:
            continue
    if len(index_list) == 0:
        case_conditions.append(cur_case_conditions)
        condition_cases.append([case])
    elif len(index_list) == 1:
        case_conditions[index_list[0]] |= cur_case_conditions
        condition_cases[index_list[0]].append(case)
    else:
        first_index = index_list[0]
        for index in index_list[1:]:
            case_conditions[first_index] |= case_conditions[index]
            case_conditions[index] = set()
            condition_cases[first_index] += condition_cases[index]
            condition_cases[index] = []
        case_conditions[first_index] |= cur_case_conditions
        condition_cases[first_index].append(case)


def dispatch_cases_with_parameters(session):
    """
    This method is to combine the same directory and conditional into an array of numbers,
    and make sure the condition is used in the test case
    so that they are executed in the same child process
    """
    condition_func_names = session.condition_manager.name2confunc.keys()
    no_condition_cases = list()
    condition_cases = list(list())
    case_conditions = list(set())
    for case in session.cases:
        case_con_names = get_case_condition_names(case)
        cur_case_conditions = case_con_names & set(condition_func_names)
        if not cur_case_conditions:
            no_condition_cases.append(case)
        else:
            cross_conditions_cases(case, case_conditions, condition_cases, cur_case_conditions)
    # remove empty lists with no data
    condition_cases = list(filter(None, condition_cases))
    # execute more condition cases first
    condition_cases.sort(key=len, reverse=True)
    condition_cases.extend(no_condition_cases)
    session.cases = condition_cases


def init_parallel_queue(session):
    testcase_queue_index = multiprocessing.Manager().Queue()
    result_queue = multiprocessing.Manager().Queue()
    cases_dict = dict()
    for i, case in enumerate(session.cases):
        cases_dict[i] = case
        testcase_queue_index.put(i)
    cases_dict = dill.dumps(cases_dict)
    return testcase_queue_index, result_queue, cases_dict


def do_execute(testcase_queue_index, result_queue, cases_dict):
    """
    The method is to pull the use case index from the queue and get the test case according to the use case dictionary.
    After executing the use case, put the execution result into the result queue and return to the main process.
    When there is one use case left in the list of to-be-executed use cases, more use cases will be pulled from the
    queue to ensure that all next_cases exist
    """
    if testcase_queue_index.empty():
        return

    def pull_queue_testcase():
        """
        Pull the use case for the first time or try to pull the use case again when there is only one use case left
        in the execution list
        """
        _cases = cases_dict.get(testcase_queue_index.get(timeout=timeout), [])
        process_cases.extend(_cases if isinstance(_cases, list) else [_cases])

    cases_dict = dill.loads(cases_dict)
    process_cases = []
    pull_queue_testcase()
    for case in process_cases:
        if case is process_cases[-1] and not testcase_queue_index.empty():
            pull_queue_testcase()
        if case is process_cases[-1]:
            next_case = None
        else:
            next_case = process_cases[process_cases.index(case) + 1]
        hook = case.session.config.hook
        hook.pistar_run_procedure(case=case, next_case=next_case)
        report_info = get_report_info(case)
        result_queue.put(generate_report_and_finish_file(case, report_info))
