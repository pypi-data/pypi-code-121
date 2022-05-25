from typing import Optional, Union

from pydantic import BaseModel

from . import response as response_models

MODEL_TYPE = "pod"


class APIPodFields(BaseModel):
    name: Optional[str] = None


class APIPodRelationships(BaseModel):
    hub: Optional[response_models.APILinksAndData] = None
    pod_contacts: Optional[response_models.APILinksAndData] = None
    schools: Optional[response_models.APILinksAndData] = None


class APIPodData(response_models.APIData):
    fields: APIPodFields


class ListAPIPodData(BaseModel):
    __root__: list[APIPodData]


class APIPodResponse(response_models.APIResponse):
    data: APIPodData


class ListAPIPodResponse(response_models.ListAPIResponse):
    data: list[Union[APIPodData, dict]]
