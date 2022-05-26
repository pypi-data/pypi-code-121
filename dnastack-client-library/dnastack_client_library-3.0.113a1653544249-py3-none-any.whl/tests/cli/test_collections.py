import re

from dnastack.client.collections.client import STANDARD_COLLECTION_SERVICE_TYPE_V1_0
from dnastack.common.environments import env
from .base import CliTestCase
from ..exam_helper import client_id, client_secret, token_endpoint


class TestCollectionsCommand(CliTestCase):
    _base_config = {
        '.mode': 'standard',
        '.authentication.client_id': client_id,
        '.authentication.client_secret': client_secret,
        '.authentication.grant_type': 'client_credentials',
        '.authentication.token_endpoint': token_endpoint,
    }

    def setUp(self) -> None:
        super().setUp()

        endpoints = [
            ('collections', 'E2E_COLLECTION_SERVICE_URL', 'https://collection-service.viral.ai/'),
            ('data_connect', 'E2E_PROTECTED_DATA_CONNECT_URL', 'https://collection-service.viral.ai/data-connect/'),
        ]

        final_config = dict()

        for service_short_type, var_name, default in endpoints:
            endpoint_url = env(var_name, default=default)

            final_config[f'{service_short_type}.url'] = endpoint_url
            final_config[f'{service_short_type}.authentication.resource_url'] = endpoint_url
            final_config.update({
                service_short_type + suffix: value
                for suffix, value in self._base_config.items()
            })

            if service_short_type == 'collections':
                full_service_type = STANDARD_COLLECTION_SERVICE_TYPE_V1_0
                final_config[f'{service_short_type}.type.group'] = full_service_type.group
                final_config[f'{service_short_type}.type.artifact'] = full_service_type.artifact
                final_config[f'{service_short_type}.type.version'] = full_service_type.version

        self._configure(final_config)
        # self.execute(f'cat {self._config_file_path}')

    def test_against_current_implementation(self):
        """ This is to test with the current implementation of collection service. """

        # Test listing collection
        collections = self.simple_invoke('collections', 'list')
        self.assertGreaterEqual(len(collections), 1, 'Must have at least one collection for this test')

        first_collection = collections[0]
        self.assertIn('id', first_collection)
        self.assertIn('name', first_collection)
        self.assertIn('slugName', first_collection)
        self.assertIn('description', first_collection)
        self.assertIn('itemsQuery', first_collection)

        # Test listing tables in the collection
        tables = self.simple_invoke('collections', 'tables', 'list')
        self.assertGreaterEqual(len(tables), 0)

        # Prepare for the test query.
        max_size = 10
        query = first_collection['itemsQuery']
        # Limit the result
        if re.search(r' limit \d+\s?', query, re.I):
            query = query + ' LIMIT ' + max_size

        # JSON version
        items_from_direct_query = self.simple_invoke('collections', 'query', query)
        self.assertLessEqual(len(items_from_direct_query), max_size, f'Expected upto {max_size} rows')

        # CSV version
        result = self.invoke('collections', 'query', '-f', 'csv', query)
        lines = result.output.split('\n')
        self.assertLessEqual(len(lines), max_size + 1, f'Expected upto {max_size} lines, excluding headers')
        for line in lines:
            if not line.strip():
                continue
            self.assertTrue(',' in line, f'The content does not seem to be a CSV-formatted string.')

        # Test the list-item command.
        items_from_command = self.simple_invoke('collections', 'list-items',
                                                '-c', first_collection['slugName'],
                                                '-l', str(max_size))
        self.assertLessEqual(len(items_from_command), max_size, f'Expected upto {max_size} rows')

        common_ids = set([i['id'] for i in items_from_direct_query]).intersection([i['id'] for i in items_from_command])
        self.assert_not_empty(common_ids)

    def test_against_legacy_implementation(self):
        """ This is to test with the legacy implementation of collection service. """

        # Test listing collection
        collections = self.simple_invoke('collections', 'list')
        self.assertGreaterEqual(len(collections), 1, 'Must have at least one collection for this test')

        first_collection = collections[0]
        self.assertIn('id', first_collection)
        self.assertIn('name', first_collection)
        self.assertIn('slugName', first_collection)
        self.assertIn('description', first_collection)
        self.assertIn('itemsQuery', first_collection)

        collection_identifier = first_collection['slugName']

        # Test listing tables in the collection
        tables = self.simple_invoke('collections', 'tables', 'list', '--collection', collection_identifier)
        self.assertGreaterEqual(len(tables), 0)

        # Prepare for the test query.
        max_size = 10
        query = first_collection['itemsQuery']
        # Limit the result
        if re.search(r' limit \d+\s?', query, re.I):
            query = query + ' LIMIT ' + max_size

        # JSON version
        rows = self.simple_invoke('collections', 'query', '--collection', collection_identifier, query)
        self.assertLessEqual(len(rows), max_size, f'Expected upto {max_size} rows')

        # CSV version
        result = self.invoke('collections', 'query', '--collection', collection_identifier, '-f', 'csv', query)
        lines = result.output.split('\n')
        self.assertLessEqual(len(lines), max_size + 1, f'Expected upto {max_size} lines, excluding headers')
        for line in lines:
            if not line.strip():
                continue
            self.assertTrue(',' in line, f'The content does not seem to be a CSV-formatted string.')
