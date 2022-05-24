import re
import copy
from teko.models.jira_export_test.storage import Storage
from teko.models.jira_export_test.test_case import TestCase
from teko.models.jira_export_test.test_step import TestStep
from teko.helpers.clog import CLog

__author__ = 'Dungntc'


class TestCaseService:
    _TUPLE_REGEX = '( *(name|objective|precondition)(, *(name|objective|precondition)){1,2}):'

    @classmethod
    def create_test_case(cls, **kwargs):
        test_case = TestCase(**kwargs)
        Storage.list_test_case.append(test_case)
        return test_case

    @classmethod
    def find_test_case(cls, test_id, test_index=None):
        for test_case in Storage.list_test_case:
            if test_case.test_id == test_id:
                new_test_case = copy.copy(test_case)
                if test_index is None:
                    return test_case

                cls._set_attr_test_case(test_case, new_test_case, 'test_name', test_index)
                cls._set_attr_test_case(test_case, new_test_case, 'objective', test_index)
                cls._set_attr_test_case(test_case, new_test_case, 'precondition', test_index)
                if test_case.sub_tests and test_index < len(test_case.sub_tests):
                    sub_test = test_case.sub_tests[test_index]
                    print(type(sub_test), dir(sub_test))
                    if sub_test.test_name:
                        new_test_case.test_name = sub_test.test_name

                    if sub_test.objective:
                        new_test_case.objective = sub_test.objective

                    if sub_test.precondition:
                        new_test_case.precondition = sub_test.precondition
                elif test_case.sub_tests and test_index >= len(test_case.sub_tests):
                    # test that will not be added to test cases
                    return None

                Storage.list_test_case.append(new_test_case)
                return new_test_case

        return None

    @classmethod
    def _set_attr_test_case(cls, test_case: TestCase, new_test_case: TestCase, field_name: str, test_index: int):
        if isinstance(getattr(test_case, field_name), list) and test_index < len(getattr(test_case, field_name)):
            setattr(new_test_case, field_name, getattr(test_case, field_name)[test_index])
        elif isinstance(getattr(test_case, field_name), list) and test_index >= len(getattr(test_case, field_name)):
            return None

    @classmethod
    def create_test_case_from_docstring(cls, docstring, function_name, test_id, test_index=None):
        MAX_NAME_LENGTH = 255
        if len(function_name) > MAX_NAME_LENGTH:
            function_name = function_name.substring(0, MAX_NAME_LENGTH)
        docstring = docstring + '::END_JIRA'
        scripts = []
        m_scripts_text = TestCaseService.parse_string(docstring, 'scripts:')
        if m_scripts_text:
            for test_step_text in m_scripts_text.split('description:'):
                if 'expectedResult:' and 'testData:' in test_step_text:
                    test_step = TestStep(
                        description=test_step_text[:test_step_text.index('expectedResult:')].strip(),
                        expected_result=test_step_text[test_step_text.index('expectedResult:') + 15
                                                       :test_step_text.index('testData:')].strip(),
                        test_data=test_step_text[test_step_text.index('testData:') + 9:].strip()
                    )
                    scripts.append(test_step)

        try:
            test_case = TestCase(
                test_id=test_id,
                test_name=TestCaseService.parse_string(docstring, 'name:', function_name, test_index=test_index),
                issue_links=TestCaseService.parse_array(docstring, 'issueLinks:'),
                objective=TestCaseService.parse_string(docstring, 'objective:', test_index=test_index),
                precondition=TestCaseService.parse_string(docstring, 'precondition:', test_index=test_index),
                priority=TestCaseService.parse_string(docstring, 'priority:', 'Normal'),
                folder=TestCaseService.parse_string(docstring, 'folder:'),
                web_links=TestCaseService.parse_array(docstring, 'webLinks:'),
                confluence_links=TestCaseService.parse_array(docstring, 'confluenceLinks:'),
                plan=TestCaseService.parse_string(docstring, 'plan:'),
                scripts=scripts
            )

            if test_index is not None:
                test_case = cls.add_sub_test_case_from_doc_string(docstring, test_index, test_case)

            Storage.list_test_case.append(test_case)
            return test_case
        except Exception as e:
            print(str(e))
            return None

    @classmethod
    def parse_string(cls, docstring, key, default='', test_index=None):
        base_regex = '(?s:([^:]*?)(issueLinks:|objective:|precondition:|priority:|folder:|' \
                     'confluenceLinks:|webLinks:|plan:|scripts:|::END_JIRA))'
        m_key = re.search(rf'{key}{base_regex}', docstring, re.MULTILINE)
        if m_key:
            m_value = m_key.group(1).strip()
            if test_index is not None:
                try:
                    m_value = list(eval(m_value))
                    return m_value[test_index].strip()
                except IndexError as ie:
                    raise ie
                except Exception as e:
                    return m_value

            return m_value
        else:
            return default

    @classmethod
    def parse_array(cls, docstring, key, default=[]):
        base_regex = '(?s:(.*?)(issueLinks:|objective:|precondition:|priority:|folder:|confluenceLinks:|webLinks:|plan:' \
                     '|scripts:|::END_JIRA|,(name|objective|precondition):))'
        m_key = re.search(rf'{key}{base_regex}', docstring, re.IGNORECASE)
        if m_key:
            return [k.strip() for k in m_key.group(1).split(',')]
        else:
            return default

    @classmethod
    def add_sub_test_case_from_doc_string(cls, docstring: str, test_index: int, test_case: TestCase):
        base_regex = '(?s:([^:]*?)(name:|issueLinks:|objective:|precondition:|priority:' \
                     '|folder:|confluenceLinks:|webLinks:|plan:|scripts:|::END_JIRA))'
        m_key = re.search(rf'{cls._TUPLE_REGEX}{base_regex}', docstring, re.MULTILINE)
        if not m_key:
            return test_case

        try:
            tuple_fields = m_key.group(1).strip().replace(' ', '').replace(':', '')
            tuple_fields = tuple_fields.split(',')
            tuple_values = m_key.group(5).strip().replace('\n', '')
            tuple_values = eval(tuple_values)
            if len(tuple_fields) <= test_index:
                return test_case

            tuple_value = tuple_values[test_index]
            if not isinstance(tuple_value, tuple):
                tuple_value = (tuple_value,)

            if len(tuple_fields) != len(tuple_value):
                CLog.warn(f'[EXTRACT TESTCASE]Number of values <> number of fields')
                return test_case

            for idx, field in enumerate(tuple_fields):
                if field == 'name':
                    test_case.test_name = tuple_value[idx]
                elif field == 'objective':
                    test_case.objective = tuple_value[idx]
                elif field == 'precondition':
                    test_case.precondition = tuple_value[idx]
                else:
                    CLog.warn(f'[EXTRACT TESTCASE]Not supported field {field}')
                    continue

            return test_case
        except Exception as e:
            return test_case
