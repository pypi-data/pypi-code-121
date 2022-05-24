"""
Pydantic models for custom Configs
"""
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field, validator

from mfire.utils.date import Datetime


class _ResourceHandlerConfig(BaseModel, ABC):
    """Abstract ResourceHandler for handling basic promethee resources"""

    # Section
    role: Optional[str]
    fatal: Optional[bool] = False
    now: Optional[bool] = True
    # Resource
    kind: str
    # Provider
    vapp: str
    vconf: str
    namespace: str
    experiment: str
    block: str
    # Container
    format: str
    local: str


class _DataResourceHandlerConfig(_ResourceHandlerConfig, ABC):
    """Abstract ResourceHandler specific for meteorological data"""

    # Resource
    model: str
    date: str
    nativefmt: str
    geometry: str
    cutoff: str
    origin: str

    @validator("date")
    def init_date(cls, date: str) -> Datetime:
        return Datetime(date)


class GridPointRHConfig(_DataResourceHandlerConfig):
    """ResourceHandler specific for GridPoint data (raw model in grib files)"""

    # Resource
    kind: str = Field("gridpoint", const=True)
    term: int


class PrometheeGridPointRHConfig(_DataResourceHandlerConfig):
    """ResourceHandler specific for GridPoint data (raw model in grib files)"""

    # Resource
    kind: str = Field("promethee_gridpoint", const=True)
    param: str
    begintime: int
    endtime: int
    step: int


class MaskRHConfig(_ResourceHandlerConfig):
    """ResourceHandler specific for promethee's masks"""

    # Resource
    kind: str = Field("promethee_mask", const=True)
    promid: str
    version: Optional[str] = None
