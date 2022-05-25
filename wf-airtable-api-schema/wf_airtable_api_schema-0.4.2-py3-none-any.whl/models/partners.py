from typing import Optional, Union

from pydantic import BaseModel

from . import response as response_models

MODEL_TYPE = "partner"


class APIPartnerFields(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[str] = None
    active_stint: Optional[list[str]] = None
    roles: Optional[list[str]] = None


class APIPartnerRelationships(BaseModel):
    hubs_as_entrepreneur: Optional[response_models.APILinks] = None
    pods_as_contact: Optional[response_models.APILinks] = None
    schools_partner_guiding: Optional[response_models.APILinksAndData] = None
    educators_partner_guiding: Optional[response_models.APILinksAndData] = None


class APIPartnerData(response_models.APIData):
    fields: APIPartnerFields


class ListAPIPartnerData(BaseModel):
    __root__: list[APIPartnerData]


class APIPartnerResponse(response_models.APIResponse):
    data: APIPartnerData


class ListAPIPartnerResponse(response_models.ListAPIResponse):
    data: list[Union[APIPartnerData, dict]]
