import logging
from typing import List

from teko.models.jira_export_test.test_case import TestCase
from teko.models.jira_export_test.test_cycle import TestCycle

_logger = logging.getLogger(__name__)


class Storage:
    list_test_case: List[TestCase] = []
    list_test_cycle: List[TestCycle] = []

    @classmethod
    def list_test_case_to_dict(cls):
        _logger.info(f'Generated {len(cls.list_test_case)} test case')
        return [test_case.to_dict()
                for test_case in cls.list_test_case
                if isinstance(test_case.test_name, str)
                and isinstance(test_case.precondition, str)
                and isinstance(test_case.objective, str)]

    @classmethod
    def list_test_cycle_to_dict(cls):
        _logger.info(f'Generated {len(cls.list_test_cycle)} test cycle')
        return [test_cycle.to_dict() for test_cycle in cls.list_test_cycle]
