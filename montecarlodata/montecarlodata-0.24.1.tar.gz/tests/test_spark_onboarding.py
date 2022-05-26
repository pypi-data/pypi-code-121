from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.spark import SparkOnboardingService, \
    SPARK_BINARY_MODE_CONFIG_TYPE, SPARK_HTTP_MODE_CONFIG_TYPE, SPARK_DATABRICKS_CONFIG_TYPE
from montecarlodata.queries.onboarding import TEST_SPARK_BINARY_MODE_CRED_MUTATION, \
    TEST_SPARK_HTTP_MODE_CRED_MUTATION, TEST_SPARK_DATABRICKS_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class SparkOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = SparkOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(SparkOnboardingService, 'onboard')
    def test_spark_binary_mode_flow(self, onboard_mock):
        options = {'host': 'host', 'database': 'database', 'port': 10000, 'username': 'user', 'password': 'password'}

        self._service.onboard_spark(SPARK_BINARY_MODE_CONFIG_TYPE, **options, **_SAMPLE_BASE_OPTIONS)
        self._assert_onboard(TEST_SPARK_BINARY_MODE_CRED_MUTATION, options, onboard_mock)

    @patch.object(SparkOnboardingService, 'onboard')
    def test_spark_http_mode_flow(self, onboard_mock):
        options = {'url': 'url', 'username': 'user', 'password': 'password'}

        self._service.onboard_spark(SPARK_HTTP_MODE_CONFIG_TYPE, **options, **_SAMPLE_BASE_OPTIONS)
        self._assert_onboard(TEST_SPARK_HTTP_MODE_CRED_MUTATION, options, onboard_mock)

    @patch.object(SparkOnboardingService, 'onboard')
    def test_spark_databricks_flow(self, onboard_mock):
        options = {'workspace_url': 'workspace_url', 'workspace_id': 'workspace_id', 'cluster_id': 'cluster_id',
                   'token': 'token'}

        self._service.onboard_spark(SPARK_DATABRICKS_CONFIG_TYPE, **options, **_SAMPLE_BASE_OPTIONS)
        self._assert_onboard(TEST_SPARK_DATABRICKS_CRED_MUTATION, options, onboard_mock)

    @staticmethod
    def _assert_onboard(mutation, options, onboard_mock):
        expected_options = {**options, **_SAMPLE_BASE_OPTIONS, **{'connectionType': 'spark'}}

        onboard_mock.assert_called_once_with(
            validation_query=mutation,
            validation_response='testSparkCredentials',
            connection_type='spark',
            **expected_options
        )
