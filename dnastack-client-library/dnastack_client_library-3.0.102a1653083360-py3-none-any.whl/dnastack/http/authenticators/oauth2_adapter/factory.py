from typing import Optional

from imagination.decorator import service

from dnastack.configuration.models import OAuth2Authentication
from dnastack.http.authenticators.oauth2_adapter.abstract import OAuth2Adapter
from dnastack.http.authenticators.oauth2_adapter.client_credential import ClientCredentialAdapter
from dnastack.http.authenticators.oauth2_adapter.device_code_flow import DeviceCodeFlowAdapter
from dnastack.http.authenticators.oauth2_adapter.personal_access_token import PersonalAccessTokenAdapter


@service.registered()
class OAuth2AdapterFactory:
    # NOTE: It was ordered this way to accommodate the general intended authentication flow.
    __supported_auth_adapter_classes = [
        DeviceCodeFlowAdapter,
        ClientCredentialAdapter,
        PersonalAccessTokenAdapter,
    ]

    def get_from(self, auth_info: OAuth2Authentication) -> Optional[OAuth2Adapter]:
        for adapter_class in self.__supported_auth_adapter_classes:
            if adapter_class.is_compatible_with(auth_info):
                return adapter_class(auth_info)
        return None
