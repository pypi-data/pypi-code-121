import json
import os

import pytest

from teko.helpers.file_io import remove_if_exists, write_file
from teko.models.jira_export_test.storage import Storage
from teko.services.jira_export_test.test_case_service import TestCaseService
from teko.services.jira_export_test.test_cycle_service import TestCycleService


@pytest.fixture(scope='function', autouse=True)
def create_test_cycle_after_each_test_function(request):
    funcitem = request._pyfuncitem
    docstring = funcitem._obj.__doc__
    # print(docstring)
    function_name = funcitem.name
    test_id = f'{funcitem.name}-{funcitem.fspath}'
    table_params = funcitem.keywords.get('pytestmark')
    test_index = None
    if table_params and hasattr(funcitem, 'callspec'):
        test_params = tuple(list(funcitem.callspec.params.values()))
        table_params = table_params[0]
        table_params = table_params.args[1]
        if len(table_params) > 0 and not isinstance(table_params[0], tuple):
            table_params = [tuple(list([param])) for param in table_params]

        if test_params in table_params:
            test_index = table_params.index(test_params)
            test_id = f'{funcitem.originalname}-{funcitem.fspath}'

    if docstring and '::JIRA' in docstring:
        test_case = TestCaseService.create_test_case_from_docstring(
            docstring=docstring,
            function_name=function_name,
            test_id=test_id,
            test_index=test_index)
    else:
        test_case = TestCaseService.find_test_case(test_id, test_index=test_index)

    if test_case:
        yield
        TestCycleService.create_test_cycle(test_case.test_name, request.node.result)
    else:
        yield


@pytest.fixture(scope='session', autouse=True)
def generate_test_case_and_test_cycle_file_after_run_all_test():
    test_case_file_path = os.getenv('JIRA_TEST_CASE_ARTIFACT', 'test_case.json')
    test_cycle_file_path = os.getenv('JIRA_TEST_CYCLE_ARTIFACT', 'test_cycle.json')
    remove_if_exists(test_case_file_path)
    remove_if_exists(test_cycle_file_path)
    yield
    test_case = json.dumps(Storage.list_test_case_to_dict(), sort_keys=True, indent=2)
    test_cycle = json.dumps(Storage.list_test_cycle_to_dict(), sort_keys=True, indent=2)
    write_file(test_case_file_path, test_case)
    write_file(test_cycle_file_path, test_cycle)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, 'result', outcome.get_result())
