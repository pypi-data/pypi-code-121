from typing import Optional, Union

from pydantic import BaseModel

from . import response as response_models
from .languages import CreateAPILanguagesFields
from .montessori_certifications import CreateAPIMontessoriCertificationsFields
from .utils import copy_field

MODEL_TYPE = "educator"


class CommonAPIEducatorFields(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[list[str]] = None
    details: Optional[str] = None
    home_address: Optional[str] = None
    target_community: Optional[str] = None
    stage: Optional[str] = None
    visioning_album_complete: Optional[bool] = False
    affiliation_agreement_url: Optional[str] = None
    current_roles: Optional[list[str]] = None
    race_and_ethnicity: Optional[list[str]] = None
    educational_attainment: Optional[str] = None
    income_background_as_child: Optional[str] = None
    household_income: Optional[str] = None
    gender: Optional[str] = None
    lgbtqia_identifying: Optional[bool] = False
    pronouns: Optional[str] = None
    discovery_newsletter: Optional[bool] = False
    etl_newsletter: Optional[bool] = False


class CreateAPIEducatorFields(CommonAPIEducatorFields):
    email: Optional[str] = None
    start_a_school_response_id: Optional[str] = None
    assigned_partner_id: Optional[str] = None
    target_community_id: Optional[str] = None
    montessori_certifications: Optional[list[CreateAPIMontessoriCertificationsFields]] = []
    languages: Optional[list[CreateAPILanguagesFields]] = []


class APIEducatorFields(CommonAPIEducatorFields):
    full_name: Optional[str] = None
    source: Optional[list[str]] = None
    source_other: Optional[str] = None
    montessori_certified: Optional[bool] = None
    race_and_ethnicity_other: Optional[str] = None
    gender_other: Optional[str] = None
    pronouns_other: Optional[str] = None


class APIEducatorMetaFields(BaseModel):
    __annotations__ = getattr(BaseModel, "__annotations__", {}).copy()
    copy_field(APIEducatorFields, "full_name", __annotations__)
    copy_field(CommonAPIEducatorFields, "first_name", __annotations__)
    copy_field(CommonAPIEducatorFields, "last_name", __annotations__)
    copy_field(CommonAPIEducatorFields, "email", __annotations__)


class APIEducatorRelationships(BaseModel):
    educators_schools: Optional[response_models.APILinksAndData] = None
    assigned_partner: Optional[response_models.APILinks] = None
    languages: Optional[response_models.APILinksAndData] = None
    montessori_certifications: Optional[response_models.APILinksAndData] = None
    hub: Optional[response_models.APILinksAndData] = None


class APIEducatorData(response_models.APIData):
    fields: APIEducatorFields


class ListAPIEducatorData(BaseModel):
    __root__: list[APIEducatorData]


class APIEducatorResponse(response_models.APIResponse):
    data: APIEducatorData


class ListAPIEducatorResponse(response_models.ListAPIResponse):
    data: list[Union[APIEducatorData, dict]]
