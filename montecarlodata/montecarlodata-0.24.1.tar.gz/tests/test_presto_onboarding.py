from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.presto import PrestoOnboardingService
from montecarlodata.queries.onboarding import TEST_PRESTO_CRED_MUTATION, TEST_S3_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class PrestoOnBoardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = PrestoOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(PrestoOnboardingService, 'onboard')
    def test_presto_sql_flow(self, onboard_mock):
        s3_key = 'testing/test'
        expected_options = {
            'ssl_options': {'mechanism': 'dc-s3', 'cert': 'testing/test', 'skip_verification': False},
            **_SAMPLE_BASE_OPTIONS
        }

        self._service.onboard_presto_sql(**{'cert_s3': s3_key, 'skip_cert_verification': False, **_SAMPLE_BASE_OPTIONS})
        onboard_mock.assert_called_once_with(
            validation_query=TEST_PRESTO_CRED_MUTATION,
            validation_response='testPrestoCredentials',
            connection_type='presto',
            **expected_options
        )

    @patch.object(PrestoOnboardingService, 'onboard')
    def test_presto_s3_flow(self, onboard_mock):
        expected_options = {**_SAMPLE_BASE_OPTIONS, **{'connectionType': 'presto-s3'}}

        self._service.onboard_presto_s3(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_S3_CRED_MUTATION,
            validation_response='testS3Credentials',
            connection_type='presto-s3',
            job_types=['query_logs'],
            **expected_options
        )
