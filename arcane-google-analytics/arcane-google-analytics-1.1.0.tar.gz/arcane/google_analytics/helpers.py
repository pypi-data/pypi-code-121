from typing import Dict, Optional

from arcane.core import UserRightsEnum, RightsLevelEnum, BadRequestError, BaseAccount
from arcane.core.types import BaseAccount
from arcane.requests import call_get_route


def get_google_analytics_account(
    base_account: BaseAccount,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_credentials_path: Optional[str] = None,
    auth_enabled: bool = True
) -> Dict:
    if not clients_service_url or not firebase_api_key or not gcp_credentials_path:
        raise BadRequestError('clients_service_url or firebase_api_key or  gcp_credentials_path should not be None')
    url = f"{clients_service_url}/api/google-analytics-account?account_id={base_account['id']}&client_id={base_account['client_id']}"
    accounts = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights':{UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=gcp_credentials_path
    )
    if len(accounts) == 0:
        raise BadRequestError(f'Error while getting google analytics account with: {base_account}. No account corresponding.')
    elif len(accounts) > 1:
        raise BadRequestError(f'Error while getting google analytics account with: {base_account}. Several account corresponding: {accounts}')

    return accounts[0]
