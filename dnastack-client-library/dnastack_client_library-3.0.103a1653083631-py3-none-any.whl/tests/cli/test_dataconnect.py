from typing import Any, Dict, List

from dnastack.common.environments import env
from .base import CliTestCase
from ..exam_helper import client_id, client_secret, token_endpoint


class TestDataConnectCommand(CliTestCase):
    test_resource_url = env('E2E_PROTECTED_DATA_CONNECT_URL', default='https://collection-service.viral.ai/data-connect/')

    def setUp(self) -> None:
        super().setUp()
        self._configure({
            'data_connect.authentication.client_id': client_id,
            'data_connect.authentication.client_secret': client_secret,
            'data_connect.authentication.grant_type': 'client_credentials',
            'data_connect.authentication.resource_url': self.test_resource_url,
            'data_connect.authentication.token_endpoint': token_endpoint,
            'data_connect.url': self.test_resource_url,
        })

    def test_query_and_get_json(self):
        result = self.invoke('dataconnect', 'query', 'SELECT 1 AS x, 2 AS y')
        self.assertEqual(0, result.exit_code)
        rows = self.parse_json(result.output)
        self.assertEqual(1, len(rows))
        self.assertEqual(1, rows[0]['x'])
        self.assertEqual(2, rows[0]['y'])

    def test_query_and_get_csv(self):
        result = self.invoke('dataconnect', 'query', 'SELECT 1 AS x, 2 AS y', '-f', 'csv')
        self.assertEqual(0, result.exit_code)
        self.assertEqual('x,y\n1,2', result.output.strip())

    def test_full_functionalities(self):
        tables = self.simple_invoke('dataconnect', 'tables', 'list')
        self.__run_test_table_and_search_apis(tables)

    def test_data_conversion_side_effects_with_decimal_as_string(self):
        # language=sql
        sql = """
        SELECT
            CAST(12345 AS int) AS c_int,
            CAST(1234567890123456789 AS bigint) AS c_bigint,
            CAST(1234567890.1234567890 AS decimal(20, 10)) AS c_decimal,
            CAST(123.456 AS real) AS c_real,
            CAST(7.445e-17 AS double) AS c_double,
            CAST(NOW() AS date) AS c_date,
            CAST(NOW() AS timestamp) AS c_timstamp,
            CAST(NOW() AS time) AS c_time,
            CAST(NOW() AS timestamp with time zone) AS c_timstamptz,
            CAST(NOW() AS time with time zone) AS c_timetz,
            CAST(
                CAST(
                    ROW(123, 'abc', true)
                    AS ROW(v1 BIGINT, v2 VARCHAR, v3 BOOLEAN)
                )
                AS JSON
            ) AS c_json -- This is the sample JSON data.
        """

        column_expected_type_map = dict(
            c_int=int,
            c_bigint=int,
            c_decimal=str,
            c_real=float,
            c_double=float,
            c_date=str,
            c_timstamp=str,
            c_time=str,
            c_timstamptz=str,
            c_timetz=str,
            c_json=dict,
        )

        # With the default decimal mapping option.
        result = self.simple_invoke('dataconnect', 'query', sql)

        sample_row = result[0]
        for column_name, expected_type in column_expected_type_map.items():
            self.assertIsInstance(sample_row[column_name],
                                  expected_type,
                                  f'The value of {column_name} is not of type {expected_type.__name__}.')

        # With the "string" decimal mapping option.
        result = self.simple_invoke('dataconnect', 'query', '--decimal-as', 'string', sql)

        sample_row = result[0]
        for column_name, expected_type in column_expected_type_map.items():
            self.assertIsInstance(sample_row[column_name],
                                  expected_type,
                                  f'The value of {column_name} is not of type {expected_type.__name__}.')

    def test_data_conversion_side_effects_with_decimal_as_float(self):
        # language=sql
        sql = """
        SELECT
            CAST(12345 AS int) AS c_int,
            CAST(1234567890123456789 AS bigint) AS c_bigint,
            CAST(1234567890.1234567890 AS decimal(20, 10)) AS c_decimal,
            CAST(123.456 AS real) AS c_real,
            CAST(7.445e-17 AS double) AS c_double,
            CAST(NOW() AS date) AS c_date,
            CAST(NOW() AS timestamp) AS c_timstamp,
            CAST(NOW() AS time) AS c_time,
            CAST(NOW() AS timestamp with time zone) AS c_timstamptz,
            CAST(NOW() AS time with time zone) AS c_timetz,
            CAST(
                CAST(
                    ROW(123, 'abc', true)
                    AS ROW(v1 BIGINT, v2 VARCHAR, v3 BOOLEAN)
                )
                AS JSON
            ) AS c_json -- This is the sample JSON data.
        """

        column_expected_type_map = dict(
            c_int=int,
            c_bigint=int,
            c_decimal=float,
            c_real=float,
            c_double=float,
            c_date=str,
            c_timstamp=str,
            c_time=str,
            c_timstamptz=str,
            c_timetz=str,
            c_json=dict,
        )

        result = self.simple_invoke('dataconnect', 'query', '--decimal-as', 'float', sql)

        sample_row = result[0]
        for column_name, expected_type in column_expected_type_map.items():
            self.assertIsInstance(sample_row[column_name],
                                  expected_type,
                                  f'The value of {column_name} is not of type {expected_type.__name__}.')

    def __run_test_table_and_search_apis(self,
                                         tables: List[Dict[str, Any]],
                                         test_table_index=0,
                                         max_size=123,
                                         max_columns=5,
                                         try_next_if_table_empty=True):
        first_listed_table_info = tables[test_table_index]

        table_info = self.simple_invoke('dataconnect', 'tables', 'get', first_listed_table_info['name'])
        self.assertEqual(first_listed_table_info['name'], table_info['name'])
        table_columns = table_info['data_model']['properties']

        sample_table_name = table_info['name']
        sample_column_names = list(table_columns.keys())[:max_columns]
        sample_column_names_string = ', '.join(sample_column_names)

        rows = self.simple_invoke('dataconnect', 'query',
                                  f'SELECT {sample_column_names_string} FROM {sample_table_name} LIMIT {max_size}')

        if len(rows) == 0:
            self._logger.warning(f'T/{sample_table_name} has not enough data for testing.')

            if try_next_if_table_empty:
                if test_table_index >= len(tables):
                    self.fail('No tables with enough data for testing')
                else:
                    self._logger.info('Trying the next table...')
                    self.__run_test_table_and_search_apis(tables, test_table_index + 1, max_size, max_columns)

        self.assertGreaterEqual(max_size, len(rows), f'Expected upto {max_size} row(s)')

        selected_column_names = list(rows[0].keys())

        self.assertGreaterEqual(max_columns, len(selected_column_names), f'Expected upto {max_columns} column(s)')
        self.assertEqual(sorted(sample_column_names), sorted(selected_column_names),
                         f'Expected columns: {sample_column_names}')

    def test_get_unknown_table(self):
        with self.assertRaises(SystemExit):
            self.invoke('dataconnect', 'tables', 'get', 'foo_bar')
