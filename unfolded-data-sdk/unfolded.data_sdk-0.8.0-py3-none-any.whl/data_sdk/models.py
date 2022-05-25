# Pydantic validators are class methods, so require the first param to be `cls`, but
# pylint can't recognize this: https://github.com/samuelcolvin/pydantic/issues/568
# pylint: disable=no-self-argument
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    root_validator,
    validator,
)

from unfolded.data_sdk.enums import (
    AggregationMethod,
    DatasetType,
    Dtype,
    HexTileFieldType,
    MediaType,
    TileMode,
    TimeInterval,
)


class DatasetMetadata(BaseModel):
    """A model representing metadata for an Unfolded Studio Dataset"""

    media_type: Optional[Union[MediaType, StrictStr]] = Field(alias="contentType")
    size: Optional[StrictInt]
    source: Optional[StrictStr]
    tileset_data_url: Optional[StrictStr] = Field(alias="tilesetDataUrl")
    tileset_metadata_url: Optional[StrictStr] = Field(alias="tilesetMetadataUrl")
    image_url: Optional[StrictStr] = Field(alias="imageUrl")
    metadata_url: Optional[StrictStr] = Field(alias="metadataUrl")
    data_status: Optional[StrictStr] = Field(alias="dataStatus")

    class Config:
        allow_population_by_field_name = True


class Dataset(BaseModel):
    """A model representing an Unfolded Studio Dataset"""

    id: UUID
    name: StrictStr
    type: DatasetType
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    description: Optional[StrictStr]
    is_valid: StrictBool = Field(..., alias="isValid")
    metadata: DatasetMetadata

    class Config:
        allow_population_by_field_name = True


class MapState(BaseModel):
    """A model representing an Unfolded Studio Map Starte"""

    id: UUID
    # data contains the actual map configuration, and should be modeled more concretely than a
    # generic Dictionary.
    # Todo (wesam@unfolded.ai): revisit this once we have a style building strategy
    data: Dict

    class Config:
        allow_population_by_field_name = True


class MapUpdateParams(BaseModel):
    """A model respresenting creation and update parameters for Unfolded Maps"""

    name: Optional[StrictStr]
    description: Optional[StrictStr]
    latest_state: Optional[MapState] = Field(None, alias="latestState")
    datasets: Optional[List[UUID]]

    class Config:
        allow_population_by_field_name = True


class Map(BaseModel):
    """A model representing an Unfolded Studio Map"""

    id: UUID
    name: StrictStr
    description: Optional[StrictStr]
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    latest_state: Optional[MapState] = Field(None, alias="latestState")
    datasets: Optional[List[Dataset]]

    class Config:
        allow_population_by_field_name = True


class HexTileMetadataField(BaseModel):
    """A model representing a field (column) within hextile dataset metadata"""

    name: StrictStr
    type: HexTileFieldType
    domain: Optional[Tuple[float, float]]

    class Config:
        allow_population_by_field_name = True
        # Ignore extra properties
        extra = "ignore"


class HexTileMetadata(BaseModel):
    """A model representing an metadata for a hextile dataset"""

    fields: List[HexTileMetadataField]
    name: Optional[StrictStr] = None
    min_zoom: StrictInt = Field(..., alias="minZoom")
    max_zoom: StrictInt = Field(..., alias="maxZoom")
    resolution_offset: StrictInt = Field(..., alias="resolutionOffset")
    version: StrictStr

    class Config:
        allow_population_by_field_name = True
        # Ignore extra properties
        extra = "ignore"


class HexTileOutputColumnConfig(BaseModel):
    source_column: StrictStr = Field(..., alias="sourceColumn")
    """Column name in source dataset"""

    target_column: StrictStr = Field(..., alias="targetColumn")
    """Column name in target dataset"""

    agg_method: Optional[AggregationMethod] = Field(..., alias="aggMethod")
    """Aggregation method to use for column"""

    dtype: Optional[Dtype] = None
    """Dtype to use for column"""

    class Config:
        allow_population_by_field_name = True


class H3Resolution(StrictInt):
    ge = 0
    le = 15


class HexTileConfig(BaseModel):
    """Config for hextiling process"""

    @root_validator
    def _validate_source_columns(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        source_hex_column = values.get("source_hex_column")
        source_lat_column = values.get("source_lat_column")
        source_lng_column = values.get("source_lng_column")
        source_time_column = values.get("source_time_column")
        time_intervals = values.get("time_intervals")

        if source_hex_column:
            if source_lat_column or source_lng_column:
                raise ValueError(
                    "Only provide source_hex_column or source_lat_column and source_lng_column, but not all three"
                )
        else:
            if not source_lat_column or not source_lng_column:
                raise ValueError(
                    "Must provide either source_hex_column or source_lat_column and source_lng_column"
                )

        if time_intervals and not source_time_column:
            raise ValueError(
                "Must provide source_time_column when passing in time_interval"
            )

        return values

    source: UUID
    """Source Dataset"""

    @validator("source", pre=True, always=True)
    def _coerce_source_to_uuid(cls, v: Any) -> Any:
        if isinstance(v, Dataset):
            return v.id

        return v

    target: Optional[UUID] = None
    """Target Dataset"""

    @validator("target", pre=True, always=True)
    def _coerce_target_to_uuid(cls, v: Any) -> Any:
        if isinstance(v, Dataset):
            return v.id

        return v

    source_hex_column: Optional[StrictStr] = Field(None, alias="sourceHexColumn")
    """Name of the hex column in the source dataset"""

    source_lat_column: Optional[StrictStr] = Field(None, alias="sourceLatColumn")
    """Name of the lat column in the source dataset"""

    source_lng_column: Optional[StrictStr] = Field(None, alias="sourceLngColumn")
    """Name of the lng column in the source dataset"""

    source_time_column: Optional[StrictStr] = Field(None, alias="sourceTimeColumn")
    """Name of the time column, in the source dataset"""

    time_intervals: Optional[List[TimeInterval]] = Field(
        None, alias="timeIntervals", min_items=1
    )
    """List of time intervals to use for temporal datasets"""

    target_res_offset: Optional[H3Resolution] = Field(None, alias="targetResOffset")
    """
    Offset between the resolution of the tile to the resolution of the data within it
    """

    finest_resolution: Optional[H3Resolution] = Field(None, alias="finestResolution")
    """
    Finest resolution for the data hexes within a tile (when creating a tileset from lat/lng columns)
    """

    experimental_tile_mode: Optional[TileMode] = Field(None, alias="tileMode")

    output_columns: Optional[List[HexTileOutputColumnConfig]] = Field(
        None, alias="outputColumns", min_items=1
    )

    experimental_positional_indexes: Optional[StrictBool] = Field(
        None, alias="positionalIndexes"
    )

    class Config:
        allow_population_by_field_name = True
