from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, HttpUrl

from . import response as response_models
from .utils import copy_field

MODEL_TYPE = "school"


class APISchoolFields(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    details: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    domain_name: Optional[str] = None
    address: Optional[str] = None
    hub_name: Optional[str] = None
    pod_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    ages_served: Optional[list[str]] = []
    school_calendar: Optional[str] = None
    school_schedule: Optional[list[str]] = []
    school_phone: Optional[str] = None
    school_email: Optional[str] = None
    website: Optional[HttpUrl] = None

    status: Optional[str] = None
    ssj_stage: Optional[str] = None
    began_ssj_at: Optional[date] = None
    entered_planning_at: Optional[date] = None
    entered_startup_at: Optional[date] = None
    opened_at: Optional[date] = None
    projected_open: Optional[date] = None
    affiliation_status: Optional[str] = None
    affiliated_at: Optional[date] = None
    affiliation_agreement_url: Optional[HttpUrl] = None
    nonprofit_status: Optional[str] = None
    left_network_reason: Optional[str] = None
    left_network_date: Optional[date] = None
    organizational_unit: Optional[str] = None


class APISchoolMetaFields(BaseModel):
    __annotations__ = getattr(BaseModel, "__annotations__", {}).copy()
    copy_field(APISchoolFields, "name", __annotations__)
    copy_field(APISchoolFields, "hub_name", __annotations__)
    copy_field(APISchoolFields, "pod_name", __annotations__)
    copy_field(APISchoolFields, "domain_name", __annotations__)
    copy_field(APISchoolFields, "status", __annotations__)
    copy_field(APISchoolFields, "ssj_stage", __annotations__)


class APISchoolRelationships(BaseModel):
    hub: Optional[response_models.APILinksAndData] = None
    pod: Optional[response_models.APILinksAndData] = None
    guides_and_entrepreneurs: Optional[response_models.APILinksAndData] = None
    educators: Optional[response_models.APILinksAndData] = None
    current_educators: Optional[response_models.APILinksAndData] = None
    primary_contacts: Optional[response_models.APILinksAndData] = None


class APISchoolData(response_models.APIData):
    fields: APISchoolFields


class ListAPISchoolData(BaseModel):
    __root__: list[APISchoolData]


class APISchoolResponse(response_models.APIResponse):
    data: APISchoolData


class ListAPISchoolResponse(response_models.ListAPIResponse):
    data: list[Union[APISchoolData, dict]]
