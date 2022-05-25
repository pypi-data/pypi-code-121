from typing import Optional, Union

from pydantic import BaseModel

from . import response as response_models

MODEL_TYPE = "area_target_community"


class APIGeoAreaTargetCommunityFields(BaseModel):
    area_name: Optional[str] = None
    area_type: Optional[str] = None
    city_radius: Optional[int] = 20
    polygon_coordinates: Optional[str] = None
    target_community_name: Optional[str] = None
    hub_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geocode: Optional[dict] = None


class APIGeoAreaTargetCommunityRelationships(BaseModel):
    hub: Optional[response_models.APILinksAndData] = None
    target_community: Optional[response_models.APILinksAndData] = None


class APIGeoAreaTargetCommunityData(response_models.APIData):
    fields: APIGeoAreaTargetCommunityFields


class ListAPIGeoAreaTargetCommunityData(BaseModel):
    __root__: list[APIGeoAreaTargetCommunityData]


class APIGeoAreaTargetCommunityResponse(response_models.APIResponse):
    data: APIGeoAreaTargetCommunityData


class ListAPIGeoAreaTargetCommunityResponse(response_models.ListAPIResponse):
    data: list[Union[APIGeoAreaTargetCommunityData, dict]]
