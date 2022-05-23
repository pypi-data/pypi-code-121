import time

import lumipy as lm
from test.integration.base_intergration_test import BaseIntegrationTest


class TestLusidQueries(BaseIntegrationTest):

    """Integration tests for client use cases.

    """

    def test_create_query_delete_view(self):

        test_provider_name = "Lumipy.Test"

        sys_connection = self.atlas.sys_connection()

        # Create view and verify returns rows
        query = sys_connection.select('*')
        df = query.setup_view(test_provider_name).go()
        self.assertEqual(df.shape[0], 9)

        # Check view has accessible provider in atlas
        time.sleep(5)
        atlas = lm.get_atlas()
        results = atlas.search_providers(test_provider_name).list_providers()
        self.assertEqual(len(results), 1)

        # Check view provider can be queried
        test_provider = results[0]()
        df = test_provider.select('*').go()
        self.assertEqual(df.shape[0], 9)

        # Delete view provider and verify removed from atlas
        df = self.client.delete_view(test_provider_name)
        self.assertEqual(df.shape[0], 1)
        time.sleep(5)
        atlas = lm.get_atlas()
        self.assertRaises(ValueError, lambda n: atlas.search_providers(n), test_provider_name)