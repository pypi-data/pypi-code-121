"""
Module for environment level config.
"""

import os

GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "XXX")
DEPLOYMENT_MODE = os.environ.get("FAUX_DATA_DEPLOYMENT_MODE",
                                 "local")  # or cloud_function

TEMPLATE_BUCKET = os.environ.get("FAUX_DATA_TEMPLATE_BUCKET", "")
TEMPLATE_LOCATION = os.environ.get("FAUX_DATA_TEMPLATE_LOCATION", "")
