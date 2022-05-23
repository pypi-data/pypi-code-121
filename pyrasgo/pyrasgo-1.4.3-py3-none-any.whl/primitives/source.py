import logging
import os
from collections import OrderedDict
from typing import Dict, Optional

import pandas as pd
import yaml
from pyrasgo.api.connection import Connection
from pyrasgo.schemas import DataType, FeaturesYML
from pyrasgo.schemas import data_source as schema
from pyrasgo.schemas.transform import Transform
from pyrasgo.utils import naming



class DataSource(Connection):
    """
    Stores a Rasgo DataSource
    """
    def __init__(self, api_object, **kwargs):
        super().__init__(**kwargs)
        self._fields = schema.DataSource(**api_object)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Source(id={self.id}, name={self.name}, sourceType={self.sourceType}, table={self.fqtn})"

    def __getattr__(self, item):
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            self.refresh()
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")

# ----------
# Properties
# ----------

    @property
    def fqtn(self) -> str:
        return naming.make_fqtn(
            table=self.table,
            database=self.tableDatabase,
            schema=self.tableSchema
        )

# --------
# Methods
# --------

    def display_source_code(self):
        """
        Convenience function to display the sourceCode property
        """
        return self._fields.sourceCode

    def read_into_df(self,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Pull Source data from DataWarehouse into a pandas Dataframe
        """
        from pyrasgo.api.read import Read
        return Read().source_data(id=self.id, filters=filters, limit=limit)

    def rebuild_from_source_code(self):
        """
        Rebuild the Source using the source code
        """
        raise NotImplementedError()

    def refresh(self):
        """
        Updates the Soure's attributes from the API
        """
        self._fields = schema.DataSource(**self._get(f"/data-source/{self.id}", api_version=1).json())

    def rename(self, new_name: str):
        """
        Updates a DataSource's display name
        """
        print(f"Renaming DataSource {self.id} from {self.name} to {new_name}")
        source = schema.DataSourceUpdate(id=self.id, name=new_name)
        self._fields = schema.DataSource(**self._patch(f"/data-source/{self.id}",
                                                    api_version=1, _json=source.dict(exclude_unset=True, exclude_none=True)).json())

    def to_dict(self) -> dict:
        for f in self._fields.features:
            attr_dict = {}
            for a in f.attributes:
                attr_dict.update({a.key: a.value})
            f.attributes = attr_dict
        return FeaturesYML(
                name=self._fields.name,
                sourceTable=self._fields.table,
                dimensions=[{"columnName": d.columnName, "dataType": d.dataType, "granularity": d.granularity.name} for d in self._fields.dimensions],
                features=self._fields.features,
                sourceCode=self._fields.sourceCode,
                sourceType=self._fields.sourceType
        ).dict(exclude_unset=False, by_alias=True)

    def to_yml(self, file_name: str,
                     directory: str = None,
                     overwrite: bool = True
    ) -> str:
        if directory is None:
            directory = os.getcwd()

        if directory[-1] == "/":
            directory = directory[:-1]

        if file_name.split(".")[-1] not in ['yaml', 'yml']:
            file_name += ".yaml"

        if os.path.exists(f"{directory}/{file_name}") and overwrite:
            logging.warning(f"Overwriting existing file {file_name} in directory: {directory}")

        safe_dumper = yaml.SafeDumper
        safe_dumper.add_representer(DataType, lambda self, data: self.represent_str(str(data.value)))
        safe_dumper.add_representer(OrderedDict, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items()))
        safe_dumper.ignore_aliases = lambda self, data: True

        with open(f"{directory}/{file_name}", "w") as _yaml:
            yaml.dump(data=OrderedDict(self.to_dict()), Dumper=safe_dumper, stream=_yaml)

    def _make_table_metadata(self) -> Dict:
        return {
            "database": self.dataTable.databaseName,
            "schema": self.dataTable.schemaName,
            "table": self.dataTable.tableName,
        }

