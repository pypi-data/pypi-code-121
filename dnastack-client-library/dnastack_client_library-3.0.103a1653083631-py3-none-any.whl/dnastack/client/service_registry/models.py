from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ServiceType(BaseModel):
    """
    GA4GH Service Type

    https://raw.githubusercontent.com/ga4gh-discovery/ga4gh-service-info/v1.0.0/service-info.yaml#/components/schemas/ServiceType
    """
    group: str
    artifact: str
    version: str

    def __repr__(self):
        return f'{self.group}:{self.artifact}:{self.version}'


class Organization(BaseModel):
    """ Organization """
    name: str
    url: str


class Service(BaseModel):
    """
    GA4GH Service

    * https://github.com/ga4gh-discovery/ga4gh-service-registry/blob/develop/service-registry.yaml#/components/schemas/ExternalService
    * https://raw.githubusercontent.com/ga4gh-discovery/ga4gh-service-info/v1.0.0/service-info.yaml#/components/schemas/Service
    """
    id: str
    name: str
    type: ServiceType
    url: str
    description: Optional[str]
    organization: Organization
    contactUrl: Optional[str]
    documentationUrl: Optional[str]
    createdAt: Optional[str]
    updatedAt: Optional[str]
    environment: Optional[str]
    version: str

    authentication: Optional[List[Dict[str, Any]]] = None
    """
    Authentication Information
    
    .. note:: This is a non-standard property. Only available via DNAstack's GA4GH Service Registry.
    """