import os
from typing import Optional

from pycarlo.core import Client, Mutation

from montecarlodata.config import Config
from montecarlodata.errors import manage_errors
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import DATABRICKS_METASTORE_CONNECTION_TYPE, \
    EXPECTED_DATABRICKS_GQL_RESPONSE_FIELD
from montecarlodata.queries.onboarding import TEST_DATABRICKS_CRED_MUTATION

DEFAULT_GATEWAY_URL = os.getenv(
    'MC_INTEGRATION_GATEWAY_URL',
    'https://integrations.getmontecarlo.com/databricks/metadata'
)
# Secret scope and name defined in the data collector:
# https://github.com/monte-carlo-data/data-collector/blob/e5db61eacd10e0388acd9ff8a32fe60644b36797/lambdas/api_lambdas/execute_databricks_actions.py#L61  # noqa
DEFAULT_SECRET_SCOPE = 'monte-carlo-collector-gateway-scope'
DEFAULT_SECRET_NAME = 'monte-carlo-collector-gateway-secret'


class DatabricksMetastoreOnboardingService(BaseOnboardingService):

    _DATABRICKS_CONFIG_KEYS = [
        'databricks_workspace_url', 'databricks_workspace_id', 'databricks_cluster_id', 'databricks_token'
    ]

    def __init__(self, config: Config, mc_client: Optional[Client] = None, **kwargs):
        super().__init__(config, **kwargs)
        self._mc_client = mc_client or Client()

    @manage_errors
    def onboard_databricks_metastore(self, **kwargs) -> None:
        """
        Onboard a databricks metastore connection
        """
        databricks_config = {key: kwargs[key] for key in self._DATABRICKS_CONFIG_KEYS}

        # Create secret
        if not kwargs.get('skip_secret_creation', False):
            mutation = Mutation()
            mutation.create_databricks_secret(
                databricks_config=databricks_config,
                secret_name=kwargs['databricks_secret_key'],
                scope_name=kwargs['databricks_secret_scope']
            )
            self._mc_client(mutation)

        # Create notebook
        if not kwargs.get('skip_notebook_creation', False):
            mutation = Mutation()
            mutation.create_databricks_notebook_job(databricks_config=databricks_config)
            resp = self._mc_client(mutation).create_databricks_notebook_job.databricks
            job_info = dict(
                databricks_job_id=resp.workspace_job_id,
                databricks_job_name=resp.workspace_job_name,
                databricks_notebook_path=resp.workspace_notebook_path
            )
        else:
            job_info = dict(
                databricks_job_id=kwargs.pop('databricks_job_id'),
                databricks_job_name=kwargs.pop('databricks_job_name'),
                databricks_notebook_path=kwargs.pop('databricks_notebook_path')
            )
        job_limits = {
            **dict(
                integration_gateway=dict(
                    gateway_url=DEFAULT_GATEWAY_URL,
                    databricks_secret_key=kwargs['databricks_secret_key'],
                    databricks_secret_scope=kwargs['databricks_secret_scope']
                )
            ),
            **job_info
        }

        # Onboard
        self.onboard(validation_query=TEST_DATABRICKS_CRED_MUTATION,
                     validation_response=EXPECTED_DATABRICKS_GQL_RESPONSE_FIELD,
                     connection_type=DATABRICKS_METASTORE_CONNECTION_TYPE,
                     job_limits=job_limits,
                     **kwargs)
