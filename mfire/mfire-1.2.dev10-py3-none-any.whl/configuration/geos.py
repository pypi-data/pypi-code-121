"""
Pydantic models for custom Promethee Geos
Parts of this module are shamefully stolen from
https://github.com/developmentseed/geojson-pydantic
"""
import re
import abc
import warnings
from typing import Tuple, Any, List, Union, Dict, Optional

import shapely.geometry as sh
from pydantic import BaseModel, Field, ValidationError, validator, root_validator
from pydantic.error_wrappers import ErrorWrapper

from mfire.configuration.resources import MaskRHConfig
from mfire.utils.hash import MD5


# =====================================
# Custom types
# =====================================
NumType = Union[float, int]
Position = Tuple[NumType, NumType]

# =====================================
# Geometries
# =====================================


class _GeometryBaseConfig(BaseModel, abc.ABC):
    """Base class for geometry models"""

    coordinates: Any  # will be constrained in child classes

    @property
    def __geo_interface__(self):
        return self.dict()


class PointConfig(_GeometryBaseConfig):
    """Point Model"""

    type: str = Field("Point", const=True)
    coordinates: Position


class MultiPointConfig(_GeometryBaseConfig):
    """MultiPoint Model"""

    type: str = Field("MultiPoint", const=True)
    coordinates: List[Position] = Field(..., min_items=1)


class LineStringConfig(_GeometryBaseConfig):
    """LineString Model"""

    type: str = Field("LineString", const=True)
    coordinates: List[Position] = Field(..., min_items=2)


class MultiLineStringConfig(_GeometryBaseConfig):
    """MultiLineString Model"""

    type: str = Field("MultiLineString", const=True)
    coordinates: List[List[Position]] = Field(..., min_items=1)

    @validator("coordinates")
    def check_coordinates(cls, multilinestring):
        """Validate that MultiLineString coordinates pass the GeoJSON spec"""
        if any([len(linestring) < 2 for linestring in multilinestring]):
            raise ValueError("All linestrings must have at least 2 Postion items")
        return multilinestring


class PolygonConfig(_GeometryBaseConfig):
    """Polygon Model"""

    type: str = Field("Polygon", const=True)
    coordinates: List[List[Position]] = Field(..., min_items=1)

    @validator("coordinates")
    def check_coordinates(cls, polygon):
        """Validate that Polygon coordinates pass the GeoJSON spec"""
        if any([len(ring) < 4 for ring in polygon]):
            raise ValueError("All linear rings must have four or more coordinates")
        if any([ring[-1] != ring[0] for ring in polygon]):
            raise ValueError("All linear rings have the same start and end coordinates")
        return polygon


class MultiPolygonConfig(_GeometryBaseConfig):
    """MultiPolygon Model"""

    type: str = Field("MultiPolygon", const=True)
    coordinates: List[List[List[Position]]] = Field(..., min_items=1)

    @validator("coordinates")
    def check_coordinates(cls, multipolygon):
        """Validate that MultiPolygon coordinates pass the GeoJSON spec"""
        if any([len(polygon) == 0 for polygon in multipolygon]):
            raise ValueError("Polygons must have at least one ring")
        if any([any([len(ring) < 4 for ring in polygon]) for polygon in multipolygon]):
            raise ValueError("All linear rings must have four or more coordinates")
        if any(
            [any([ring[-1] != ring[0] for ring in polygon]) for polygon in multipolygon]
        ):
            raise ValueError("All linear rings have the same start and end coordinates")
        return multipolygon


GeometryConfig = Union[
    PointConfig,
    MultiPointConfig,
    LineStringConfig,
    MultiLineStringConfig,
    PolygonConfig,
    MultiPolygonConfig,
]


class GeometryCollectionConfig(BaseModel):
    """GeometryCollection Model"""

    type: str = Field("GeometryCollection", const=True)
    geometries: List[GeometryConfig] = Field(..., min_items=1)

    def __iter__(self):
        """iterate over geometries"""
        return iter(self.geometries)

    def __len__(self):
        """return geometries length"""
        return len(self.geometries)

    def __getitem__(self, index):
        """get geometry at a given index"""
        return self.geometries[index]


