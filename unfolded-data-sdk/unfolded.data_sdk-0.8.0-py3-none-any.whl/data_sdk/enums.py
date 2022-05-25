from enum import Enum


class MediaType(str, Enum):
    CSV = "text/csv"
    GEOJSON = "application/geo+json"
    JSON = "application/json"


class DatasetType(str, Enum):
    MANAGED = "managed"
    EXTERNALLY_HOSTED = "externally-hosted"
    VECTOR_TILE = "vector-tile"
    RASTER_TILE = "raster-tile"
    HEX_TILE = "hex-tile"
    SQL = "sql"


class HexTileFieldType(str, Enum):
    """Possible field types for hextile datasets"""

    STRING = "string"
    INTEGER = "integer"
    REAL = "real"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    GEOJSON = "geojson"
    POINT = "point"


class AggregationMethod(str, Enum):
    """Available aggregation types
    Values should be strings or functions that can be passed to pd.DataFrame.agg
    """

    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"


class Dtype(str, Enum):
    """Available data types"""

    INT64 = "int64"
    INT32 = "int32"
    INT16 = "int16"
    INT8 = "int8"
    UINT64 = "uint64"
    UINT32 = "uint32"
    UINT16 = "uint16"
    UINT8 = "uint8"
    BOOL = "bool"
    FLOAT64 = "float64"
    FLOAT32 = "float32"
    FLOAT16 = "float16"


class TimeInterval(str, Enum):
    """Time granularities for hextile job input."""

    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    SECOND = "SECOND"


class TileMode(str, Enum):
    """Available tile modes"""

    DENSE = "dense"
    SPARSE = "sparse"
    AUTO = "auto"


class NodeType(str, Enum):
    """Enum for the supported QueryNode types"""

    DATASET = "dataset"
    INLINE_DATA = "inline_data"
    SELECT = "select"
    GROUP = "group"
    FILTER = "filter"
    SORT = "sort"
    LIMIT = "limit"
    SAMPLE = "sample"
    JOIN = "join"
    ENRICH = "enrich"
    HEXIFY = "hexify"
    TILE_EXTRACT = "tileExtract"
