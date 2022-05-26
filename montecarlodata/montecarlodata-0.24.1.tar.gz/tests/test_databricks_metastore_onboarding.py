from unittest import TestCase
from unittest.mock import Mock, patch

from box import Box
from pycarlo.core import Client

from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.databricks_metastore import DatabricksMetastoreOnboardingService, \
    DEFAULT_GATEWAY_URL, DEFAULT_SECRET_NAME, DEFAULT_SECRET_SCOPE
from montecarlodata.queries.onboarding import TEST_DATABRICKS_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG


class DatabricksMetastoreOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._mc_client_mock = Mock(autospec=Client)
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = DatabricksMetastoreOnboardingService(
            _SAMPLE_CONFIG,
            mc_client=self._mc_client_mock,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(DatabricksMetastoreOnboardingService, 'onboard')
    def test_databricks_metastore_flow(self, onboard_mock):
        options = {
            'databricks_workspace_url': 'databricks_workspace_url',
            'databricks_workspace_id': 'databricks_workspace_id',
            'databricks_cluster_id': 'databricks_cluster_id',
            'databricks_token': 'databricks_token',
            'databricks_secret_key': DEFAULT_SECRET_NAME,
            'databricks_secret_scope': DEFAULT_SECRET_SCOPE
        }
        job_info = dict(
            databricks_job_id='databricks_job_id',
            databricks_job_name='databricks_job_name',
            databricks_notebook_path='databricks_notebook_path'
        )

        self._mc_client_mock.return_value = Box(dict(
            create_databricks_notebook_job=dict(
                databricks=dict(
                    workspace_job_id=job_info['databricks_job_id'],
                    workspace_job_name=job_info['databricks_job_name'],
                    workspace_notebook_path=job_info['databricks_notebook_path']
                )
            )
        ))

        self._service.onboard_databricks_metastore(**options, **_SAMPLE_BASE_OPTIONS)

        expected_options = {**options, **_SAMPLE_BASE_OPTIONS}
        expected_job_limits = {
            **job_info,
            'integration_gateway': {
                'gateway_url': DEFAULT_GATEWAY_URL,
                'databricks_secret_key': DEFAULT_SECRET_NAME,
                'databricks_secret_scope': DEFAULT_SECRET_SCOPE
            }
        }

        onboard_mock.assert_called_once_with(
            validation_query=TEST_DATABRICKS_CRED_MUTATION,
            validation_response='testDatabricksCredentials',
            connection_type='databricks-metastore',
            job_limits=expected_job_limits,
            **expected_options
        )
        self.assertEqual(self._mc_client_mock.call_count, 2)
