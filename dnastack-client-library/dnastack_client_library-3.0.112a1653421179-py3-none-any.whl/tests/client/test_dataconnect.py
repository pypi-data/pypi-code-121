import os.path

import datetime
from decimal import Decimal
from typing import Callable, Any, Union
from unittest.mock import Mock

from dnastack import DataConnectClient
from dnastack.client.base_exceptions import UnauthenticatedApiAccessError, ApiError
from dnastack.client.data_connect import QueryLoader
from dnastack.configuration.models import ServiceEndpoint
from dnastack.common.environments import env
from dnastack.common.logger import get_logger
from ..exam_helper import initialize_test_endpoint, measure_runtime, ReversibleTestCase, DataConversionSample

_logger = get_logger(os.path.basename(__file__))


class TestUnit(ReversibleTestCase):
    def test_data_conversion_in_query_loader(self):
        samples = (
            # Number
            DataConversionSample.make('int', 12345, int),
            DataConversionSample.make('bigint', '12345678901234567890', int),
            DataConversionSample.make('decimal',
                                      '1234567890.1234567890',
                                      Decimal,
                                      [
                                          # Check the integer conversion
                                          lambda s: self.assertEqual(int(s), 1234567890),
                                          # Check the float conversion
                                          # NOTE: Python does truncate the fractional part when it is too long, e.g.,
                                          #       "1234567890.1234567890" is interpreted as "1234567890.1234567".
                                          lambda s: self.assertEqual(float(s), 1234567890.1234567),
                                          lambda s: self.assertEqual(str(float(s)), '1234567890.1234567'),
                                          # Check the string conversion
                                          lambda s: self.assertEqual(str(s), '1234567890.1234567890'),
                                      ]),
            DataConversionSample.make('real', 123.456, float),
            DataConversionSample.make('double', 7.445e-17, float),

            # Date
            DataConversionSample.date('2134-06-07',
                                      [
                                          lambda ts: self.assertEqual(ts.year, 2134),
                                          lambda ts: self.assertEqual(ts.month, 6),
                                          lambda ts: self.assertEqual(ts.day, 7),
                                      ]),

            # Time without time zone
            DataConversionSample.time('12:34:56',
                                      [lambda ts: self.assertEqual(ts.microsecond, 0)]),
            DataConversionSample.time('23:45:01.234',
                                      [lambda ts: self.assertEqual(ts.microsecond, 234000)]),
            DataConversionSample.time('23:45:01.234567',
                                      [lambda ts: self.assertEqual(ts.microsecond, 234567)]),

            # Time with time zone
            DataConversionSample.time_with_time_zone('12:34:56Z',
                                                     [self.__assert_utc_time_zone]),
            DataConversionSample.time_with_time_zone('12:34:56-01',
                                                     [self.__make_tzinfo_checker('UTC-01:00')]),
            DataConversionSample.time_with_time_zone('12:34:56+01',
                                                     [self.__make_tzinfo_checker('UTC+01:00')]),
            DataConversionSample.time_with_time_zone('12:34:56-02:34',
                                                     [self.__make_tzinfo_checker('UTC-02:34')]),
            DataConversionSample.time_with_time_zone('12:34:56+02:34',
                                                     [self.__make_tzinfo_checker('UTC+02:34')]),
            DataConversionSample.time_with_time_zone('23:45:01.234Z',
                                                     [self.__assert_utc_time_zone]),
            DataConversionSample.time_with_time_zone('23:45:01.234-01',
                                                     [self.__make_tzinfo_checker('UTC-01:00')]),
            DataConversionSample.time_with_time_zone('23:45:01.234+01',
                                                     [self.__make_tzinfo_checker('UTC+01:00')]),
            DataConversionSample.time_with_time_zone('23:45:01.234-02:34',
                                                     [self.__make_tzinfo_checker('UTC-02:34')]),
            DataConversionSample.time_with_time_zone('23:45:01.234+02:34',
                                                     [self.__make_tzinfo_checker('UTC+02:34')]),
            DataConversionSample.time_with_time_zone('23:45:01.234567Z',
                                                     [self.__assert_utc_time_zone]),
            DataConversionSample.time_with_time_zone('23:45:01.234567-01',
                                                     [self.__make_tzinfo_checker('UTC-01:00')]),
            DataConversionSample.time_with_time_zone('23:45:01.234567+01',
                                                     [self.__make_tzinfo_checker('UTC+01:00')]),
            DataConversionSample.time_with_time_zone('23:45:01.234567-02:34',
                                                     [self.__make_tzinfo_checker('UTC-02:34')]),
            DataConversionSample.time_with_time_zone('23:45:01.234567+02:34',
                                                     [self.__make_tzinfo_checker('UTC+02:34')]),

            # Timestamp without time zone
            # NOTE: The samples are mixed with both "<date>T<time><tz>" and "<date> <time><tz>" of ISO 8601.
            DataConversionSample.timestamp('2345-06-07 12:34:56',
                                           [lambda ts: self.assertEqual(ts.time().microsecond, 0)]),
            DataConversionSample.timestamp('2345-06-07T23:45:01.234',
                                           [lambda ts: self.assertEqual(ts.time().microsecond, 234000)]),
            DataConversionSample.timestamp('2345-06-07 23:45:01.234567',
                                           [lambda ts: self.assertEqual(ts.time().microsecond, 234567)]),

            # Timestamp with time zone
            # NOTE: The samples are mixed with both "<date>T<time><tz>" and "<date> <time><tz>" of ISO 8601.
            DataConversionSample.timestamp_with_time_zone('2345-06-07 12:34:56Z',
                                                          [lambda ts: self.assertEqual(ts.time().microsecond, 0),
                                                           self.__assert_utc_time_zone]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T12:34:56-01',
                                                          [self.__make_tzinfo_checker('UTC-01:00')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 12:34:56+01',
                                                          [self.__make_tzinfo_checker('UTC+01:00')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T12:34:56-02:34',
                                                          [self.__make_tzinfo_checker('UTC-02:34')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 12:34:56+02:34',
                                                          [self.__make_tzinfo_checker('UTC+02:34')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234Z',
                                                          [lambda ts: self.assertEqual(ts.time().microsecond, 234000),
                                                           self.__assert_utc_time_zone]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234-01',
                                                          [self.__make_tzinfo_checker('UTC-01:00')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234+01',
                                                          [self.__make_tzinfo_checker('UTC+01:00')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234-02:34',
                                                          [self.__make_tzinfo_checker('UTC-02:34')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234+02:34',
                                                          [self.__make_tzinfo_checker('UTC+02:34')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234567Z',
                                                          [lambda ts: self.assertEqual(ts.time().microsecond, 234567),
                                                           self.__assert_utc_time_zone]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234567-01',
                                                          [self.__make_tzinfo_checker('UTC-01:00')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234567+01',
                                                          [self.__make_tzinfo_checker('UTC+01:00')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234567-02:34',
                                                          [self.__make_tzinfo_checker('UTC-02:34')]),
            DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234567+02:34',
                                                          [self.__make_tzinfo_checker('UTC+02:34')]),

            # Interval day to second
            DataConversionSample.interval_day_to_second('P3DT4H3M2S'),
            DataConversionSample.interval_day_to_second('PT3M2S'),
            DataConversionSample.interval_day_to_second('PT4H3M'),

            # Interval year to month
            DataConversionSample.interval_year_to_month('P3Y2M'),
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data_model': {
                'properties': {
                    sample.id: sample.get_schema()
                    for sample in samples
                }
            },
            'data': [
                {
                    sample.id: sample.content
                    for sample in samples
                }
            ],
        }

        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        loader = QueryLoader(initial_url='http://localhost:12345/table/foo/data', http_session=mock_session)
        results = loader.load()
        first_result = results[0]

        for sample in samples:
            value = first_result[sample.id]
            self.assertIsInstance(
                value,
                sample.expected_type,
                f'The converted type of {sample.content} must be {sample.expected_type.__name__}, but given {type(value).__name__}.'
            )
            for check_expectation in sample.expectations:
                try:
                    check_expectation(value)
                except AssertionError:
                    raise RuntimeError(f'The data conversion for {value} fails an expectation.')

    def __make_tzinfo_checker(self, expected_string_representation: str) -> Callable[[Any], None]:
        def checker(ts: Union[datetime.date, datetime.datetime, datetime.time]):
            self.assertIsNotNone(ts.tzinfo, 'Missing time zone information')
            self.assertEqual(str(ts.tzinfo), expected_string_representation, 'Parsed as a different time zone')

        return checker

    def __assert_utc_time_zone(self, ts: Union[datetime.date, datetime.datetime, datetime.time]):
        self.assertEqual(ts.tzinfo, datetime.timezone.utc, 'Not in UTC')


class TestEndToEnd(ReversibleTestCase):
    """ End-to-end test for a client to Data Connect Service """

    # Test-specified
    endpoint = initialize_test_endpoint(env('E2E_PROTECTED_DATA_CONNECT_URL',
                                            default='https://collection-service.viral.ai/data-connect/'),
                                        type=DataConnectClient.get_default_service_type())

    def test_unauthenticated_client_accessing_protected_service_receives_http_401(self):
        client = DataConnectClient.make(ServiceEndpoint(id='abc', adapter_type='data_connect', url='https://data-connect-trino.viral.ai/'))

        with self.assertRaises(UnauthenticatedApiAccessError):
            __ = self._query(client, 'SELECT 1')

    def test_auth_client_performs_random_valid_queries(self):
        client = DataConnectClient.make(self.endpoint)

        # language=sql
        rows = self._query(client, 'SELECT 1')

        self.assertEqual(len(rows), 1)

    def test_auth_client_interacts_with_data_connect_service(self):
        client = DataConnectClient.make(self.endpoint)

        # Drain the whole list to ensure that the iterator can drain the result.
        with measure_runtime('List tables'):
            tables = client.list_tables()

        # Assume that the test environment has at least one tables.
        self.assertGreaterEqual(len(tables), 1)

        first_listed_table = tables[0]

        table = client.table(first_listed_table)
        table_info = table.info

        self.assertEqual(
            table_info,
            client.get_table(first_listed_table.name),
            'The metadata from the soon-to-be-deprecated method should be the same as the intended one.'
        )

        self.assertEqual(table_info.name, first_listed_table.name)
        self.assertTrue('properties' in table_info.data_model)

        # Get the first hundred rows.
        data_rows = []
        for row in table.data:
            if len(data_rows) >= 100:
                break
            data_rows.append(row)
        self.assertGreater(len(data_rows), 0, f'The table, called "{table.name}", is unexpectedly empty.')

        # Run a query from the first table
        with measure_runtime('Query the first 10 items'):
            # language=sql
            rows = self._query(client, f'SELECT * FROM {table_info.name} LIMIT 10')

        self.assertGreaterEqual(len(rows), 1, 'Should have at least one row')

        # Handle invalid columns
        with self.assertRaisesRegex(ApiError, r'(C|c)olumn'):
            # language=sql
            __ = self._query(client, f'SELECT panda FROM {table_info.name} LIMIT 10')

        # Handle unknown catalog/schema/table
        with self.assertRaisesRegex(ApiError, r'(S|s)chema'):
            # language=sql
            __ = self._query(client, f'SELECT * FROM foo LIMIT 10')

    def test_181962131_handle_map_column(self):
        client = DataConnectClient.make(self.endpoint)

        # First, run the test with the original query. Please note that the value part of the map is returned as string
        # by the data connect service.

        first_row = self._query(
            client,
            # language=sql
            """
            SELECT map(
                array ['HP:0012780', 'HP:0410331', 'HP:0001000'], 
                array [1.0, -1.0, 1.0]
            ) AS original_terms
            """
        )[0]

        self.assertIn('original_terms', first_row)

        original_terms = first_row['original_terms']

        self.assertEqual(original_terms['HP:0012780'], '1.0')
        self.assertEqual(original_terms['HP:0410331'], '-1.0')
        self.assertEqual(original_terms['HP:0001000'], '1.0')

        # Then, run the identical query but with casting.

        first_row = self._query(
            client,
            # language=sql
            """
            SELECT map(
                array ['HP:0012780', 'HP:0410331', 'HP:0001000'], 
                array [CAST(1.0 AS DOUBLE), CAST(-1.0 AS DOUBLE), CAST(1.0 AS DOUBLE)]
            ) AS original_terms
            """
        )[0]

        self.assertIn('original_terms', first_row)

        original_terms = first_row['original_terms']

        self.assertEqual(original_terms['HP:0012780'], 1.0)
        self.assertEqual(original_terms['HP:0410331'], -1.0)
        self.assertEqual(original_terms['HP:0001000'], 1.0)

    @staticmethod
    def _query(client: DataConnectClient, query: str):
        return [row for row in client.query(query)]