def parse_geometry_obj(obj) -> GeometryConfig:
    """
    `obj` is an object that is supposed to represent a GeoJSON geometry.
    This method returns the reads the `"type"` field and returns the
    correct pydantic Geometry model.
    """
    if "type" not in obj:
        raise ValidationError(
            [
                ErrorWrapper(ValueError("Missing 'type' field in geometry"), "type"),
                "Geometry",
            ]
        )
    if obj["type"] == "Point":
        return PointConfig.parse_obj(obj)
    elif obj["type"] == "MultiPoint":
        return MultiPointConfig.parse_obj(obj)
    elif obj["type"] == "LineString":
        return LineStringConfig.parse_obj(obj)
    elif obj["type"] == "MultiLineString":
        return MultiLineStringConfig.parse_obj(obj)
    elif obj["type"] == "Polygon":
        return PolygonConfig.parse_obj(obj)
    elif obj["type"] == "MultiPolygon":
        return MultiPolygonConfig.parse_obj(obj)
    raise ValidationError(
        [ErrorWrapper(ValueError("Unknown type"), "type")], "Geometry"
    )


# =====================================
# Features
# =====================================


class PropertiesConfig(BaseModel):
    """Properties Model"""

    label: str
    name: Optional[str]
    is_axe: Optional[bool] = False
    customers: Optional[List[str]]
    tags: Optional[List[str]]
    owner: Optional[str]
    visibility: Optional[str]
    center: Optional[str]
    thumbnail: Optional[str]
    shapefile_properties: Optional[Dict]
    station: Optional[str]
    service_identifiers_values: Optional[List]
    identifiers: Optional[Dict]
    extra_fields: Optional[Dict]

    @validator("name", always=True)
    def get_name_from_label(cls, v: str, values: dict) -> str:
        if v:
            return v
        # ! temporary patch before etiquettes
        label = values["label"]
        search = re.search(r"^.*_\((.*)$", label)
        if search:
            return search.group(1).strip("()")
        return label


class FeatureConfig(BaseModel):
    """Feature Model"""

    id: str
    properties: Optional[PropertiesConfig]
    type: str = Field("Feature", const=True)
    geometry: GeometryConfig

    class Config:
        """Config: FeatureConfig own config (such as advised by Pydantic)"""

        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v: Any, values: dict) -> GeometryConfig:
        feat_id = values.get("id")
        feat_label = dict(values.get("properties", {})).get("label")
        # geometry validation
        geometry = v
        if hasattr(v, "__geo_interface__"):
            geometry = v.__geo_interface__

        # geometry's shape validation
        shape = sh.asShape(geometry)
        if not shape.is_valid:
            raise ValueError(
                f"Given geometry's shape no valid (id={feat_id}, label={feat_label})."
            )
        lon0, lat0, lon1, lat1 = shape.bounds
        lon_lat_valid = (
            (-180 <= lon0 <= 180)
            and (-180 <= lon1 <= 180)
            and (-90 <= lat0 <= 90)
            and (-90 <= lat1 <= 90)
        )
        if not lon_lat_valid:
            raise ValueError(
                f"Longitude/Latitude error : (lon, lat, lon, lat) = {shape.bounds}"
                ", while longitude values must be in [-180,180] and latitude values"
                f" must be in [-90, 90]. (id={feat_id}, label={feat_label})."
            )
        return geometry

    @property
    def shape(self) -> sh.base.BaseGeometry:
        """Returns the equivalent shapely geometry.

        Returns:
            sh.base.BaseGeometry: shapely geometry
        """
        return sh.asShape(self.geometry)

    def is_in(
        self, lat_min: float, lon_min: float, lat_max: float, lon_max: float
    ) -> bool:
        grid = sh.Polygon(
            (
                (lon_min, lat_min),
                (lon_min, lat_max),
                (lon_max, lat_max),
                (lon_max, lat_min),
                (lon_min, lat_min),
            )
        )
        return grid.contains(self.shape)


class FeatureCollectionConfig(BaseModel):
    """FeatureCollection Model"""

    type: str = Field("FeatureCollection", const=True)
    features: List[FeatureConfig]

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]

    def __hash__(self) -> str:
        return MD5(self.dict()).hash


# =====================================
# Mask configuration model
# =====================================


class MaskConfig(BaseModel):
    """Mask configuration model"""

    file: str
    id: str
    name: str
    config_hash: str
    prod_hash: str
    mask_hash: Optional[str]
    geos: FeatureCollectionConfig
    resource_handler: MaskRHConfig

    @root_validator
    def check_mask_hash(cls, values):
        geos_hash = values["geos"].__hash__()
        mask_hash = values.get("mask_hash")
        if mask_hash != geos_hash:
            if mask_hash:
                warnings.warn(
                    "Given mask_hash differs from the given geos hash. Changed it."
                )
            values["mask_hash"] = geos_hash
        rh_hash = values["resource_handler"].version
        if rh_hash != geos_hash:
            if rh_hash:
                warnings.warn(
                    "Given version in resource handler differs from the given geos "
                    "hash. Changed it."
                )
            values["resource_handler"].version = geos_hash
        return values
