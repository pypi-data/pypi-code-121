import enum


class FiddlerPublishSchema:
    STATIC = '__static'
    DYNAMIC = '__dynamic'
    ITERATOR = '__iterator'
    UNASSIGNED = '__unassigned'

    VALID_SCHEMA_KEYWORDS = [STATIC, DYNAMIC, ITERATOR]

    ORG = '__org'
    MODEL = '__model'
    PROJECT = '__project'
    TIMESTAMP = '__timestamp'
    DEFAULT_TIMESTAMP = '__default_timestamp'
    TIMESTAMP_FORMAT = '__timestamp_format'
    EVENT_ID = '__event_id'
    IS_UPDATE_EVENT = '__is_update_event'
    STATUS = '__status'
    LATENCY = '__latency'
    ITERATOR_KEY = '__iterator_key'

    CURRENT_TIME = 'CURRENT_TIME'


@enum.unique
class DataUploadType(enum.Enum):
    """Supported Data Upload for the Fiddler engine."""

    DATAFRAME = 0
    LOCAL_DISK = 1
    AWS_S3 = 2
    GCP_STORAGE = 3


class ExtractorDataSource:
    UNKNOWN = -1
    JSON = 0
    LOCAL_DISK = DataUploadType.LOCAL_DISK.value
    AWS_S3 = DataUploadType.AWS_S3.value
    GCP_STORAGE = DataUploadType.GCP_STORAGE.value


class ExtractorDataType:
    UNKNOWN = -1
    BATCHED = 0
    STREAMED = 1


class ExtractorFileType:
    UNKNOWN = -1
    CSV = 0
    PARQUET = 1
    PKL = 2
    CSV_GZ = 3
    AVRO = 4


class TransformType:
    UNKNOWN = -1
    JSON = 0
    DF = 1
    PARQUET = 2
    AVRO = 3


# Since `None` is a valid return type, this value is used to indicate a strictly missing value.
#  e.g. a dictionary with no key would return `SENTINEL_ABSENT`
SENTINEL_ABSENT = ()


SUPPORTABLE_FILE_EXTENSIONS = ['.csv', '.avro']
FILE_EXTENSIONS_TO_CODE = {
    '.csv': ExtractorFileType.CSV,
    '.csv.gz': ExtractorFileType.CSV_GZ,
    '.parquet': ExtractorFileType.PARQUET,
    '.pq': ExtractorFileType.PARQUET,
    '.pkl': ExtractorFileType.PKL,
    '.avro': ExtractorFileType.AVRO,
}
DTYPES_CSV = 'dtypes.csv'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

CHUNK_SIZE = 1000
DOT = '.'

# CSV configurations
CSV_EXTENSION = 'csv'

# Parquet configuration
PARQUET_EXTENSION = 'parquet'
PARQUET_COMPRESSION = 'snappy'
PARQUET_ENGINE = 'pyarrow'
PARQUET_ROW_GROUP_SIZE = 10_000
