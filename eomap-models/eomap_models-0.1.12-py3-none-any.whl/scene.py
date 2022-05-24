
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from .aoi import AOI


class SceneBase(BaseModel):
    request_id: str
    scene_id: str


class SceneSummary(SceneBase):
    scene_name: str
    tile: str = None
    tile_intersection_w_aoi: Optional[float]
    date_time: datetime

    thumbnail_url: Optional[str]

    subset_cloud_coverage: Optional[float]
    subset_no_data_percetange: Optional[float]
    overall_data_coverage: Optional[float]
    overall_data_perc_of_aoi:  Optional[float]
    scene_grade:  Optional[float]
        
    def __init__(self, **data):
        super().__init__(**data)
        self.tile = self.get_tile_name_from_scene()
    
    def get_tile_name_from_scene(self):
        name = self.scene_id.split("_")[1]
        if len(name) != 5:
            name = f"0{name}"
        return name


class Scene(SceneSummary):
    aoi: Optional[AOI]
    scl_href_url: Optional[str]
    blue_channel_href: Optional[str]
    tile_cloud_coverage: Optional[float]
    mean_blue_channel: Optional[float]
    normalised_blue_channel: Optional[float]