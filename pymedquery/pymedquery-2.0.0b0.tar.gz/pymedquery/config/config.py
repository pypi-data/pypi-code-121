import os
from collections import defaultdict
from typing import Dict, List, Tuple
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from pymedquery.src.helpers import nested_dict

# Paths
ROOT: str = os.getcwd()
# Get the package path
data_path: str = pkg_resources.path('pymedquery.sql.default', 'image_default_query.sql')
data_path_col: str = pkg_resources.path('pymedquery.sql.default', 'col_query.sql')
sh_path: str = pkg_resources.path('pymedquery', 'medqueryInit.sh')
with data_path as sql, data_path_col as col_query_sql, sh_path as sh:
    SERIES_MASK_QUERY_DEFAULT = str(sql)
    COL_QUERY_DEFAULT = str(col_query_sql)
    SHPATH = str(sh)

MOD_FILE_PATH: os.PathLike = os.path.join(ROOT, 'tests/data/modelw_v1.1.0.pkl')
# postgres and storage params
DATABASE_TMP: str = 'medquery_template'

STORAGE_NAME: str = "medical_imaging_storage"
BUCKET_NAME: str = "multimodal-images"
TEST_BUCKET: str = 'test-bucket'
bucket_dict: Dict[str, List[str]] = defaultdict(list)
blob_dict: Dict[str, List[str]] = defaultdict(list)
nested_blob_dict: Dict[str, Dict[str, any]] = nested_dict()
BUCKET_KEYS: List[str] = ["bucket_name", "creation_date"]
# NOTE! naming conventions tend to change between MinIO versions. Be aware!
IMG_META = 'X-Amz-Meta-Img_shape'
DTYPE_META = 'X-Amz-Meta-Dtype'

TEST_TABLE: str = 'test_table'
PRIMARY_KEY: List[str] = ['series_uid']
NEW_COL_VALS: str = 'new_name'
COL_TO_CHANGE: str = 'protocol_names'
COLS: List[str] = ['series_uid', 'pixel_spacing', 'series_number', 'protocol_names']
RECORDS: List[Tuple[str, List[float], int, str]] = [('series_666', [0.431, 0.233], 32, 'i_am_a_protocol')]
SQL_FILE_PATH: os.PathLike = os.path.join(ROOT, 'pymedquery/data/sql/test.sql')

USELESS_SERIES: str = 'series_f1fe0d2028b182c7c8ced7cfcc180b272109b19a7c188566c64fed97f6e8616377898e6939a9fec9d2758be93f87c'
TEST_SQL_FILE: os.PathLike = os.path.join(ROOT, 'pymedquery/data/sql/create.sql')
TEST_DATA_FILEPATH: os.PathLike = os.path.join(ROOT, 'tests/data/np.npy')
TEST_WEIGHTS_FILEPATH: os.PathLike = os.path.join(ROOT, 'tests/data/model_weights_v010.h5')

BLOB_NAME_I = 'img_666'
BLOB_NAME_W = 'mod_weights_666'

BLOBS: List[str] = [BLOB_NAME_I, BLOB_NAME_W]

UPDATE_ON_PRIMARY_KEY: str = 'series_666'

# Extensions
EXT_READTYPE_DICT: Dict[str, str] = {"pkl": "rb", "pickle": "r", "json": "r", "csv": "r", "gz": "rb"}

USER: str = os.environ.get('MQUSER')
PASSWORD: str = os.environ.get('MQPWD')
DATABASE: str = os.environ.get('DATABASE')
