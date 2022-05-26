from unittest.mock import MagicMock
from uuid import uuid4

from dnastack import CollectionServiceClient
from dnastack.client.service_registry.client import ServiceRegistry, Service
from dnastack.client.service_registry.factory import ClientFactory, UnregisteredServiceEndpointError
from dnastack.client.service_registry.models import ServiceType, Organization
from dnastack.configuration.models import ServiceEndpoint
from dnastack.common.environments import env
from tests.exam_helper import BaseTestCase

SERVICE_REGISTRY_URL = env('E2E_SERVICE_REGISTRY_URL',
                           required=False,
                           default='https://ga4gh-service-registry.staging.dnastack.com/')

# Configurable expectations
# NOTE: The service registry MUST have the expected collection service.
REGISTERED_COLLECTION_SERVICE_URL = env('E2E_REGISTERED_COLLECTION_SERVICE_URL',
                                        required=False,
                                        default='https://collection-service.staging.dnastack.com/')


class TestServiceRegistryEndToEnd(BaseTestCase):
    def test_list_services(self):
        registry = ServiceRegistry(ServiceEndpoint(url=SERVICE_REGISTRY_URL))
        services = [service for service in registry.list_services()]
        self.assert_not_empty(services)
        for service in services:
            self.assertIsInstance(service, Service)


class TestClientFactoryUnit(BaseTestCase):
    mock_service_type_1 = ServiceType(group='com.dnastack',
                                      artifact='panda',
                                      version='1.2.3')

    mock_service_type_1_older = ServiceType(group='com.dnastack',
                                            artifact='panda',
                                            version='1.0.1')

    mock_service_type_2 = ServiceType(group='com.dnastack',
                                      artifact='x-ray',
                                      version='5.7.11')

    mock_service_type_3 = ServiceType(group='com.dnastack',
                                      artifact='collection-service',
                                      version='1.0.0')

    mock_org = Organization(name='dnastack', url='https://dnastack.com')

    mock_service_1 = Service(id=str(uuid4()),
                             name='foo.io panda api',
                             organization=mock_org,
                             type=mock_service_type_1,
                             url='https://foo.io/api/',
                             version='4.5.6')

    # Simulate the same URL but a different service type
    mock_service_2 = Service(id=str(uuid4()),
                             name='foo.io x-ray api',
                             organization=mock_org,
                             type=mock_service_type_2,
                             url='https://foo.io/api/',
                             version='4.5.6')

    # Simulate the same service type but a different URL:
    mock_service_3 = Service(id=str(uuid4()),
                             name='dna panda',
                             organization=mock_org,
                             type=mock_service_type_1,
                             url='https://panda.dnastack.com/delta/november/alpha/',
                             version='7.8.9')

    mock_service_4_public = Service(id=str(uuid4()),
                                    name='zulu',
                                    organization=mock_org,
                                    type=mock_service_type_3,
                                    url='https://zulu.dnastack.com/public/',
                                    version='10.11.12')

    mock_service_4_restricted = Service(id=str(uuid4()),
                                        authentication=[
                                            dict(
                                                authorizationUrl='http://foo.io/oauth2/authorize',
                                                clientId='fake-client-id',
                                                clientSecret='fake-client-secret',
                                                grantType='client_credentials',
                                                resource='http://foo.io/api/',
                                                accessTokenUrl='http://foo.io/oauth2/token',
                                            )
                                        ],
                                        name='zulu',
                                        organization=mock_org,
                                        type=mock_service_type_3,
                                        url='https://zulu.dnastack.com/restricted/',
                                        version='10.11.12')

    mock_registry_1 = MagicMock(ServiceRegistry)
    mock_registry_1.list_services.return_value = [mock_service_3, mock_service_4_public, mock_service_4_restricted]

    mock_registry_2 = MagicMock(ServiceRegistry)
    mock_registry_2.list_services.return_value = [mock_service_1, mock_service_2]

    def test_find_services(self):
        factory = ClientFactory([self.mock_registry_1, self.mock_registry_2])

        # Search combo: exact match, types (found: 2)
        results = self.drain_iterable(factory.find_services(exact_match=True,
                                                            types=[self.mock_service_type_1,
                                                                   self.mock_service_type_1_older]))
        self.assertEqual(len(results), 2)

        # Search combo: loosely match, types (found: 3)
        results = self.drain_iterable(factory.find_services(exact_match=False,
                                                            types=[self.mock_service_type_1,
                                                                   self.mock_service_type_2]))
        self.assertEqual(len(results), 3)

        # Search combo: exact match, url (found: 1)
        results = self.drain_iterable(factory.find_services(exact_match=True,
                                                            url='https://foo.io/api/'))
        self.assertEqual(len(results), 2)

        # Search combo: exact match, incomplete but identical url (found: 0)
        results = self.drain_iterable(factory.find_services(exact_match=True,
                                                            url='https://foo.io/api'))
        self.assertEqual(len(results), 0)

        # Search combo: loosely match, incomplete but identical url (found: 2)
        results = self.drain_iterable(factory.find_services(exact_match=False,
                                                            url='https://foo.io/api'))
        self.assertEqual(len(results), 2)

        # Search combo: loosely match, types, incomplete but identical url (found: 2)
        results = self.drain_iterable(factory.find_services(exact_match=False,
                                                            types=[self.mock_service_type_1,
                                                                   self.mock_service_type_2],
                                                            url='https://foo.io/api'))
        self.assertEqual(len(results), 2)

        # Search combo: loosely match, types, exact url (found: 1)
        results = self.drain_iterable(factory.find_services(exact_match=True,
                                                            types=[self.mock_service_type_1,
                                                                   self.mock_service_type_1_older],
                                                            url='https://foo.io/api/'))
        self.assertEqual(len(results), 1)

    def test_create_client_with_public_access_ok(self):
        factory = ClientFactory([self.mock_registry_1, self.mock_registry_2])
        client = factory.create(CollectionServiceClient, self.mock_service_4_public.url)
        self.assertIsInstance(client, CollectionServiceClient)
        self.assertEqual(client.url, self.mock_service_4_public.url)
        self.assertFalse(client.require_authentication())

    def test_create_client_with_restricted_access_ok(self):
        factory = ClientFactory([self.mock_registry_1, self.mock_registry_2])
        client = factory.create(CollectionServiceClient, self.mock_service_4_restricted.url)
        self.assertIsInstance(client, CollectionServiceClient)
        self.assertTrue(client.require_authentication())


