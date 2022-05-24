import re

from dnastack.client.collections.client import CollectionServiceClient, Collection, \
    STANDARD_COLLECTION_SERVICE_TYPE_V1_0
from dnastack.client.data_connect import DATA_CONNECT_TYPE_V1_0, DataConnectClient
from dnastack.exceptions import ServiceException
from dnastack.common.environments import env
from ..exam_helper import initialize_test_endpoint, ReversibleTestCase, BaseTestCase


class TestCollectionsClient(ReversibleTestCase, BaseTestCase):
    """ Test a client for Collection Service """

    # Test-specified
    collection_endpoint = initialize_test_endpoint(env('E2E_COLLECTION_SERVICE_URL',
                                                       default='https://collection-service.viral.ai/'),
                                                   type=STANDARD_COLLECTION_SERVICE_TYPE_V1_0)
    data_connect_endpoint = initialize_test_endpoint(env('E2E_PROTECTED_DATA_CONNECT_URL',
                                                         default='https://collection-service.viral.ai/data-connect/'),
                                                     type=DATA_CONNECT_TYPE_V1_0)

    def test_auth_client_interacts_with_collection_api(self):
        collection_client = CollectionServiceClient.make(self.collection_endpoint)

        collections = collection_client.list_collections()

        self.assertGreater(len(collections), 0)
        self.assertIsInstance(collections[0], Collection)
        collection = collections[0]
        self.assert_not_empty(collection.id)
        self.assert_not_empty(collection.slugName)

        with self.assertRaisesRegex(ServiceException, 'Collection not found'):
            collection_client.get('foo-bar')

    def test_auth_client_interacts_with_data_connect_api_without_collection(self):
        collection_client = CollectionServiceClient.make(self.collection_endpoint)
        data_connect_client = DataConnectClient.make(collection_client.data_connect_endpoint())
        tables = data_connect_client.list_tables()
        self.assert_not_empty(tables)
        first_table = tables[0]
        self.assert_not_empty([row for row in data_connect_client.query(f'SELECT * FROM {first_table.name} LIMIT 10')])

    def test_auth_client_interacts_with_data_connect_api_with_collection_for_backward_compatibility(self):
        re_table_type = re.compile(r"type\s*=\s*'table'")

        collection_client = CollectionServiceClient.make(self.collection_endpoint)

        collections = collection_client.list_collections()
        self.assert_not_empty(collections)

        target_collection = [c for c in collections if re_table_type.search(c.itemsQuery)][0]

        data_connect_client = DataConnectClient.make(collection_client.data_connect_endpoint(target_collection))
        tables = data_connect_client.list_tables()
        self.assert_not_empty(tables)
        first_table = tables[0]
        self.assert_not_empty([row for row in data_connect_client.query(f'SELECT * FROM {first_table.name} LIMIT 10')])
