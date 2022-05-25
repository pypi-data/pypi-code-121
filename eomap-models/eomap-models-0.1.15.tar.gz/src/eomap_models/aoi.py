
from typing import Dict, List, Tuple

from bson import ObjectId
from geojson_pydantic import Feature
from pydantic import BaseModel, Field
from pydantic.fields import PrivateAttr


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AOI(BaseModel):
    aoi_type: str = Field(...)
    feature_collection: List[Feature]
    _coords: List[Tuple[float, float]] = PrivateAttr()
    _min_max_lat: Tuple[float, float] = PrivateAttr()
    _aoi_data: Dict = PrivateAttr()
    _geometry: Dict = PrivateAttr()
    _top_left: Tuple[float, float] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._coords = self.make_coords_array()
        self._min_max_lat = self.make_min_max_lat()
        self._aoi_data = self.make_aoi_data()
        self._geometry = self.make_geometry()
        self._top_left = self.make_top_left()

    def make_coords_array(self):
        return self.feature_collection[0].geometry.coordinates[0]

    def make_min_max_lat(self):
        geo_type = self.feature_collection[0].geometry.type
        if geo_type == "Polygon":
            lats = [i[1] for i in self._coords]
            return min(lats), max(lats)
        elif geo_type == "MultiPolygon":
            lats = [i[1] for i in self._coords[0]]
            return min(lats), max(lats)

    def make_aoi_data(self):
        return {"type": self.aoi_type,
                "features": [f.dict() for f in self.feature_collection]}

    def make_geometry(self):
        return self._aoi_data["features"][0]["geometry"]

    def make_top_left(self):
        xs = [x[0] for x in self._coords]
        ys = [y[1] for y in self._coords]
        return min(xs), max(ys)
