import hashlib
import json
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any
from uuid import uuid4

from dnastack.client.service_registry.models import ServiceType


class ConfigurationModelMixin:
    def get_content_hash(self):
        # noinspection PyUnresolvedReferences
        return ConfigurationModelMixin.hash(self.dict(exclude_none=True))

    @staticmethod
    def hash(content):
        raw_config = json.dumps(content, sort_keys=True)
        h = hashlib.new('sha256')
        h.update(raw_config.encode('utf-8'))
        return h.hexdigest()


class OAuth2Authentication(BaseModel, ConfigurationModelMixin):
    """OAuth2 Authentication Information"""
    authorization_endpoint: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    device_code_endpoint: Optional[str]
    grant_type: str
    personal_access_endpoint: Optional[str]
    personal_access_email: Optional[str]
    personal_access_token: Optional[str]
    redirect_url: Optional[str]
    resource_url: str
    scope: Optional[str]
    token_endpoint: Optional[str]
    type: str = 'oauth2'


class EndpointSource(BaseModel):
    source_id: str
    """ The ID of the source of the endpoint configuration 
    
        This references an service endpoint in the configuration (file). 
    """

    external_id: str
    """ This endpoint's identifier in the external source system """


class ServiceEndpoint(BaseModel, ConfigurationModelMixin):
    """API Service Endpoint"""
    model_version: float = 2.0
    """ Service Endpoint Configuration Specification Version """

    id: str = Field(default_factory=lambda: str(uuid4()))
    """ Local Unique ID"""

    adapter_type: Optional[str] = None
    """ Adapter type (only used with ClientManager)
    
        DO NOT USE THIS. This is replaced by "type" in model version 2.0.
    """

    authentication: Optional[Dict[str, Any]] = None
    """ (Primary) authentication information """

    fallback_authentications: Optional[List[Dict[str, Any]]] = None
    """ The list of fallback Authentication information
    
        This is in junction with GA4GH Service Information.
    """

    type: Optional[ServiceType]
    """ Service Type """

    url: str
    """ Base URL """

    mode: Optional[str]
    """ Client mode ("standard" or "explorer") - only applicable if the client supports.
    
        DO NOT USE THIS. This is replaced by "type" in model version 2.0.
    """

    source: Optional[EndpointSource]
    """ The source of the endpoint configuration (e.g., service registry) """

    def get_authentications(self) -> List[Dict[str, Any]]:
        """ Get the list of authentication information """
        raw_auths = []

        if self.authentication:
            raw_auths.append(self.authentication)
        if self.fallback_authentications:
            raw_auths.extend(self.fallback_authentications)

        return [self.__convert_to_dict(raw_auth) for raw_auth in raw_auths]

    def __convert_to_dict(self, model: Union[Dict[str, Any], BaseModel]) -> Dict[str, Any]:
        converted_model: Dict[str, Any] = dict()

        if isinstance(model, dict):
            converted_model.update(model)
        elif isinstance(model, BaseModel):
            converted_model.update(model.dict())
        else:
            raise NotImplementedError(f'No interpretation for {model}')

        # Short-term backward-compatibility until May 2022
        if 'oauth2' in converted_model:
            converted_model = converted_model['oauth2']
            converted_model['type'] = 'oauth2'

        return converted_model


class Configuration(BaseModel):
    """Configuration (v3)"""
    version: float = 3
    defaults: Dict[str, str] = dict()  # adapter-type-to-service-id
    endpoints: List[ServiceEndpoint] = list()
