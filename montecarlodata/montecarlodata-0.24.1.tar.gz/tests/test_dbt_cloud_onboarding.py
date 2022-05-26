from unittest import TestCase
from unittest.mock import Mock, patch

from click import Abort

from montecarlodata.common.data import OnboardingConfiguration, ValidationResult
from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.etl.dbt_cloud import DbtCloudOnboardingService
from montecarlodata.integrations.onboarding.fields import DBT_CLOUD_CONNECTION_TYPE, EXPECTED_DBT_CLOUD_RESPONSE_FIELD, \
    EXPECTED_ADD_CONNECTION_RESPONSE_FIELD
from montecarlodata.queries.onboarding import TEST_DBT_CLOUD_CRED_MUTATION, ADD_CONNECTION_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_common_user import _SAMPLE_CONFIG

_SAMPLE_WAREHOUSE = {
    'uuid': 'my-snowflake-warehouse-uuid',
    'name': 'snowflake',
    'connectionType': 'SNOWFLAKE',
    'connections': [
        {
            'uuid': 'my-snowflake-connection-uuid',
            'type': 'SNOWFLAKE',
            'createdOn': '2020-03-28T23:51:04.775647+00:00',
            'jobTypes': ['metadata', 'query_logs', 'sql_query', 'json_schema'],
            'connectionIdentifier': {
                'key': 'account',
                'value': 'hda34492.us-east-1'
            }
        }]
}


class DbtCloudOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = DbtCloudOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )
        self._service._disable_handle_errors = True

    @patch.object(DbtCloudOnboardingService, '_validate_connection')
    @patch('montecarlodata.integrations.onboarding.base.prompt_connection')
    def test_onboard_dbt_cloud(self, prompt_mock, validation_mock):
        self._user_service_mock.warehouses = [
            _SAMPLE_WAREHOUSE
        ]
        validation_mock.return_value = ValidationResult(has_warnings=False, credentials_key='path')

        self._service.onboard_dbt_cloud()

        validation_mock.assert_called_once_with(
            query=TEST_DBT_CLOUD_CRED_MUTATION,
            response_field=EXPECTED_DBT_CLOUD_RESPONSE_FIELD
        )

        self._request_wrapper_mock.make_request_v2.assert_called_with(
            operation=EXPECTED_ADD_CONNECTION_RESPONSE_FIELD,
            query=ADD_CONNECTION_MUTATION,
            variables={
                'key': 'path',
                'connectionType': 'dbt-cloud',
                'dwId': 'my-snowflake-warehouse-uuid'  # check that dwId is passed as a parameter
            })

    def test_disambiguate(self):
        self._user_service_mock.warehouses = [
            _SAMPLE_WAREHOUSE
        ]

        config = OnboardingConfiguration(connection_type=DBT_CLOUD_CONNECTION_TYPE)
        self.assertEqual(self._service._disambiguate_warehouses('foo', config), {
            'dwId': 'my-snowflake-warehouse-uuid'
        })

    def test_disambiguate_multiple_warehouses(self):
        self._user_service_mock.warehouses = [
            {
                'uuid': 'my-datalake-warehouse-uuid',
                'name': 'data-lake',
                'connectionType': 'DATA_LAKE',
                'connections': []
            },
            _SAMPLE_WAREHOUSE
        ]

        # Multiple warehouses, should abort
        config = OnboardingConfiguration(connection_type=DBT_CLOUD_CONNECTION_TYPE)
        with self.assertRaises(Abort):
            self._service._disambiguate_warehouses('foo', config)

        # Multiple warehouses, with connection-id specified, should succeed
        config = OnboardingConfiguration(connection_type=DBT_CLOUD_CONNECTION_TYPE,
                                         connection_id='my-snowflake-connection-uuid')
        self.assertEqual(self._service._disambiguate_warehouses('foo', config), {
            'dwId': 'my-snowflake-warehouse-uuid'
        })

        # Multiple warehouses, with connection-id specified, unknown connection_id
        config = OnboardingConfiguration(connection_type=DBT_CLOUD_CONNECTION_TYPE,
                                         connection_id='blah')
        with self.assertRaises(Abort):
            self._service._disambiguate_warehouses('foo', config)