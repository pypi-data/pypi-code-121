from typing import Callable, Optional

import click
from pycarlo.core import Client, Query
from tabulate import tabulate

from montecarlodata.errors import manage_errors


class RuleService:
    CIRCUIT_BREAKER_RULE_HEADERS = ('Custom rule UUID', 'Description', 'Updated time (UTC)')
    MORE_RULES_MESSAGE = 'There are more monitors available. Increase the limit to view them.'

    PSEUDO_RULE_TYPE_CB_COMPATIBLE = 'circuit_breaker_compatible'
    RULE_TYPE_CUSTOM_SQL = 'custom_sql'
    RULE_TYPE_TABLE_METRIC = 'table_metric'
    RULE_TYPE_FRESHNESS = 'freshness'
    RULE_TYPES = [
        PSEUDO_RULE_TYPE_CB_COMPATIBLE,
        RULE_TYPE_CUSTOM_SQL,
        RULE_TYPE_TABLE_METRIC,
        RULE_TYPE_FRESHNESS,
    ]

    def __init__(
        self,
        client: Optional[Client] = None,
        print_func: Optional[Callable] = click.echo,
    ):
        self._client = client or Client()
        self._print_func = print_func

    @manage_errors
    def list_rules(self, rule_type: str, limit: int):
        query = Query()
        query.get_custom_rules(rule_type=rule_type, first=limit + 1).edges.node.__fields__(
            'uuid',
            'description',
            'updated_time'
        )
        response = self._client(query)

        compatible_rules = (edge.node for edge in response.get_custom_rules.edges)
        table = [(rule.uuid, rule.description, rule.updated_time) for rule in compatible_rules]

        more_rules_available = False
        if len(table) > limit:
            table = table[:-1]
            more_rules_available = True

        self._print_func(tabulate(table, headers=self.CIRCUIT_BREAKER_RULE_HEADERS, tablefmt='fancy_grid'))

        if more_rules_available:
            self._print_func(self.MORE_RULES_MESSAGE)
