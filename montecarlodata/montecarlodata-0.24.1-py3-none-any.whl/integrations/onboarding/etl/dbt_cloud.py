from typing import Dict

from montecarlodata.common.data import OnboardingConfiguration
from montecarlodata.config import Config
from montecarlodata.errors import manage_errors, complain_and_abort
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import EXPECTED_DBT_CLOUD_RESPONSE_FIELD, \
    EXPECTED_ADD_CONNECTION_RESPONSE_FIELD, DBT_CLOUD_CONNECTION_TYPE
from montecarlodata.queries.onboarding import TEST_DBT_CLOUD_CRED_MUTATION, ADD_CONNECTION_MUTATION


class DbtCloudOnboardingService(BaseOnboardingService):
    def __init__(self, config: Config, **kwargs):
        super().__init__(config, **kwargs)

    @manage_errors
    def onboard_dbt_cloud(self, **kwargs) -> None:
        self.onboard(validation_query=TEST_DBT_CLOUD_CRED_MUTATION,
                     validation_response=EXPECTED_DBT_CLOUD_RESPONSE_FIELD,
                     connection_query=ADD_CONNECTION_MUTATION,
                     connection_response=EXPECTED_ADD_CONNECTION_RESPONSE_FIELD,
                     connection_type=DBT_CLOUD_CONNECTION_TYPE, **kwargs)

    def _disambiguate_warehouses(self, warehouse_type: str, onboarding_config: OnboardingConfiguration) -> Dict:
        """
        Determine which warehouse to associate with dbt cloud connection
        """
        if not self._user_service.warehouses:
            complain_and_abort('You must have at least one warehouse connection configured.')

        if onboarding_config.connection_id:
            # Return ID of warehouse containing the matching connection_id
            for warehouse in self._user_service.warehouses:
                for connection in warehouse['connections']:
                    if connection['uuid'] == onboarding_config.connection_id:
                        return {'dwId': warehouse['uuid']}
            complain_and_abort(f"Could not find connection ID = {onboarding_config.connection_id}"
                               "Hint: Use 'montecarlo integrations list' to find a connection ID of the desired warehouse")

        # If there is only a single warehouse
        if len(self._user_service.warehouses) == 1:
            return {'dwId': self._user_service.warehouses[0]['uuid']}

        complain_and_abort("Multiple warehouses detected. You must choose a warehouse connection using --connection-id")