from typing import Any, Dict, Optional

from dnastack.client.service_registry.models import Service
from dnastack.configuration.models import ServiceEndpoint


def parse_ga4gh_service_info(service: Service, alternate_service_id: Optional[str] = None) -> ServiceEndpoint:
    authentications = [
        _parse_authentication_info(auth_info)
        for auth_info in (service.authentication or list())
    ]

    return ServiceEndpoint(
        model_version=2.0,
        id=alternate_service_id or service.id,
        fallback_authentications=authentications,
        type=service.type,
        url=service.url,
    )


def _parse_authentication_info(auth_info: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        type='oauth2',
        authorization_endpoint=auth_info.get('authorizationUrl'),
        client_id=auth_info.get('clientId'),
        client_secret=auth_info.get('clientSecret'),
        device_code_endpoint=auth_info.get('deviceCodeUrl'),
        grant_type=auth_info.get('grantType'),
        redirect_url=auth_info.get('redirectUrl'),
        resource_url=auth_info.get('resource'),
        scope=auth_info.get('scope'),
        token_endpoint=auth_info.get('accessTokenUrl'),
    )
