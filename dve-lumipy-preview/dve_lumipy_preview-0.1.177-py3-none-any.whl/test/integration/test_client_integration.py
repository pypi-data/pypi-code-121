import time

import pandas as pd

from test.integration.base_intergration_test import BaseIntegrationTest


class TestWebClient(BaseIntegrationTest):

    def test_field_table_catelog(self):
        df = self.client.table_field_catalog()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(df.shape[0], 0)

    def test_synchronous_query(self):
        sql_str = "select * from Sys.Field limit 100"
        df = self.client.query_and_fetch(sql_str)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 100)

    def test_asynchronous_query(self):
        sql_str = "select * from Sys.Field limit 100"
        ex_id = self.client.start_query(sql_str)
        self.assertIsInstance(ex_id, str)
        self.assertGreater(len(ex_id), 0)

        status = self.client.get_status(ex_id)
        while not status['status'] == 'RanToCompletion':
            status = self.client.get_status(ex_id)
            time.sleep(1)

        df = self.client.get_result(ex_id)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 100)
