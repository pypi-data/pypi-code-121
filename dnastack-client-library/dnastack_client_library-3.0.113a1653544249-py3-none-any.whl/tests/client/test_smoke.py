from typing import Any, Dict, Iterator, Optional, List

from dnastack import CollectionServiceClient, DataConnectClient
from dnastack.client.base_exceptions import ApiError
from dnastack.client.collections.client import EXPLORER_COLLECTION_SERVICE_TYPE_V1_0
from dnastack.configuration.models import ServiceEndpoint
from dnastack.common.logger import get_logger
from ..exam_helper import BaseTestCase


class TestSmoke(BaseTestCase):
    _logger = get_logger('lib/smoke_test')

    def test_demo(self):
        """
        This is based on the public documentation.

        .. note:: This test is specifically designed for a certain deployment.
        """
        endpoint = ServiceEndpoint(url='https://viral.ai/api/', type=EXPLORER_COLLECTION_SERVICE_TYPE_V1_0)
        client = CollectionServiceClient.make(endpoint)

        self._logger.debug('Listing collections...')
        collections = client.list_collections()
        self.assertGreater(len(collections), 0, f'{endpoint.url} should have at least ONE collection.')

        target_collection = collections[0]

        data_connect = DataConnectClient.make(client.data_connect_endpoint(target_collection))

        self._logger.debug('Listing tables...')
        tables = data_connect.list_tables()
        self.assertGreater(len(tables), 0, f'{target_collection.name} should have at least ONE table.')

        table = data_connect.table(tables[0])

        table_info = table.info
        self.assertIsNotNone(table_info.name)
        self.assert_not_empty(table_info.data_model['properties'])

        self.assert_not_empty(self._get_subset_of(table.data, 100))

        queried_tables = [r for r in data_connect.query(target_collection.itemsQuery)]
        queried_table_count = len(queried_tables)

        table_index = 0

        while table_index < len(queried_tables):
            target_table_name = queried_tables[table_index]['qualified_table_name']

            if len(target_table_name.split(r'.')) < 3:
                target_table_name = f'ncbi_sra.{target_table_name}'

            self._logger.debug(f'Querying from {target_table_name}...')
            query = f'SELECT * FROM {target_table_name} LIMIT 20000'

            try:
                rows = self._get_subset_of(data_connect.query(query))
            except ApiError as e:
                self._logger.warning(f'T/{target_table_name}: Encountered unexpected error.')
                if table_index < queried_table_count - 1:
                    self._logger.warning('Try the next table...')
                    table_index += 1
                    continue
                else:
                    self.fail('No more table usable to this test')

            if len(rows) == 0:
                self._logger.warning(f'T/{target_table_name}: No data.')
                if table_index < queried_table_count - 1:
                    self._logger.warning('Try the next table...')
                    table_index += 1
                    continue
                else:
                    self.fail('No more table usable to this test')
            else:
                break

        if table_index == len(queried_tables):
            self.fail(f"Cannot test as there is no data in any of {', '.join([t['qualified_table_name'] for t in queried_tables])}")

    def _get_subset_of(self, iterator: Iterator[Dict[str, Any]], max_size: Optional[int] = None) -> List[Dict[str, Any]]:
        rows = []

        for row in iterator:
            rows.append(row)

            if max_size and len(rows) >= max_size:
                break

            if len(rows) % 10000 == 0:
                self._logger.debug(f'Receiving {len(rows)} rows...')

            self.assertGreater(len(row.keys()), 0)

        self._logger.debug(f'Received {len(rows)} row(s)')

        return rows
