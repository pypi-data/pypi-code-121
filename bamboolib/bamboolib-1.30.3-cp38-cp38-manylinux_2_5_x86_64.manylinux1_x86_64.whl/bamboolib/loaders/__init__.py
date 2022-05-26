# Copyright (c) Databricks Inc.
# Distributed under the terms of the DB License (see https://databricks.com/db-license-source
# for more information).

"""
Setup loader plugins. The import order defines the order in the search results.
"""

from bamboolib.loaders.databricks_database_table_loader import (
    DatabricksDatabaseTableLoader,
)
from bamboolib.loaders.dummy_data import DummyData
