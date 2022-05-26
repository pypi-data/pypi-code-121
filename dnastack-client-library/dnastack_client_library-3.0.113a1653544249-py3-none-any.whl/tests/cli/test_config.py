import yaml
from typing import Optional

from dnastack.client.collections.client import STANDARD_COLLECTION_SERVICE_TYPE_V1_0, \
    EXPLORER_COLLECTION_SERVICE_TYPE_V1_0
from dnastack.client.service_registry.models import ServiceType
from dnastack.configuration.models import Configuration
from .base import CliTestCase


class TestConfiguration(CliTestCase):
    def test_list_available_properties(self):
        result = self.invoke('config', 'available-properties')
        self.assertIn('collections.url', result.output)
        self.assertIn('data_connect.authentication.client_id', result.output)

    def test_crud_operations_for_client_with_multiple_supported_types(self):
        # Get all configurations when there is nothing defined.
        result = self.invoke('config', 'list')
        self.assertEqual('{}',
                         result.output.strip(),
                         'When the configuration file does not exist, it should show as empty string.')

        # Get the property when there is nothing defined.
        result = self.invoke('config', 'get', 'collections.url')
        self.assertEqual('null',
                         result.output.strip(),
                         'When the configuration is not set, it should show as empty string.')

        # Set the property.
        self.invoke('config', 'set', 'collections.url', 'https://cs-000', bypass_error=False)
        self.assert_config_property('collections.url', 'https://cs-000', 'Set the endpoint URL')

        # When it is set for the first time, the service type will be filled in automatically by the short service type.
        # NOTE: This is the default type.
        self._check_service_type('collections', EXPLORER_COLLECTION_SERVICE_TYPE_V1_0)

        test_endpoint_001 = 'test-collection-endpoint-001'

        self.invoke('config', 'add-endpoint', 'collections', test_endpoint_001)
        self.invoke('config', 'add-endpoint', 'collections', test_endpoint_001, bypass_error=True)

        self.assertEqual(len([e for e in self._get_full_config().endpoints if e.id == test_endpoint_001]), 1)

        self.invoke('config', 'set', '-i', test_endpoint_001, 'collections.url', 'https://cs-001')
        self.invoke('config', 'set', '-i', test_endpoint_001, 'collections.type.group',
                    STANDARD_COLLECTION_SERVICE_TYPE_V1_0.group)
        # NOTE: This is the type for the explorer.
        self._check_service_type('collections', STANDARD_COLLECTION_SERVICE_TYPE_V1_0, test_endpoint_001)
        result = self.invoke('config', 'get', '-i', test_endpoint_001, 'collections.url')
        self.assertEqual(result.output.strip(), 'https://cs-001')

        test_endpoint_002 = 'test-collection-endpoint-002'

        self.invoke('config', 'add-endpoint', 'collections', test_endpoint_002)
        endpoints = self._get_full_config().endpoints
        self.assertEqual(len([e for e in endpoints if e.id == test_endpoint_001]), 1)
        self.assertEqual(len([e for e in endpoints if e.id == test_endpoint_002]), 1)
        self.assertEqual(len([e for e in endpoints if e.type.artifact == 'collection-service']), 3)

        self.invoke('config', 'remove-endpoint', 'collections', test_endpoint_001)
        endpoints = self._get_full_config().endpoints
        self.assertEqual(len([e for e in endpoints if e.id == test_endpoint_001]), 0)
        self.assertEqual(len([e for e in endpoints if e.id == test_endpoint_002]), 1)
        self.assertEqual(len([e for e in endpoints if e.type.artifact == 'collection-service']), 2)

        self.invoke('config', 'remove-endpoint', 'collections', test_endpoint_002)
        endpoints = self._get_full_config().endpoints
        self.assertEqual(len([e for e in endpoints if e.id == test_endpoint_001]), 0)
        self.assertEqual(len([e for e in endpoints if e.id == test_endpoint_002]), 0)
        self.assertEqual(len([e for e in endpoints if e.type.artifact == 'collection-service']), 1)

    def test_crud_operations_for_client_with_one_supported_type(self):
        # Get all configurations when there is nothing defined.
        result = self.invoke('config', 'list')
        self.assertEqual('{}',
                         result.output.strip(),
                         'When the configuration file does not exist, it should show as empty string.')

        # Get the property when there is nothing defined.
        result = self.invoke('config', 'get', 'data_connect.url')
        self.assertEqual('null',
                         result.output.strip(),
                         'When the configuration is not set, it should show as empty string.')

        # Set the property.
        self.invoke('config', 'set', 'data_connect.url', 'https://data-connect.dnastack.com', bypass_error=False)
        self.assert_config_property('data_connect.url', 'https://data-connect.dnastack.com', 'Set the endpoint URL')

        # When it is set for the first time, the service type will be filled in automatically by the short service type.
        self.assert_config_property('data_connect.type.group', 'org.ga4gh', 'Type group is not defined properly')
        self.assert_config_property('data_connect.type.artifact', 'data-connect',
                                    'Type artifact is not defined properly')
        self.assert_config_property('data_connect.type.version', '1.0.0', 'Type version is not defined properly')

        # Set the nested property.
        self.invoke('config', 'set', 'data_connect.authentication.client_id', 'foo', bypass_error=False)
        self.assert_config_property('data_connect.url', 'https://data-connect.dnastack.com',
                                    'The endpoint URL should remain the same after dealing with one nested property.')
        self.assert_config_property('data_connect.authentication.client_id', 'foo',
                                    'The client ID should be set to the expected value.')

        self.invoke('config', 'set', 'data_connect.authentication.client_secret', 'bar', bypass_error=False)
        self.assert_config_property('data_connect.url', 'https://data-connect.dnastack.com',
                                    'The endpoint URL should remain the same after dealing with two nested properties.')
        self.assert_config_property('data_connect.authentication.client_id', 'foo',
                                    'The client ID should remain the same after dealing with two nested properties.')
        self.assert_config_property('data_connect.authentication.client_secret', 'bar',
                                    'The client secret should be set to the expected value.')

    def test_set_and_unset_mandatory_properties(self):
        self.invoke('config', 'set', 'data_connect.url', 'https://www.foo.com')
        self.invoke('config', 'unset', 'data_connect.url')
        self.invoke('config', 'get', 'data_connect.url')

    def test_get_unknown_properties(self):
        with self.assertRaises(SystemExit):
            self.invoke('config', 'get', 'foo.url')

        with self.assertRaises(SystemExit):
            self.invoke('config', 'get', 'data_connect.foo_url')

    def test_set_unknown_properties(self):
        with self.assertRaises(SystemExit):
            self.invoke('config', 'set', 'foo.url', 'hello')

        with self.assertRaises(SystemExit):
            self.invoke('config', 'set', 'data_connect.foo_url', 'eh?')

    def assert_config_property(self,
                               property_path: str,
                               expected_value: str,
                               summary: str,
                               endpoint_id: Optional[str] = None):
        result = self.invoke('config', 'get', '-i', endpoint_id, property_path) \
            if endpoint_id \
            else self.invoke('config', 'get', property_path)
        given_value = result.output.strip()
        self.assertEqual(expected_value, given_value,
                         f'Summary: {summary}\nExpected: [{expected_value}]\nGiven: [{given_value}]')

    def _check_service_type(self,
                            service_short_type: str,
                            service_type: ServiceType,
                            endpoint_id: Optional[str] = None
                            ):
        for p_name, p_value in service_type.dict().items():
            self.assert_config_property(f'{service_short_type}.type.{p_name}',
                                        p_value,
                                        f'The {p_name} of the type is not defined properly',
                                        endpoint_id)

    def _get_full_config(self) -> Configuration:
        result = self.invoke('config', 'list')
        return Configuration(**yaml.load(result.output, Loader=yaml.SafeLoader))