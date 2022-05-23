from typing import Optional, List, Union

from teko.helpers.exceptions import ExportTestException
from teko.models.jira_export_test.test_case import SubTest
from teko.models.jira_export_test.test_step import TestStep
from teko.services.jira_export_test.test_case_service import TestCaseService


def jira_test(
        test_name: Optional[Union[str, List[str]]] = '',
        issue_links: List[str] = [],
        objective: Optional[Union[str, List[str]]] = '',
        precondition: Optional[Union[str, List[str]]] = '',
        priority: Optional[str] = 'Normal',
        folder: Optional[str] = '',
        web_links: Optional[List[str]] = [],
        confluence_links: Optional[List[str]] = [],
        plan: Optional[str] = '',
        sub_tests: Optional[List[Union[dict, SubTest]]] = [],
        scripts: Optional[List[TestStep]] = []):
    def wrapper(f):
        test_id = f'{f.__name__}-{f.__code__.co_filename}'
        if TestCaseService.find_test_case(test_id=test_id):
            raise ExportTestException('Not allow duplicate test function name at same file')

        name = test_name or f.__name__
        name = name.substring(0, 255) if len(name) > 255 else name
        sub_test_models = []
        for test in sub_tests:
            if isinstance(test, SubTest):
                test = test.to_dict()

            sub_test_models.append(SubTest(**test))

        TestCaseService.create_test_case(
            test_id=test_id,
            test_name=name,
            issue_links=issue_links,
            objective=objective,
            precondition=precondition,
            priority=priority,
            folder=folder,
            web_links=web_links,
            confluence_links=confluence_links,
            plan=plan,
            scripts=scripts,
            sub_tests=sub_test_models
        )
        return f

    return wrapper
