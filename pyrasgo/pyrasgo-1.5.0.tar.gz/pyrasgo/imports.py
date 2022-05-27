"""
Manage Data Warehouse specific imports
"""

### ------------
# Note to users:
# This module is used to allow pyrasgo to install the minimum dependencies
# needed to run your flavor of DataWarehouse

# We support downloading extas packages for each DW: e.g. `pyrasgo[snowflake]`
# so your machine is not cluttered with unused google packages.
# In doing so, we run the risk of not having required dependencies at runtime

# This module attempts to import all possible datawarehouse packages, and
# fails gracefully if they are not present
# pyRasgo will use these empty aliases to raise a PackageDependencyWarning
# from the class or function that needs the import
### ------------

# Attempt safe imports of all DW packages so we can warn later if they are missing
try:
    from snowflake import connector as sf_connector
    from snowflake.connector.pandas_tools import write_pandas
except ImportError:
    sf_connector = None
    write_pandas = None

try:
    from google.cloud import bigquery as bq
    from google.cloud import exceptions as gcp_exc
    from google.oauth2 import service_account as gcp_svc
except ImportError:
    bq = None
    gcp_exc = None
    gcp_svc = None

try:
    from google_auth_oauthlib import flow as gcp_flow
except ImportError:
    gcp_flow = None
