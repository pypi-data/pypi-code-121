from typing import Optional, Union

from pydantic import BaseModel

from . import response as response_models

MODEL_TYPE = "area_contact"


class APIGeoAreaContactFields(BaseModel):
    area_name: Optional[str] = None
    area_type: Optional[str] = None
    city_radius: Optional[int] = 20
    polygon_coordinates: Optional[str] = None
    first_contact_email: Optional[str] = None
    assigned_rse_name: Optional[str] = None
    hub_name: Optional[str] = None
    sendgrid_template_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geocode: Optional[dict] = None


class APIGeoAreaContactRelationships(BaseModel):
    hub: Optional[response_models.APILinksAndData] = None
    assigned_rse: Optional[response_models.APILinksAndData] = None


class APIGeoAreaContactData(response_models.APIData):
    fields: APIGeoAreaContactFields


class ListAPIGeoAreaContactData(BaseModel):
    __root__: list[APIGeoAreaContactData]


class APIGeoAreaContactResponse(response_models.APIResponse):
    data: APIGeoAreaContactData


class ListAPIGeoAreaContactResponse(response_models.ListAPIResponse):
    data: list[Union[APIGeoAreaContactData, dict]]
