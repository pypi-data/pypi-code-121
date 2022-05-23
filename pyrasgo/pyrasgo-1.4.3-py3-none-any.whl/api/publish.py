import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from pyrasgo.primitives import Dataset
from pyrasgo.primitives.dataset import DS_PUBLISHED_STATUS
from pyrasgo.schemas.dataset import DatasetSourceType
from pyrasgo.storage.dataframe import utils as df_utils
from pyrasgo.utils import naming
from .error import APIError, ParameterValueError


class Publish:
    def __init__(self):
        from pyrasgo.config import get_session_api_key

        from . import Create, Get, Update
        from .connection import Connection

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.get = Get()
        self.create = Create()
        self.update = Update()
        self._dw = None

    @property
    def data_warehouse(self):
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        if self._dw:
            return self._dw
        self._dw: SnowflakeDataWarehouse = DataWarehouse.connect()
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
            raise APIError(f"This Dataset already exists in Rasgo. {dataset}. Transform the dataset to save it.")
        if verbose:
            print(f"Saving Dataset with name={name!r} description={description!r} resource_key={resource_key}...")
        operation_set = dataset._get_or_create_op_set()
        if time_index:
            if attributes and "time_index" not in attributes:
                attributes["time_index"] = time_index
            elif attributes and "time_index" in attributes:
                raise ValueError(
                    f"Timeseries index explicitly defined as"
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
        dataset_table_name: str = None,
        parents: Optional[List[Dataset]] = None,
        verbose: bool = False,
        attributes: Optional[dict] = None,
        fqtn: Optional[str] = None,
        if_exists: Optional[str] = None,
        generate_stats: bool = True,
    ) -> Dataset:
        """
        Push a Pandas Dataframe a Data Warehouse table and register it as a Rasgo Dataset

        params:
            df: pandas DataFrame
            name: Optional name for the Dataset (if not provided a random string will be used)
            description: Optional description for this Rasgo Dataset
            dataset_table_name: Optional name for the Dataset table in Snowflake (if not provided a random string will be used)
            parents: Set Parent Dataset dependencies for this df dataset. Input as list of dataset primitive objs.
            verbose: Print status statements to stdout while function executes if true
            attributes: Dictionary with metadata about the Dataset
            fqtn: If appending to an existing table via DataFrame, include the Fully Qualified Table Name here
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

        if if_exists and if_exists.lower() not in if_exists_vals:
            raise ParameterValueError("if_exists", if_exists_vals)

        if fqtn and fqtn.count(".") != 2:
            raise ValueError(
                f"'{fqtn}' is not a valid fully qualified table name. "
                f"FQTNs should follow the format DATABASE.SCHEMA.TABLE_NAME.  "
                f"Please pass a valid FQTN and try again"
            )

        if if_exists and not fqtn:
            raise ValueError(
                f"`if_exists` passed as '{if_exists}', but no FQTN was passed. "
                "In order to amend an existing Dataset, please pass the FQTN "
                "of that dataset"
            )

        if verbose:
            print("Publishing df as Rasgo dataset")

        if fqtn:
            db_name, schema_name, table_name = fqtn.split(".")
            # Get dataset matching FQTN
            ds = self.get.dataset(fqtn=fqtn)
            if verbose:
                print(f"Found Dataset {ds.id} matching FQTN {fqtn}")

            # If no Dataset matching the FQTN, fail and warn
            if not ds:
                raise ValueError(f"Dataset with FQTN {fqtn} not found. Please confirm FQTN.")
            else:
                if if_exists and if_exists.lower() == "overwrite":
                    # Users should only be able to overwrite datasets in their own organization
                    if ds._api_dataset.organization_id != self.api._profile.get("organizationId"):
                        raise APIError(
                            f"Dataset {ds.id} already exists. This API key does not have permission to replace it."
                        )
                    self.data_warehouse.write_dataframe_to_table(df, table_name=table_name, append=False)
                    if verbose:
                        print(f"Dataset {ds.id} with FQTN {fqtn} successfully overwritten")
                elif if_exists and if_exists.lower() == "append":
                    self.data_warehouse.write_dataframe_to_table(df, table_name=table_name, append=True)
                    if verbose:
                        print(f"Data successfully appended to Dataset {ds.id} with FQTN {fqtn}")
                elif if_exists and if_exists.lower() == "fail":
                    raise ValueError(
                        f"FQTN {fqtn} already exists, and {if_exists} was passed for `if_exists`. "
                        "Please confirm the FQTN or choose another value for `if_exists`"
                    )

                self.data_warehouse.grant_table_ownership(
                    table=table_name, role=self.data_warehouse.publisher_role, database=db_name, schema=schema_name
                )
                self.data_warehouse.grant_table_access(
                    table=table_name, role=self.data_warehouse.reader_role, database=db_name, schema=schema_name
                )

            # return the dataset we have
            return ds
        else:
            _org_defaults = self.api._get_default_namespace()
            table_name = (dataset_table_name or naming.random_table_name()).upper()
            name = name or table_name
            table_database = _org_defaults.get('database')
            table_schema = _org_defaults.get('schema')
            naming_fqtn = naming.make_fqtn(table=table_name, database=table_database, schema=table_schema)

            df_utils.cleanse_sql_dataframe(df)
            self.data_warehouse.write_dataframe_to_table(df, table_name=table_name, append=False)
            self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

            # Create dataset based on new table FQTN created from df
            dataset = self.table(
                fqtn=naming_fqtn,
                name=name,
                resource_key=resource_key,
                description=description,
                verbose=verbose,
                attributes=attributes,
                parents=parents,
                generate_stats=generate_stats,
                source_type=DatasetSourceType.DATAFRAME,
            )
        if verbose:
            print("Done publishing df as Rasgo dataset")
        return dataset

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
            print("Publishing table as Rasgo dataset")

        if fqtn.count(".") != 2:
            raise ValueError(
                f"'{fqtn}' is not a valid fully qualified table name. "
                "FQTNs should follow the format DATABASE.SCHEMA.TABLE_NAME.  "
                "Please pass a valid FQTN and try again"
            )

        table_database, table_schema, table_name = fqtn.split('.')

        try:
            src_table = self.data_warehouse.get_source_table(
                table_name=table_name,
                database=table_database,
                schema=table_schema,
                record_limit=10,
            )
            if src_table.empty:
                raise APIError(f"Source table {table_name} is empty or this role does not have access to it.")
        except Exception:
            raise APIError(f"Source table {table_name} does not exist or this role does not have access to it.")

        # Make sure `source_type` param is valid Enum Value
        if not isinstance(source_type, DatasetSourceType):
            raise ValueError(
                "Param `source_type` must be a valid enum member from `pyrasgo.schemas.dataset.DatasetSourceType`"
            )

        # TODO: Re-implement when search by fqtn is available. For now, we'll trust the API to enforce uniqueness on fqtns
        # Check if a Dataset already exists
        # dataset = self.match.dataset(fqtn=fqtn)
        # if dataset:
        #     raise APIError(f"Dataset {dataset.id} already exists in Rasgo")

        # NOTE: grant_table_access is intentional here
        # In other methods, we create a table with the rasgo user role and want to hand if off to the reader role
        # In this case, the table is likely part of a pre-existing rbac model and we just want to grant rasgo access
        self.data_warehouse.grant_table_access(
            table=table_name,
            role=self.data_warehouse.reader_role,
            database=table_database,
            schema=table_schema,
        )

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
            raise APIError("DataSource failed to upload")

        # Return dataset if no error
        if verbose:
            print("Done publishing table as Rasgo dataset")
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
            raise APIError(
                "Can't publish pandas Df to Rasgo. Df column "
                f"'{col_name}' needs to be converted to proper datetime format.\n\n"
                "If your column is a **DATE** use `pd.to_datetime(df[<col_name>]).dt.date` to convert it\n"
                "If your column is a **TIMESTAMP** use `pd.to_datetime(final_df['col_name']).dt.tz_localize('UTC')`"
            )
