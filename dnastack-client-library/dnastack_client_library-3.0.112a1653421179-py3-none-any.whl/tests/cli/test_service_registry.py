from pprint import pformat

from typing import Iterable, Any, Dict

from dnastack.cli.service_registry import EndpointAlreadyExisted, RegistryNotFound
from dnastack.common.simple_stream import SimpleStream
from .base import CliTestCase


class TestCliServiceRegistry(CliTestCase):
    def test_happy_path(self):
        # Fill in the configuration
        self.invoke('endpoints', 'add', 'test-collection-service', '-t', 'collections')
        initial_list = self.simple_invoke('endpoints', 'list')
        self.assert_not_empty(initial_list)

        # Adding a new registry should import all available service endpoints.
        self.invoke('registries', 'add', 'gcp-staging',
                    'https://collection-service.staging.dnastack.com/service-registry/')
        post_adding_list = self.simple_invoke('endpoints', 'list')
        self.assert_not_empty(post_adding_list)
        self.assertNotEqual(initial_list, post_adding_list)

        # Just to ensure that the available service(s) remain in tact.
        self.assert_not_empty([e for e in post_adding_list if e['id'] == 'test-collection-service'],
                              'All previously existing endpoints should remain on the list after adding a registry.')

        # Run the first sync... there should be no changes.
        self.invoke('registries', 'sync', 'gcp-staging')
        post_first_sync_list = self.simple_invoke('endpoints', 'list')
        self.assert_not_empty(post_first_sync_list)
        self.assertEqual(post_adding_list, post_first_sync_list,
                         'There should be no changes after syncing right after adding a new registry.')

        # List all endpoints associated to the registry.
        imported_endpoints = self.simple_invoke('registries', 'list-endpoints', 'gcp-staging')
        self.assert_not_empty(imported_endpoints)

        # Manually remove an endpoint imported from the registry.
        self.invoke('endpoints', 'remove', 'gcp-staging:drs')
        post_single_endpoint_removal_list = self.simple_invoke('endpoints', 'list')
        self.assert_not_empty(post_single_endpoint_removal_list)

        # Attempt to sync again to see if the removed endpoint is restored.
        self.invoke('registries', 'sync', 'gcp-staging')
        post_second_sync_list = self.simple_invoke('endpoints', 'list')
        self.assert_not_empty(post_second_sync_list)
        self.assertNotEqual(post_single_endpoint_removal_list, post_second_sync_list, 'There should be a change.')
        self._assert_if_endpoint_lists_are_identical(post_first_sync_list, post_second_sync_list)

        pre_adding_gcp_staging_endpoints = self.simple_invoke('registries', 'list-endpoints', 'gcp-staging')

        # Adding a new registry should not remove the endpoints associated to other registries.
        self.invoke('registries', 'add', 'gcp-prod',
                    'https://collection-service.prod.dnastack.com/service-registry/')

        post_adding_gcp_staging_endpoints = self.simple_invoke('registries', 'list-endpoints', 'gcp-staging')
        self.assertEqual(pre_adding_gcp_staging_endpoints, post_adding_gcp_staging_endpoints)
        gcp_prod_endpoints = self.simple_invoke('registries', 'list-endpoints', 'gcp-prod')
        self.assert_not_empty(gcp_prod_endpoints)

        # Removing a registry should also remove the associated endpoints.
        self.invoke('registries', 'remove', 'gcp-staging')

        # Ensure that all endpoints from prod still exists after removing the gcp-staging registry.
        self._assert_if_endpoint_lists_are_identical(gcp_prod_endpoints,
                                                     self.simple_invoke('registries', 'list-endpoints', 'gcp-prod'))

        # Removing a registry should also remove the associated endpoints.
        self.invoke('registries', 'remove', 'gcp-prod')
        post_unsync_list = self.simple_invoke('endpoints', 'list')
        self.assert_not_empty(post_unsync_list)
        self.assertNotEqual(post_second_sync_list, post_unsync_list, 'There should be a change.')
        self.assertEqual(initial_list, post_unsync_list,
                         'The current list of endpoints should be the same as the initial list.')

    def test_user_cannot_add_registry_with_known_id(self):
        self.invoke('endpoints', 'add', 'panda-service', '-t', 'collections')
        self.expect_error_from(['registries', 'add', 'panda-service', 'https://panda.faux.dnastack.com'],
                               error_regex='^Endpoint already existed:')

    def test_user_cannot_add_registry_with_known_registry_url(self):
        # Fake a normal service endpoint with the registry URL for testing.
        self.invoke('endpoints', 'add', 'panda-service', '-t', 'collections')
        self.invoke('endpoints', 'set', 'panda-service', 'url',
                    'https://collection-service.staging.dnastack.com/service-registry/')

        # Adding a service registry with the URL that is already used by
        # existing non-service-registry endpoints should be allowed.
        self.invoke('registries', 'add', 'test-registry-001',
                    'https://collection-service.staging.dnastack.com/service-registry/')

        self.expect_error_from(['registries', 'add', 'test-registry-002',
                                'https://collection-service.staging.dnastack.com/service-registry/'],
                               error_regex='^Endpoint already existed:')

    def test_user_cannot_sync_with_unknown_registry(self):
        self.expect_error_from(['registries', 'sync', 'lala'],
                               error_regex='^Registry not found:')

    def _assert_if_endpoint_lists_are_identical(self,
                                                expected_list: Iterable[Dict[str, Any]],
                                                given_list: Iterable[Dict[str, Any]]):
        def _simplify(service: Dict[str, Any]) -> Dict[str, Any]:
            return {
                k: v
                for k, v in service.items()
                if k in ['fallback_authentications', 'authentication', 'type', 'url']
            }

        self.assertEqual(SimpleStream(expected_list).map(_simplify).to_list(),
                         SimpleStream(given_list).map(_simplify).to_list(),
                         'The lists should be identical with exception of some properties, like ID.\n'
                         f'\nExpected:\n{pformat(expected_list, indent=2)}\n'
                         f'\nGiven:\n{pformat(given_list, indent=2)}\n'
                         )
