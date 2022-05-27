from typing import Any, Literal

from pydantic import BaseModel

from fastel.config import SdkConfig
from fastel.utils import requests


class MapRequestModel(BaseModel):
    logistics_subtype: Literal[
        "FAMI",
        "UNIMART",
        "HILIFE",
        "FAMIC2C",
        "UNIMARTC2C",
        "HILIFEC2C",
        "OKMARTC2C",
        "TCAT",
        "ECAN",
    ]
    redirect_url: str


def map_request(logistics_subtype: str, redirect_url: str) -> Any:
    data = {
        "LogisticsType": "CVS",
        "LogisticsSubType": logistics_subtype,
        "IsCollection": "N",
        "Device": 0,
    }
    if redirect_url:
        data["redirect_url"] = redirect_url

    url = f"{SdkConfig.payment_host}/ecpay/logistics/map/request?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}"
    result = requests.post(url, json=data)
    return result.json()
