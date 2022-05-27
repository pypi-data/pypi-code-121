"""
Common constants used by the package.

We maintain this file to make sure that we don't have inconsistencies in the
constants used. It is common to notice spelling mistakes associated with strings
additionally, we don't get IDE's to automatically suggest values.

consider:

```python
a_dict["key"]
```

and 

```
a_dict[const.KEY]
```
In the latter, a mature IDE will suggest the KEY constant, reducing time and ensuring consistency.
"""
ID = "id"
AUTHORIZATION = "authorization"
ROUTE__CALL = "/call_report/calls/"
ROUTE__TURN = "/call_report/calls/{}/"
ROUTE__EXPORT_CALL = "/call_report/export/calls/"
LIVE = "live"
SUBTESTING = "subtesting"
FILE_URL = "file_url"
# ----------- Tagged calls are one of the following -----------
REPORTED = "reported"
RESOLVED = "resolved"
# but if there are no preferences, we can get
# all calls.
ALL = "all"
# ------------------------------------------------------------

# --------------------- Get call params ----------------------
START_DATE = "start"
END_DATE = "end"
LANG_CODE = "lang_code"
PAGE_SIZE = "page_size"
CALL_TYPE = "call_type"
IGNORED_CALLER_NUMBERS = "ignored_caller_numbers"
TAB = "tab"
PAGE = "page"
CUSTOM_SEARCH_KEY = "custom_search_key"
CUSTOM_SEARCH_VALUE = "custom_search_value"

# These are system generated pings and are never required
DEFAULT_IGNORE_CALLERS_LIST = ("ev-connect", "0000000000")
# ---------------------------------------------------------

# ----------- columns in the calls+turns list -------------
TOTAL_PAGES = "total_pages"
TOTAL_ITEMS = "total_items"
ITEMS = "items"
UUID = "uuid"
CONV_UUID = "conversation_uuid"
CALL_UUID = "call_uuid"
CONV_ID = "conversation_id"
CALL_ID = "call_id"
TURNS = "turns"
CONVERSATIONS = "conversations"
PREDICTION = "prediction"
METADATA = "metadata"
DEBUG_METADATA = "debug_metadata"
CREATED_AT = "created_at"
UPDATED_AT = "updated_at"
CALL_HISTORY = "call_history"
# ---------------------------------------------------------

# ------------------------- cli -----------------------------------
DESCRIPTION = """
Skit.ai's calls library {version}.

We provide means to sample calls and conversations from a 
specified environment.

Learn about this library at: https://github.com/skit-ai/skit-calls
""".strip()
# ------------------------------------------------------------------

ON_DISK = "on-disk"
IN_MEMORY = "in-memory"
MEMORY_LIMIT = 10e7
Q_DELAY = 0.2
DEFAULT_API_GATEWAY_URL = "https://apigateway.vernacular.ai"
DEFAULT_CALL_QUANTITY = 200
DEFAULT_TIMEZONE = "Asia/Kolkata"

S3_URL_PATTERN_1 = r"https:\/\/s3\.\w{2}-(north|south|east|west)-\d{1,2}\.amazonaws\.com\/([A-Za-z0-9\-]+)\/(.+)"
S3_URL_PATTERN_2 = r"https:\/\/([a-zA-Z\-]+)\.s3\.\w{2}-(north|south|east|west)-\d{1,2}\.amazonaws\.com\/(.+)"
S3_OBJ_PATTERN = r"s3:\/\/([a-zA-Z0-9\-]+)\/(.+)"
RANDOM_CALL_ID_QUERY = "RANDOM_CALL_ID_QUERY"
RANDOM_CALL_DATA_QUERY = "RANDOM_CALL_DATA_QUERY"
CALL_IDS_FROM_UUIDS_QUERY = "CALL_IDS_FROM_UUIDS_QUERY"
RANDOM_CALL_DATA_CURSOR = "random_call_data_cursor"

# Call types
OUTBOUND = "OUTBOUND"
INBOUND = "INBOUND"
CALL_TEST = "CALL_TEST"
DB_HOST = "DB_HOST"
DB_PORT = "DB_PORT"
DB_USER = "DB_USER"
DB_PASSWORD = "DB_PASSWORD"
DB_NAME = "DB_NAME"
EXCLUDED_NUMBERS = "excluded_numbers"
CALL_IDS = "call_ids"
USE_CASE = "use_case"
FLOW_NAME = "flow_name"
LANG = "lang"
MIN_AUDIO_DURATION = "min_duration"
ASR_PROVIDER = "asr_provider"
STATES = "states"
GRAPH = "graph"
OUTPUT = "output"
INTENTS = "intents"
NAME = "name"
SCORE = "score"
VALUES = "values"
SLOTS = "slots"
TRANSCRIPT = "transcript"
CDN_RECORDINGS_BASE_PATH = "CDN_RECORDINGS_BASE_PATH"
WAV_FILE = ".wav"
CSV_FILE = ".csv"
LIMIT = "limit"
OFFSET = "offset"
TURNS_LIMIT = 1000
CONVERSATION_TYPES = "conversation_types"
CONVERSATION_SUB_TYPES = "conversation_sub_types"
UCASE_INPUT = "INPUT"
UCASE_AUDIO = "AUDIO"
MARGIN = 0.1