class TestClientFactoryEndToEnd(BaseTestCase):
    def test_find_services(self):
        collection_service_types = CollectionServiceClient.get_supported_service_types()
        search_url = REGISTERED_COLLECTION_SERVICE_URL[:int(len(REGISTERED_COLLECTION_SERVICE_URL) / 2)]
        search_filter = dict(types=collection_service_types, url=search_url)

        factory = ClientFactory.use(SERVICE_REGISTRY_URL)

        # Suppose that the expected URL is registered. An exact-match search with the expected URL
        # must yield at least one result.
        exact_match_result_count = len(
            self.drain_iterable(factory.find_services(exact_match=True,
                                                      types=collection_service_types,
                                                      url=REGISTERED_COLLECTION_SERVICE_URL))
        )
        self.assertGreaterEqual(exact_match_result_count, 1)

        # An exact-match search with the partial URL yields nothing.
        exact_match_result_count = len(self.drain_iterable(factory.find_services(exact_match=True, **search_filter)))
        self.assertEqual(exact_match_result_count, 0)

        # A loosely-match search with the partial URL yields at least something.
        loosely_match_result_count = len(self.drain_iterable(factory.find_services(exact_match=False, **search_filter)))
        self.assertGreaterEqual(loosely_match_result_count, 1)

    def test_create_ok(self):
        factory = ClientFactory.use(SERVICE_REGISTRY_URL)
        client = factory.create(CollectionServiceClient, REGISTERED_COLLECTION_SERVICE_URL)
        self.assertIsInstance(client, CollectionServiceClient)

    def test_create_failed(self):
        factory = ClientFactory.use(SERVICE_REGISTRY_URL)

        with self.assertRaises(UnregisteredServiceEndpointError):
            factory.create(CollectionServiceClient, REGISTERED_COLLECTION_SERVICE_URL[:-10])
