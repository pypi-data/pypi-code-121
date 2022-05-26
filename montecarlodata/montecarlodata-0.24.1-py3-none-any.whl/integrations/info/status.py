from typing import Optional, List, Dict

import click
from tabulate import tabulate

from montecarlodata.common.common import normalize_gql
from montecarlodata.common.user import UserService
from montecarlodata.config import Config
from montecarlodata.errors import manage_errors
from montecarlodata.integrations.onboarding.fields import GQL_TO_FRIENDLY_CONNECTION_MAP


class OnboardingStatusService:
    _INTEGRATION_FRIENDLY_HEADERS = ['Integration', 'Name', 'ID', 'Connection', 'Created on (UTC)']

    def __init__(self, config: Config, user_service: Optional[UserService] = None):
        self._abort_on_error = True
        self._user_service = user_service or UserService(config=config)

    @manage_errors
    def display_integrations(self, headers: Optional[str] = 'firstrow', table_format: Optional[str] = 'fancy_grid'):
        """
        Display active integrations in an easy to read table. E.g.
        ╒═══════════════════╤═══════════╤══════════════════════════════════════╤═════════════════════════════╤══════════════════════════════════╕
        │ Integration       │ Name      │ ID                                   │ Connection                  │ Created on (UTC)                 │
        ╞═══════════════════╪═══════════╪══════════════════════════════════════╪═════════════════════════════╪══════════════════════════════════╡
        │ Snowflake         │ rick_test │ 9403e385-1a56-4c3b-b185-4f2bb8e324d3 │ account: hda34492.us-east-1 │ 2022-03-25T19:55:11.858022+00:00 │
        ╘═══════════════════╧═══════════╧══════════════════════════════════════╧═════════════════════════════╧══════════════════════════════════╛
        """
        table = [self._INTEGRATION_FRIENDLY_HEADERS]
        for integration in (self._user_service.warehouses or [{}]) + (self._user_service.bi_containers or [{}]):
            table += self._build_table_record(name=integration.get('name'), connections=integration.get('connections'))
        click.echo(tabulate(table, headers=headers, tablefmt=table_format))

    def _build_table_record(self, name: str, connections: List[Dict]) -> List[List[str]]:
        table = []
        for connection in connections or []:
            table.append(
                [
                    GQL_TO_FRIENDLY_CONNECTION_MAP.get(normalize_gql(connection['type']), connection['type']),
                    name,
                    connection['uuid'],
                    self._build_connection_info(connection),
                    connection['createdOn']
                ]
            )  # order by the friendly headers, defaulting to gql response if not found
        return table

    @staticmethod
    def _build_connection_info(connection: Dict) -> Optional[str]:
        identifier = connection.get('connectionIdentifier')
        if identifier:
            key = identifier.get('key')
            value = identifier.get('value')
            return f'{key}: {value}'
        return None
