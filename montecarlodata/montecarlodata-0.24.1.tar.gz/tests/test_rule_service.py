from unittest import TestCase
from unittest.mock import call, Mock

import click
from box import Box
from pycarlo.core import Client

from montecarlodata.rules.rule_service import RuleService


class RuleServiceTest(TestCase):
    RULE_TABLE = """\
╒════════════════════╤═══════════════════╤══════════════════════════════════╕
│ Custom rule UUID   │ Description       │ Updated time (UTC)               │
╞════════════════════╪═══════════════════╪══════════════════════════════════╡
│ test-uuid1         │ test-description1 │ 2000-01-01 00:00:00.000000+00:00 │
├────────────────────┼───────────────────┼──────────────────────────────────┤
│ test-uuid2         │ test-description2 │ 2000-01-01 00:00:00.000000+00:00 │
╘════════════════════╧═══════════════════╧══════════════════════════════════╛"""
    LIMIT = 2
    RULE_TYPE = 'custom_sql'

    def setUp(self):
        self._client = Mock(autospec=Client)
        self._print_func = Mock(autospec=click.echo)
        self._service = RuleService(client=self._client, print_func=self._print_func)

    @staticmethod
    def _rule_response(rule_count):
        return Box(
            {
                'get_custom_rules': {
                    'edges': [
                        {
                            'node': {
                                'uuid': f'test-uuid{i}',
                                'description': f'test-description{i}',
                                'updated_time': '2000-01-01 00:00:00.000000+00:00',
                            }
                        }
                        for i in range(1, rule_count + 1)
                    ]
                }
            }
        )

    def test_list_circuit_breaker_compatible_rules(self):
        self._client.return_value = self._rule_response(self.LIMIT)

        self._service.list_rules(self.RULE_TYPE, self.LIMIT)

        self._print_func.assert_called_once_with(self.RULE_TABLE)

    def test_list_circuit_breaker_compatible_rules_with_more_available(self):
        self._client.return_value = self._rule_response(self.LIMIT + 1)

        self._service.list_rules(self.RULE_TYPE, self.LIMIT)

        expected_calls = [
            call(self.RULE_TABLE),
            call(self._service.MORE_RULES_MESSAGE),
        ]
        self._print_func.assert_has_calls(expected_calls)
