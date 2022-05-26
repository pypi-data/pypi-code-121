from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.hive import HiveOnboardingService
from montecarlodata.integrations.onboarding.fields import AWS_RDS_CA_CERT
from montecarlodata.queries.onboarding import TEST_DATABASE_CRED_MUTATION, \
    TEST_S3_CRED_MUTATION, TEST_HIVE_SQL_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class HiveOnboardingTest(TestCase):
    _DEFAULT_JOB_LIMITS = {'get_partition_locations': True, 'max_partition_locations': 50}

    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = HiveOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    def test_hive_mysql_flow_without_a_catalog(self):
        sample_input = {'use_ssl': True, 'catalog': None, **_SAMPLE_BASE_OPTIONS}
        self._test_hive_mysql_flow(sample_input=sample_input, job_limits=self._DEFAULT_JOB_LIMITS)

    def test_hive_mysql_flow_with_a_catalog(self):
        sample_input = {'use_ssl': True, 'catalog': 'foo', **_SAMPLE_BASE_OPTIONS}
        self._test_hive_mysql_flow(sample_input=sample_input, job_limits={'catalog_name': 'foo', **self._DEFAULT_JOB_LIMITS})

    @patch.object(HiveOnboardingService, 'onboard')
    def test_hive_s3_flow(self, onboard_mock):
        expected_options = {**_SAMPLE_BASE_OPTIONS, **{'connectionType': 'hive-s3'}}

        self._service.onboard_hive_s3(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_S3_CRED_MUTATION,
            validation_response='testS3Credentials',
            connection_type='hive-s3',
            job_types=['query_logs'],
            **expected_options
        )

    @patch.object(HiveOnboardingService, 'onboard')
    def test_hive_sql_flow(self, onboard_mock):
        self._service.onboard_hive_sql(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_HIVE_SQL_CRED_MUTATION,
            validation_response='testHiveCredentials',
            connection_type='hive',
            **_SAMPLE_BASE_OPTIONS
        )

    @patch.object(HiveOnboardingService, 'onboard')
    def _test_hive_mysql_flow(self, onboard_mock: Any, sample_input: Dict, job_limits: Optional[Dict] = None):
        expected_options = {'ssl_options': {'ca': AWS_RDS_CA_CERT}, 'connectionType': 'hive-mysql',
                            **_SAMPLE_BASE_OPTIONS}

        self._service.onboard_hive_mysql(**sample_input)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_DATABASE_CRED_MUTATION,
            validation_response='testDatabaseCredentials',
            connection_type='hive-mysql',
            job_limits=job_limits,
            **expected_options
        )
