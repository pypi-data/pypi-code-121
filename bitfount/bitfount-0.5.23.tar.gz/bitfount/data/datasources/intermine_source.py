"""Module containing IntermineSource class.

IntermineSource class handles loading data stored in Intermine templates.

Intermine is an open source biological data warehouse developed by the University
of Cambridge http://intermine.org/ .
The IntermineSource launches a pod that can access all templates defined under a
specified service. Please see Intermine's tutorials for a detailed overview of there
python API: https://github.com/intermine/intermine-ws-python-docs .
"""
import itertools
import logging
from typing import Any, Dict, Iterable, List, Optional, Union

from intermine.webservice import Service
import numpy as np
import pandas as pd

from bitfount.data.datasources.base_source import _MultiTableSource
from bitfount.data.utils import _convert_python_dtypes_to_pandas_dtypes
from bitfount.types import _Dtypes

logger = logging.getLogger(__name__)

INTERMINE_TYPE_MAPPING = {
    "java.lang.String": str,
    "java.lang.Double": float,
    "java.lang.Float": float,
    "java.lang.Integer": int,
    "java.lang.Boolean": bool,
    "org.intermine.objectstore.query.ClobAccess": object,
    "java.util.Date": object,
    "int": int,
}


class IntermineSource(_MultiTableSource):
    """Data Source for loading data from Intermine templates.

    Intermine is an open source biological data warehouse developed by the University
    of Cambridge http://intermine.org/ .
    The IntermineSource launches a pod that can access all templates defined under a
    specified service. Please see Intermine's tutorials for a detailed overview of their
    python API: https://github.com/intermine/intermine-ws-python-docs .
    """

    def __init__(self, service_url: str, token: Optional[str], **kwargs: Any) -> None:
        self.service = Service(service_url, token=token)
        self.all_templates_names: Dict[
            str, List[str]
        ] = self.service.all_templates_names
        self.template_to_user_map = {
            t: user
            for user, tables in self.service.all_templates_names.items()
            for t in tables
        }
        self._check_duplicate_templates()

    def _check_duplicate_templates(self) -> None:
        """Check for duplicate template names in intermine service."""
        table_names = set()
        for t in self.table_names:
            if t in table_names:
                raise ValueError(
                    f"Duplicated template name: '{t}', found in service. "
                    "Template names must have unique names."
                )
            table_names.add(t)

    @property
    def table_names(self) -> List[str]:
        """The names of the tables accessible from this data source."""
        return list(itertools.chain(*self.all_templates_names.values()))

    def _validate_table_name(self, table_name: Optional[str] = None) -> None:
        """Validate the table name exists as a template in the Intermine service.

        Args:
            table_name: The name of the Intermine template.

        Raises:
            ValueError: If the data is multi-table but no table name provided.
            ValueError: If the table name is not found in the data.
            ValueError: If the database connection does not have any table names.
        """
        if table_name is None:
            raise ValueError("No table name provided for Intermine service.")
        elif not self.table_names:
            raise ValueError(f"Service {self.service} did not return any templates.")
        elif table_name not in self.table_names:
            raise ValueError(
                f"Template name {table_name} not found in service: {self.service}. "
                f"Available tables: {self.table_names}"
            )

    def get_values(
        self, col_names: List[str], table_name: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from list of columns.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.
            table_name: The name of the table to which the column exists. Required
                for multi-table databases.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.
        """
        output: Dict[str, Iterable[Any]] = {}
        if table_name:
            self._validate_table_name(table_name)

            data = self._template_to_df(table_name)
            for col_name in col_names:
                output[col_name] = data[col_name].unique()
        return output

    def get_column(
        self, col_name: str, table_name: Optional[str] = None, **kwargs: Any
    ) -> Union[np.ndarray, pd.Series]:
        """Get single column from dataset.

        Args:
            col_name: The name of the column which should be loaded.
            table_name: The name of the table to which the column exists. Required
                for multi-table databases.

        Returns:
            The column requested as a series.

        Raises:
            ValueError: If the data is multi-table but no table name provided.
            ValueError: If the table name is not found in the data.
        """
        if table_name:
            self._validate_table_name(table_name)
            data = self._template_to_df(table_name)

            return data[col_name]
        else:
            raise ValueError("Expected parameter: table_name.")

    def _template_to_df(self, template_name: str) -> pd.DataFrame:
        """Transform intermine template to pandas dataframe."""
        user = self.template_to_user_map[template_name]
        template = self.service.get_template_by_user(template_name, user)

        return pd.DataFrame(
            template.results(row="list"),
            columns=[col.replace(".", "_") for col in template.views],
        )

    def get_data(
        self, table_name: Optional[str] = None, **kwargs: Any
    ) -> Optional[pd.DataFrame]:
        """Loads and returns data from Intermine template.

        Args:
            table_name: Table name for multi table data sources. This
                comes from the DataStructure.

        Returns:
            A DataFrame-type object which contains the data.
        """
        data: Optional[pd.DataFrame] = None
        if table_name:
            self._validate_table_name(table_name)
            data = self._template_to_df(table_name)
        return data

    def get_dtypes(self, table_name: Optional[str] = None, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types of the Intermine template.

        Args:
            table_name: The name of the table_name which should be loaded. Only
                required for multitable database.

        Returns:
            A mapping from column names to column types.
        """
        self._validate_table_name(table_name)
        user = self.template_to_user_map[table_name]
        template = self.service.get_template_by_user(table_name, user)
        # intermine view_types are given in their java types
        java_dtypes = dict(zip(template.views, template.view_types))
        dtypes = {
            k.replace(".", "_"): _convert_python_dtypes_to_pandas_dtypes(
                INTERMINE_TYPE_MAPPING[v], k
            )
            for k, v in java_dtypes.items()
        }
        return dtypes

    def __len__(self) -> int:
        """Intemine template length."""
        return len(self.data)

    @property
    def multi_table(self) -> bool:
        """Attribute to specify whether the datasource is multi table."""
        if len(self.table_names) > 1:
            return True
        else:
            return False
