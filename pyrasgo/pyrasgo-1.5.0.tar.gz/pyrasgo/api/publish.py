"""
API Publish Functions
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Literal

import numpy as np
import pandas as pd

from pyrasgo import errors
from pyrasgo.primitives.dataset import Dataset, DS_PUBLISHED_STATUS
from pyrasgo.schemas.dataset import DatasetSourceType
from pyrasgo.utils import naming


class Publish:
    """
    API Publish Class
    """

    def __init__(self):
        from pyrasgo.api import Create, Get, Update
        from pyrasgo.api.connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.get = Get()
        self.create = Create()
        self.update = Update()
        self._dw = None

    @property
    def data_warehouse(self):
        from pyrasgo.storage import DataWarehouse, dw_connection

        if self._dw:
            return self._dw
        self._dw: DataWarehouse = dw_connection(self.api._dw_type())
        return self._dw

    def dataset(
        self,
        dataset: Dataset,
        name: str,
        resource_key: Optional[str] = None,
        description: Optional[str] = None,
        verbose: bool = False,
        time_index: str = None,
        attributes: Optional[dict] = None,
        table_type: Optional[str] = "VIEW",
        table_name: Optional[str] = None,
        generate_stats: bool = True,
        timeout: Optional[int] = None,
    ) -> Dataset:
        """
        Saves a transformed Dataset in Rasgo to published
        Args:
            dataset: Dataset to save
            name: Name of dataset
            resource_key: A table-safe key used to identify this dataset
            description: Description of dataset
            verbose: If true will print save progress status
            time_index: If the dataset is a time-series with a date column, pass the name of the date column here
            attributes: Dictionary with metadata about the Dataset
            table_type: Type of object to create in snowflake. Can be "TABLE" or "VIEW"
            table_name: Data Warehouse Table Name to set for this DS's published operation
            generate_stats: If True (default) will generate stats for dataset when published
            timeout: Approximate timeout in seconds. Raise an APIError if the dataset isn't available in x seconds
        """
        # Saving of previously-existing Datasets is not allowed
        if dataset._api_dataset:
            raise errors.RasgoRuleViolation(
                f"This Dataset already exists in Rasgo. {dataset}. Transform the dataset to save it."
            )
        if verbose:
            print(f"Saving Dataset with name={name!r} description={description!r} resource_key={resource_key}...")
        operation_set = dataset._get_or_create_op_set()
        if time_index:
            if attributes and "time_index" not in attributes:
                attributes["time_index"] = time_index
            elif attributes and "time_index" in attributes:
                raise errors.ParameterValueError(
                    message=f"Timeseries index explicitly defined as"
                    f" {time_index} in parameters, but defined as "
                    f"{attributes['time_index']} in attributes dict. "
                    f"Please choose to publish either in attributes or "
                    f"as a separate parameter, but not both."
                )
            else:
                attributes = {"time_index": time_index}

        dataset = self.create._dataset(
            name=name,
            source_type=DatasetSourceType.RASGO,
            resource_key=resource_key,
            description=description,
            status=DS_PUBLISHED_STATUS,
            dw_table_id=operation_set.operations[-1].dw_table_id,
            dw_operation_set_id=operation_set.id,
            attributes=attributes,
            publish_ds_table_type=table_type,
            publish_ds_table_name=table_name,
            generate_stats=generate_stats,
            timeout=timeout,
        )
        dataset = Dataset(api_dataset=dataset, api_operation_set=operation_set)
        if verbose:
            print(f"Finished Saving {dataset}")
        return dataset

    def dbt_project(
        self,
        datasets: List[Dataset],
        project_directory: Union[os.PathLike, str] = None,
        models_directory: Union[os.PathLike, str] = None,
        project_name: str = None,
        model_args: Dict[str, Any] = None,
    ) -> str:
        """
        Exports all given datasets to Models in a dbt Project

        Params:
        `datasets`: List[Dataset]:
            list of Rasgo datasets to write to dbt as models
        `project_directory`: Path:
            directory to save project files to
            defaults to current working dir
        `models_directory`: Path:
            directory to save model files to
            defaults to project_directory/models
        `project_name`: str:
            name for this project
            defaults to organization name
        """
        from pyrasgo.primitives import DbtProject
        from pyrasgo.utils.dbt import dataset_to_model, dataset_to_source

        project_directory = Path(project_directory or os.getcwd())
        project_name = project_name or naming.cleanse_dbt_name(self.api._profile["organization"]["name"])
        models_directory = Path(models_directory or (project_directory / "models"))
        project = DbtProject(
            name=project_name,
            project_directory=project_directory,
            models_directory=models_directory,
            models=[dataset_to_model(ds) for ds in datasets if not ds.is_source],
            sources=[dataset_to_source(ds) for ds in datasets if ds.is_source],
            model_args=model_args,
        )
        return project.save_files()

    def df(
        self,
        df: pd.DataFrame = None,
        name: Optional[str] = None,
        resource_key: Optional[str] = None,
        description: Optional[str] = None,
        dataset_table_name: str = None,  # TODO: Deprecate in future version
        parents: Optional[List[Dataset]] = None,
        verbose: bool = False,
        attributes: Optional[dict] = None,
        fqtn: Optional[str] = None,
        if_exists: Optional[Literal["append", "overwrite", "fail"]] = "fail",
        generate_stats: bool = True,
    ) -> Dataset:
        """
        Push a Pandas Dataframe a Data Warehouse table and register it as a Rasgo Dataset

        params:
            df: pandas DataFrame
            name: Optional name for the Dataset (if not provided a random string will be used)
            description: Optional description for this Rasgo Dataset
            dataset_table_name: Optional name for the target table (if not provided a random string will be used)
            parents: Set Parent Dataset dependencies for this df dataset. Input as list of dataset primitive objs.
            verbose: Print status statements to stdout while function executes if true
            attributes: Dictionary with metadata about the Dataset
            fqtn: Optional name for the target table (if not provided a random string will be used)
            if_exists: Values: ['fail', 'append', 'overwrite'] directs the function what to do if a FTQN is passed, and represents an existing Dataset
            generate_stats: If True (default) will generate stats for df dataset when published
        return:
            Rasgo Dataset
        """
        # Make sure no incompatible dw dtypes in df uploading
        _raise_error_if_bad_df_dtypes(df)

        # Validate all parent ds Ids exist if passed
        # Calling rasgo.get.dataset(<id>) will raise error if doesn't
        parents = parents if parents else []
        parent_ids = [ds.id for ds in parents]
        for p_ds_id in parent_ids:
            self.get.dataset(p_ds_id)

        if_exists_vals = ["overwrite", "append", "fail"]
        if_exists = if_exists.lower()
        if if_exists not in if_exists_vals:
            raise errors.ParameterValueError("if_exists", if_exists_vals)

        if dataset_table_name:
            print(
                "Param `dataset_table_name` will be deprecated in a future version. "
                "Pass `fqtn` to specify the target table for this df."
            )

        target_database, target_schema, target_table = naming.parse_fqtn(
            fqtn or dataset_table_name or naming.random_table_name(), self.api._default_dw_namespace()
        )
        target_fqtn = naming.make_fqtn(database=target_database, schema=target_schema, table=target_table)

        # Check for existing datasets matching FQTN
        ds = None
        try:
            ds = self.get.dataset(fqtn=target_fqtn)
            if ds and verbose:
                print(f"Found Dataset {ds.id} matching FQTN {target_fqtn}. Proceeding in {if_exists} mode.")
        except errors.RasgoResourceException:
            pass

        if ds and if_exists == "overwrite":
            # Users should only be able to overwrite datasets in their own organization
            if ds._api_dataset.organization_id != self.api._profile.get("organizationId"):
                raise errors.RasgoRuleViolation(
                    f"Dataset {ds.id} already exists. This API key does not have permission to replace it."
                )
        elif ds and if_exists == "fail":
            raise errors.ParameterValueError(
                message=f"FQTN {target_fqtn} already exists, and {if_exists} was passed for `if_exists`. "
                "Please confirm the FQTN or choose another value for `if_exists`"
            )

        # Write the df to the target table
        if verbose:
            verb = "Appending" if if_exists == "append" else "Writing"
            print(f"{verb} dataframe to target table {target_fqtn}")
        self.data_warehouse.write_dataframe_to_table(df, table_name=target_fqtn, method=if_exists)

        # Create dataset based on new table FQTN created from df
        if not ds:
            ds = self.table(
                fqtn=target_fqtn,
                name=name or target_fqtn,
                resource_key=resource_key,
                description=description,
                verbose=verbose,
                attributes=attributes,
                parents=parents,
                generate_stats=generate_stats,
                source_type=DatasetSourceType.DATAFRAME,
            )
        return ds

    def table(
        self,
        fqtn: str,
        name: Optional[str] = None,
        resource_key: Optional[str] = None,
        description: Optional[str] = None,
        parents: Optional[List[Dataset]] = None,
        verbose: bool = False,
        attributes: Optional[dict] = None,
        generate_stats: bool = True,
        timeout: Optional[int] = None,
        source_type: DatasetSourceType = DatasetSourceType.TABLE,
    ) -> Dataset:
        """
        Register an existing table as a Rasgo Dataset

        params:
            fqtn: The fully qualified table name of the table to register
            name: Optional name to apply to this Rasgo Dataset
            description: Optional description for this Rasgo Dataset
            parents: Set Parent Dataset dependencies for this table dataset. Input as list of dataset primitive objs.
            verbose: Print status statements to stdout while function executes if true
            attributes: Dictionary with metadata about the Dataset
            generate_stats: If True (default) will generate stats for table dataset when published
            timeout: Approximate timeout for creating the table in seconds. Raise an APIError if the reached
            source_type: Specifies the `source_type` of this Dataset in Rasgo. Defaults to 'TABLE'
        return:
            Rasgo Dataset
        """
        # Validate all parent ds Ids exist if passed
        # Calling rasgo.get.dataset(<id>) will raise error if doesn't
        parents = parents if parents else []
        parent_ids = [ds.id for ds in parents]
        for p_ds_id in parent_ids:
            self.get.dataset(p_ds_id)

        if verbose:
            print(f"Publishing {source_type.value} {fqtn} as Rasgo dataset")

        if fqtn.count(".") != 2:
            raise errors.ParameterValueError(
                message=f"'{fqtn}' is not a valid fully qualified table name. "
                "FQTNs should follow the format DATABASE.SCHEMA.TABLE_NAME.  "
                "Please pass a valid FQTN and try again"
            )

        table_database, table_schema, table_name = naming.parse_fqtn(fqtn)

        try:
            row_count = self.data_warehouse.query_into_dict(
                f"select count(1) as ROW_CT from {table_database}.{table_schema}.{table_name}"
            )
            if row_count[0]["ROW_CT"] == 0:
                raise errors.DWResourceException(
                    f"Source table {table_name} is empty or this role does not have access to it."
                )
        except Exception as err:
            raise errors.DWResourceException(
                f"Source table {table_name} does not exist or this role does not have access to it."
            ) from err

        # Make sure `source_type` param is valid Enum Value
        if not isinstance(source_type, DatasetSourceType):
            raise errors.ParameterValueError("source_type", ["CSV", "RASGO", "TABLE", "DATAFRAME"])

        # Check if a Dataset already exists
        existing_ds = None
        try:
            existing_ds = self.get.dataset(fqtn=fqtn)
        except errors.RasgoResourceException:
            pass
        if existing_ds:
            raise errors.RasgoResourceException(f"{fqtn} is already registered with Rasgo as Dataset {existing_ds.id}")

        # Create operation set with parent dependencies
        # set for this dataset
        operation_set = self.create._operation_set(
            operations=[],
            dataset_dependency_ids=parent_ids,
            async_compute=False,
        )

        # Publish Dataset with operation set created above
        dataset = self.create._dataset(
            name=name or table_name,
            source_type=source_type,
            resource_key=resource_key,
            description=description,
            fqtn=fqtn,
            status=DS_PUBLISHED_STATUS,
            attributes=attributes,
            dw_operation_set_id=operation_set.id,
            generate_stats=generate_stats,
            timeout=timeout,
        )
        # Raise API error if backend error creating dataset
        if not dataset:
            raise errors.APIError("DataSource failed to upload")

        # Return dataset if no error
        return Dataset(api_dataset=dataset)


# ------------------------------------------
#  Private Helper Funcs for Publish Class
# ------------------------------------------


def _raise_error_if_bad_df_dtypes(df: pd.DataFrame) -> None:
    """
    Raise an API error is any dtypes in the pandas dataframe,
    which are being pushed to the data warehouse aren't compatible.

    Raise proper error message if so
    """
    for col_name in df:
        col = df[col_name]
        if col.dtype.type == np.datetime64:
            raise errors.RasgoRuleViolation(
                "Can't publish pandas Df to Rasgo. Df column "
                f"'{col_name}' needs to be converted to proper datetime format.\n\n"
                "If your column is a **DATE** use `pd.to_datetime(df[<col_name>]).dt.date` to convert it\n"
                "If your column is a **TIMESTAMP** use `pd.to_datetime(final_df['col_name']).dt.tz_localize('UTC')`"
            )
