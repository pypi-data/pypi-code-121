import os
from setuptools import setup, find_packages

setup(
    name="pg_to_evalscript",
    version=os.environ.get("PG_TO_EVALSCRIPT_VERSION", "0.0.0"),
    packages=["pg_to_evalscript"],
    package_data={
        "pg_to_evalscript": ["javascript_datacube/*.js", "javascript_common/*.js", "javascript_processes/*.js"]
    },
)
