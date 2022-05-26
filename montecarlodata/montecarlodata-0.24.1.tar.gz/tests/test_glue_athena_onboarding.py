from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.glue_athena import GlueAthenaOnboardingService
from montecarlodata.queries.onboarding import TEST_GLUE_CRED_MUTATION, TEST_ATHENA_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class GlueAthenaOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = GlueAthenaOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(GlueAthenaOnboardingService, 'onboard')
    def test_glue_flow(self, onboard_mock):
        self._service.onboard_glue(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_GLUE_CRED_MUTATION,
            validation_response='testGlueCredentials',
            connection_type='glue',
            **_SAMPLE_BASE_OPTIONS
        )

    @patch.object(GlueAthenaOnboardingService, 'onboard')
    def test_athena_flow(self, onboard_mock):
        self._service.onboard_athena(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_ATHENA_CRED_MUTATION,
            validation_response='testAthenaCredentials',
            connection_type='athena',
            **_SAMPLE_BASE_OPTIONS
        )
