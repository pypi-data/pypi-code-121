from unittest import TestCase
from unittest.mock import Mock, patch

import click

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.fields import EXPECTED_ADD_BI_RESPONSE_FIELD
from montecarlodata.integrations.onboarding.self_hosted_credentials import SelfHostedCredentialOnboardingService
from montecarlodata.queries.onboarding import ADD_BI_CONNECTION_MUTATION, TEST_SELF_HOSTED_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class SelfHostedCredentialOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = SelfHostedCredentialOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(SelfHostedCredentialOnboardingService, 'onboard')
    def test_onboard_warehouse(self, onboard_mock):
        key = 'arn:aws:secretsmanager:us-east-1:test_account:secret:test-key'
        conn_type = 'snowflake'
        expected_options = {
            'connectionType': conn_type,
            'region': 'us-east-1',
            'warehouseType': 'snowflake',
            **_SAMPLE_BASE_OPTIONS
        }

        self._service.onboard_connection(conn_type, key, **_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_SELF_HOSTED_CRED_MUTATION,
            validation_response='testSelfHostedCredentials',
            connection_type=conn_type,
            self_hosting_key=key,
            **expected_options
        )

    @patch.object(SelfHostedCredentialOnboardingService, 'onboard')
    def test_onboard_lake(self, onboard_mock):
        key = 'arn:aws:secretsmanager:us-east-1:test_account:secret:test-key'
        conn_type = 'presto'
        expected_options = {'connectionType': conn_type, 'region': 'us-east-1', **_SAMPLE_BASE_OPTIONS}

        self._service.onboard_connection(conn_type, key, **_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_SELF_HOSTED_CRED_MUTATION,
            validation_response='testSelfHostedCredentials',
            connection_type=conn_type,
            self_hosting_key=key,
            **expected_options
        )

    @patch.object(SelfHostedCredentialOnboardingService, 'onboard')
    def test_onboard_bi(self, onboard_mock):
        key = 'arn:aws:secretsmanager:us-east-1:test_account:secret:test-key'
        conn_type = 'looker'
        expected_options = {'connectionType': conn_type, 'region': 'us-east-1', **_SAMPLE_BASE_OPTIONS}

        self._service.onboard_connection(conn_type, key, **_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_SELF_HOSTED_CRED_MUTATION,
            validation_response='testSelfHostedCredentials',
            connection_type=conn_type,
            connection_query=ADD_BI_CONNECTION_MUTATION,
            connection_response=EXPECTED_ADD_BI_RESPONSE_FIELD,
            self_hosting_key=key,
            **expected_options
        )

    def test_bad_arn(self):
        with self.assertRaises(click.Abort):
            self._service.onboard_connection('presto', 'invalid_arn')
