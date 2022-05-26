import base64
from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.warehouse.warehouses import WarehouseOnboardingService
from montecarlodata.queries.onboarding import TEST_DATABASE_CRED_MUTATION, TEST_SNOWFLAKE_CRED_MUTATION, \
    TEST_BQ_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class WarehouseOnBoardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = WarehouseOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(WarehouseOnboardingService, 'onboard')
    def test_redshift_flow(self, onboard_mock):
        expected_options = {**{'connectionType': 'redshift', 'warehouseType': 'redshift'}, **_SAMPLE_BASE_OPTIONS}

        self._service.onboard_redshift(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_DATABASE_CRED_MUTATION,
            validation_response='testDatabaseCredentials',
            connection_type='redshift',
            **expected_options
        )

    @patch.object(WarehouseOnboardingService, 'onboard')
    def test_snowflake_flow(self, onboard_mock):
        expected_options = {**{'warehouseType': 'snowflake'}, **_SAMPLE_BASE_OPTIONS}

        self._service.onboard_snowflake(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_SNOWFLAKE_CRED_MUTATION,
            validation_response='testSnowflakeCredentials',
            connection_type='snowflake',
            **expected_options
        )

    @patch.object(WarehouseOnboardingService, 'onboard')
    @patch('montecarlodata.integrations.onboarding.warehouse.warehouses.read_as_base64')
    def test_bq_flow(self, read_as_base64_mock, onboard_mock):
        file_path, service_json = 'foo', 'bar'
        base64_service_json = base64.b64encode(service_json.encode('utf-8'))

        input_options = {'ServiceFile': file_path, **_SAMPLE_BASE_OPTIONS}
        expected_options = {
            **{'warehouseType': 'bigquery', 'serviceJson': base64_service_json.decode()}, **_SAMPLE_BASE_OPTIONS}

        read_as_base64_mock.return_value = base64_service_json

        self._service.onboard_bq(**input_options)
        read_as_base64_mock.assert_called_once_with(file_path)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_BQ_CRED_MUTATION,
            validation_response='testBqCredentials',
            connection_type='bigquery',
            **expected_options
        )
