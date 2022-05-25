"""
Dataset 'Primitive' In Rasgo SDK
"""
from __future__ import annotations
import functools
import inspect
from datetime import datetime
from inspect import Parameter
from typing import Callable, Dict, List, Optional, Tuple, Union

import pandas as pd

from pyrasgo.schemas import (
    OperationSet,
    Dataset as DatasetSchema,
    OperationCreate,
    Transform,
    DatasetBulk,
    DatasetColumn,
    DatasetSourceType,
)
from pyrasgo.api.connection import Connection
from pyrasgo.storage.datawarehouse.base import DataWarehouse
from pyrasgo.storage.datawarehouse.snowflake import SnowflakeDataWarehouse
from pyrasgo.utils import naming, polling, rendering


# Value of dataset.status if dataset is published
DS_PUBLISHED_STATUS = 'published'

# Name of required source table arg we auto populate
SOURCE_TABLE_ARG_NAME = 'source_table'

# Transform Arg Types which expect DS inputs
# should contain Datasets Objs
TABLE_ARG_TYPE = 'table'
TABLE_LIST_ARG_TYPE = 'table_list'


def require_published(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self: Dataset = args[0]
        self._assert_is_published()
        return func(*args, **kwargs)

    return wrapper


def require_operation_set(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self: Dataset = args[0]
        self._require_operation_set()
        return func(*args, **kwargs)

    return wrapper


class Dataset(Connection):
    """
    Representation of a Rasgo Dataset
    """

    def __init__(
        self,
        # Args passed from Rasgo
        api_dataset: Optional[DatasetSchema] = None,
        api_operation_set: Optional[OperationSet] = None,
        # Args passed from transforming
        operations: Optional[List[OperationCreate]] = None,
        dataset_dependencies: Optional[List[int]] = None,
        table_name: Optional[str] = None,
        transforms: Optional[List[Transform]] = None,
        verbose=False,
        async_compute: Optional[bool] = True,  # TODO: Remove before next major version
        **kwargs: Dict,
    ):
        """
        Init functions in two modes:
            1. This Dataset retrieved from Rasgo. This object is for reference, and cannot
               be changed, but can be transformed to build new datasets
            2. This Dataset represents a new dataset under construction. It is not persisted in Rasgo
               and instead consists of some operations that will be used to generate a new dataset.
        """
        super().__init__(**kwargs)

        self._verbose = verbose
        self._api_dataset: DatasetSchema = api_dataset
        self._api_operation_set: OperationSet = api_operation_set
        self._operations = operations if operations else []
        self._dataset_dependencies = dataset_dependencies if dataset_dependencies else []
        self._table_name = table_name
        self._source_code_preview = None
        if transforms:
            self._available_transforms = transforms
        else:
            self._available_transforms = _get_transforms()
        self._async_compute = async_compute

        #  alias .transform allowing direct referencing of named transforms
        for transform in self._available_transforms:
            f = self._create_transform_function(transform)
            setattr(self, transform.name, f)

    def __repr__(self) -> str:
        """
        Get string representation of this dataset
        """
        if self._api_dataset:
            return (
                f"Dataset(id={self.id}, "
                f"name={self.name}, "
                f"resource_key={self._api_dataset.resource_key}, "
                f"version={self._api_dataset.version}, "
                f"status={self.status}, "
                f"description={self.description})"
            )
        else:
            return "Dataset()"

    # -------------------
    # Properties
    # -------------------

    @property
    def id(self) -> Optional[int]:
        """
        Return the id for this dataset

        Raise API error if one doesn't exist yet and is an offline dataset
        """
        if self._api_dataset:
            return self._api_dataset.id

    @property
    def name(self) -> Optional[str]:
        """
        Return dataset name if set/saved
        """
        if self._api_dataset:
            return self._api_dataset.name

    @property
    def description(self) -> Optional[str]:
        """
        Return dataset description if set/saved
        """
        if self._api_dataset:
            return self._api_dataset.description

    @property
    def status(self) -> Optional[str]:
        """
        Return dataset status
        """
        if self._api_dataset:
            return self._api_dataset.status

    @property
    def fqtn(self) -> str:
        """
        Returns the Fully Qualified Table Name for this dataset
        """
        if self._api_dataset and self._api_dataset.dw_table:
            return self._api_dataset.dw_table.fqtn
        elif self._table_name:
            dw_namespace = self._get_default_namespace()
            return f"{dw_namespace['database']}.{dw_namespace['schema']}.{self._table_name}".upper()
        else:
            raise AttributeError("No data warehouse fqtn exists for this Dataset")

    @property
    def table_type(self) -> Optional[str]:
        """
        If this is a published dataset, return the
        table type for it's set Dw Table ( 'VIEW' or 'TABLE')
        """
        if self._api_dataset and self._api_dataset.dw_table:
            return self._api_dataset.dw_table.table_type

    @property
    def columns(self) -> Optional[List[DatasetColumn]]:
        """
        Return the columns for this dataset if it is from the API
        """
        if self._api_dataset:
            # If the dataset was from bulk `rasgo.get.datasets()`
            # it won't have dataset columns, so make API call
            # to retrieve them.
            if self._api_dataset.columns is None:
                from pyrasgo.api import Get

                self._api_dataset.columns = Get()._dataset_columns(self.id)

            return self._api_dataset.columns

    @property
    def resource_key(self) -> Optional[str]:
        """
        Return the resource key for this dataset.

        Only published datasets will contain this value
        """
        if self._api_dataset:
            return self._api_dataset.resource_key

    @property
    def created_date(self) -> Optional[datetime]:
        """
        Return date this dataset was created
        """
        if self._api_dataset:
            return self._api_dataset.create_timestamp

    @property
    def update_date(self) -> Optional[datetime]:
        """
        Return date this dataset was updated
        """
        if self._api_dataset:
            return self._api_dataset.update_timestamp

    @property
    def attributes(self) -> Optional[Dict]:
        """
        Return the attributes for this dataset if it is from the API
        """
        if self._api_dataset:
            return self._api_dataset.attributes

    @property
    def source_type(self) -> Optional[str]:
        """
        Return dataset source type if set on published Dataset

        All offline datasets are of type `RASGO`
        """
        if self._api_dataset:
            return self._api_dataset.source_type.value
        else:
            return DatasetSourceType.RASGO.value

    @property
    def is_source(self) -> bool:
        """
        Is this Dataset a standalone source? i.e. does it have no applied operations?
        Sources are imported from csvs, dataframes or directly from Snowflake tables

        This property is a convenience calc to support exporting Datasets to dbt
        """
        if self._api_dataset:
            return self._api_dataset.is_source

    @property
    def dependencies(self) -> List[Dataset]:
        """
        Return a list of dataset dependencies for this dataset
        """
        from pyrasgo.api import Get

        get = Get()
        dataset_deps = []
        self._cache_op_set_from_api()
        if self._api_operation_set:
            for ds in self._api_operation_set.dataset_dependencies:
                dataset_deps.append(get.dataset(ds.id))
        else:
            get = Get()
            for ds_id in self._dataset_dependencies:
                dataset_deps.append(get.dataset(ds_id))
        return dataset_deps

    @property
    @require_operation_set
    def sql(self) -> Optional[str]:
        """
        Return the source code SQL used to generate this dataset
        """
        # Raise error if no operations/source code for this dataset yet
        has_operations = not hasattr(self._api_operation_set, "operations") or (not self._api_operation_set.operations)
        if has_operations and not self._source_code_preview:
            return
        if self._api_dataset:
            return '\n\n'.join([x.operation_sql for x in self._api_operation_set.operations])
        else:
            return self._source_code_preview

    @property
    def snapshots(self) -> Optional[list]:
        """return a list of tuples of timestamp identified by index and the snapshot creation timestamp"""
        return [(i + 1, ss.timestamp) for i, ss in enumerate(self._api_dataset.snapshots)]

    @property
    def versions(self) -> List[DatasetBulk]:
        """return a list of versions of this dataset"""
        return self._get(
            f"datasets/rk/{self._api_dataset.resource_key}/versions",
            api_version=2,
        ).json()

    @property
    def schema(self):
        if self._api_dataset:
            data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
            return data_warehouse.get_schema(self._api_dataset.dw_table.fqtn)

    # --------
    # Methods
    # --------

    def transform(
        self,
        transform_name: str,
        arguments: Optional[Dict[str, Union[str, int, List, Dict, Dataset]]] = None,
        operation_name: Optional[str] = None,
        async_compute: Optional[bool] = True,
        render_only: Optional[bool] = False,
        **kwargs: Union[str, int, List, Dict, Dataset],
    ) -> Union[Dataset, None]:
        """
        Transform a new dataset with the given transform and arguments.
        Created operation is added to the dataset's canvas/operations set

        Args:
            transform_name: Name of transform to Apply
            arguments: Optional transform arguments sin not supplied by **kwargs
            operation_name: Name to set for the operation/transform
            render_only: Optional flag to simply render the operation that will result
                from this transformation instead of using it to create a new Dataset.
            **kwargs:

        Returns:
             Returns an new dataset with the referenced transform
             added to this dataset's definition/operation set

             Optionally, can be used to try out some inputs to a transform by passing `render_only = True`
        """
        # Update the Transform arguments with any supplied kwargs
        arguments = arguments if arguments else {}
        arguments.update(kwargs)

        # Do any validation on input transform args
        transform = self._get_transform_by_name(transform_name)
        _assert_value_types_of_args(transform, arguments, self)

        # Add required reference to self in transform
        arguments[SOURCE_TABLE_ARG_NAME] = self

        # Scan through supplied transform arguments
        #
        # Determine what should be set for this operation's plus offline dataset's
        # dependencies, along with getting the parent operations for this operation
        # by reading data from input Datasets obj attribute data
        #
        # We also convert 'Datasets' to fqtns in the arguments dict in
        # the func below
        op_deps, ds_deps, parent_ops, arguments = self._get_op_deps_parents_and_args(arguments)

        # Init table name for outputted dataset
        table_name = naming.gen_operation_table_name(
            op_num=len(parent_ops) + 1,
            transform_name=transform_name,
        )

        # Init New Operation Create Contract
        operation_create = OperationCreate(
            operation_name=operation_name if operation_name else transform.name,
            operation_args=arguments,
            transform_id=transform.id,
            table_name=table_name,
            table_dependency_names=op_deps,
        )

        # If rendering only, short circuit and get the SQL we'll
        # render for this operation
        if render_only:
            from pyrasgo.api import Create

            print(Create()._operation_render(operation_create))
            return None

        # Init and return new offline dataset
        return self.__class__(
            operations=parent_ops + [operation_create],
            dataset_dependencies=ds_deps,
            table_name=table_name,
            async_compute=async_compute,
        )

    @require_operation_set
    def to_df(
        self,
        filters: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        snapshot_index: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Reads and returns this dataset into a pandas dataframe

        You can supply SQL WHERE clause filters, order the dataset by columns, only
        return selected columns, and add a return limit as well

        Example:
            ```
            ds = rasgo.get.dataset(dataset_id=74)
            ds.to_df(
                filters=['SALESTERRITORYKEY = 1', 'TOTALPRODUCTCOST BETWEEN 1000 AND 2000'],
                order_by=['TOTALPRODUCTCOST'],
                columns=['PRODUCTKEY', 'TOTALPRODUCTCOST', 'SALESTERRITORYKEY'],
                limit=50
            )
            ```

        Args:
            filters: List of SQL WHERE filters strings to filter on returned df
            order_by: List of columns to order by in returned dataset
            columns: List of columns to return in the df
            limit: Only return this many rows in the df
            snapshot_index: the index of a snapshot from Dataset.snapshots to read
        """
        from pyrasgo.api import Read

        return Read().dataset(
            dataset=self,
            filters=filters,
            order_by=order_by,
            columns=columns,
            limit=limit,
            snapshot_index=snapshot_index - 1 if snapshot_index else None,
        )

    def preview(
        self,
        filters: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Preview the first 10 rows of this dataset, returned as pandas dataframe

        You can supply SQL WHERE clause filters, order the dataset by columns, and
        only return selected columns

        Example:
            ```
            ds = rasgo.get.dataset(dataset_id=74)
            ds.preview(
                filters=['SALESTERRITORYKEY = 1', 'TOTALPRODUCTCOST BETWEEN 1000 AND 2000'],
                order_by=['TOTALPRODUCTCOST'],
                columns=['PRODUCTKEY', 'TOTALPRODUCTCOST', 'SALESTERRITORYKEY']
            )
            ```

        Args:
            filters: List of SQL WHERE filters strings to filter on returned df
            order_by: List of columns to order by in returned dataset
            columns: List of columns to return in the df
        """
        return self.to_df(filters, order_by, columns, limit=10)

    def generate_yaml(self) -> str:
        """
        Return a YAML representation of this dataset
        """
        from pyrasgo.api import Get

        if not self._api_dataset or not self._api_dataset.dw_table_id:
            raise AttributeError("Dataset must be created in Rasgo first to generate a YAML for this dataset")
        return Get().dataset_yaml(self.id)

    def generate_py(self) -> str:
        """
        Generate and return as a string the PyRasgo code which
        will create an offline a copy of this dataset whether DS
        is in draft or unpublished status.

        Dataset must be created in Rasgo first first before you can call this func.
        """
        from pyrasgo.api import Get

        if not self._api_dataset:
            raise AttributeError("Dataset must be created in Rasgo first to generate the PyRasgo code for this dataset")
        return Get().dataset_py(self.id)

    # -----------------------------------------------------
    # Methods requiring dataset to be registered with Rasgo
    # -----------------------------------------------------

    def _refresh(self) -> None:
        """
        Refresh this Dataset's metadata from the Rasgo API
        """
        if self._api_dataset:
            self._api_dataset = DatasetSchema(**self._get(f"/datasets/{self.id}", api_version=2).json())

    def dw_sync(self) -> None:
        """
        Looks up the schema of this Dataset's table in the DataWarehouse and synchronizes
        the Dataset's column metadata to match it

        Helpful to pick up common changes:
        - new fields added to table
        - existing fields removed from table
        - data type changes

        Does not pick up:
        - table renames
        - column renames
        """
        from pyrasgo.api import Update

        if self._api_dataset:
            Update().dataset_schema(self.id)
            self._refresh()

    def profile(self) -> any:
        """
        Get the URL for this Dataset in the RasgoUI
        """
        if not self.id:
            raise AttributeError("This dataset has not been created")

        from pyrasgo.api.session import Environment

        return f"{Environment.from_environment().app_path}/datasets/{self.id}/canvas"

    def run_stats(self, only_if_data_changed: Optional[bool] = True) -> None:
        """
        Trigger new stats for this dataset

        Args:
            only_if_data_changed: Use False to tell Rasgo to run stats even if the data has not changed
        """
        if not self._api_dataset or not self._api_dataset.dw_table_id:
            raise AttributeError("Dataset must be created and have an output selected in order to generate stats")
        from pyrasgo.api.create import Create

        create = Create()

        table_id = self._api_dataset.dw_table_id

        create._dataset_correlation_stats(table_id=table_id, only_if_data_changed=only_if_data_changed)
        print(
            f"Request to generate stats for Dataset {self.id} started. Once generated, view stats at {self.profile()}"
        )

    def refresh_table(self, verbose: bool = False, timeout: Optional[int] = None) -> None:
        """
        Kicks off a query for re-materializing this dataset's set Dw Table.

        The dataset needs to be published first in order call this function

        Args:
            verbose: If True will print information related to refreshing table
            timeout: Approximate timeout for creating the table in seconds.
                     Raise an APIError if timeout reached
        """
        from pyrasgo.api.update import Update

        Update().dataset_table(dataset=self, verbose=verbose, timeout=timeout)

    def to_sql(self) -> Optional[str]:
        """
        Return the SQL statement to create this dataset
        """
        sql = self._get_cte_for_dataset()
        return f"CREATE OR REPLACE {self.table_type} {self.fqtn} AS {sql}"

    def to_accelerator(self) -> Optional[str]:
        if self._api_dataset:
            from pyrasgo.utils import exports

            return exports.dataset_to_accelerator_yaml(dataset=self)

    # ---------------------------------
    #  Private Helper Funcs for Class
    # ---------------------------------

    @require_operation_set
    def _get_cte_for_dataset(self) -> str:
        """
        Return the SQL statement to create this dataset as a CTE
        """
        # If we have operations, use those. Otherwise this is a raw imported table and we have to just do a select.
        return (
            rendering.operations_as_cte(self._api_operation_set.operations)
            if self._api_operation_set.operations
            else f'SELECT * FROM {self._api_dataset.dw_table.fqtn}'
        )

    def _get_transform_by_name(self, transform_name: str) -> Transform:
        """
        Get and return a transform obj by name

        Raise Error if no transform with that name found
        """
        for transform in self._available_transforms:
            if transform_name == transform.name:
                return transform
        raise ValueError(f"No Transform with name '{transform_name}' available to your organization")

    def _assert_can_transform(self) -> None:
        """
        Raise an API error if you can't transform this dataset
        """
        if self._api_dataset:
            if not self._api_dataset.dw_table_id or self.status != DS_PUBLISHED_STATUS:
                raise AttributeError(
                    f"Dataset({self._api_dataset.id}) has not been locked/published, "
                    f"and cannot be used as an arg for new dataset transformations"
                )

    def _assert_is_published(self) -> None:
        """
        Raise an error if the dataset is not published
        """
        if self.status != DS_PUBLISHED_STATUS:
            raise AttributeError(
                "Dataset must be published in order to perform this action. Please publish your dataset to continue."
            )

    def _require_operation_set(self) -> None:
        """
        This function used to ensure that an operation set exists for a given dataset before
        attempting to do any operations that require the operations to exist in Rasgo (for example,
        previewing tables before they actually exist)

        If the operation set does not exist, AND the set of operations to be created does,
        create temp operations so the tables exists.

        NOTE: If this is a 'offline'/transformed dataset, the endpoint hit
        doesn't do everything to create a full working OP set for the UI for
        speed performance reason, just a temp one; Just enough so can preview
        datasets/source code. Call  `self._get_or_create_op_set()`
        to create the full working op set for UI and more
        """
        # If the dataset is from the API and it has a
        # op set, get and cache it if not done so yet
        if self._api_dataset:
            self._cache_op_set_from_api()

        # If this is a transformed/'offline' dataset create temp op set
        # and set source code preview
        if not self._source_code_preview and self._operations:
            from pyrasgo.api.create import Create

            if self._async_compute:
                task = Create()._operation_set_preview_async(
                    operations=self._operations,
                    dataset_dependency_ids=self._dataset_dependencies,
                )
                self._source_code_preview = polling.poll_operation_set_offline_async_status(task)
            else:
                self._source_code_preview = Create()._operation_set_preview(
                    operations=self._operations,
                    dataset_dependency_ids=self._dataset_dependencies,
                )

    def _cache_op_set_from_api(self) -> None:
        """
        If this dataset is from the API, and it's op set is not cached
        yet do so
        """
        if self._api_dataset:
            if not self._api_operation_set and self._api_dataset.dw_operation_set_id:
                from pyrasgo.api import Get

                self._api_operation_set = Get()._operation_set(self._api_dataset.dw_operation_set_id)

    def _get_or_create_op_set(self) -> OperationSet:
        """
        Get or create plus return the operation set for this dataset
        """
        # If the dataset is from the API and it has a
        # op set, get and cache it if not done so yet
        if self._api_dataset:
            self._cache_op_set_from_api()

        # If the dataset doesn't have a op set in the API, or
        # it is a 'offline' transformed dataset create the op
        # set if not done so on this dataset yet
        if not self._api_operation_set:
            from pyrasgo.api.create import Create

            self._api_operation_set = Create()._operation_set(
                operations=self._operations,
                dataset_dependency_ids=self._dataset_dependencies,
                async_compute=self._async_compute,
                async_verbose=self._verbose,
            )

        return self._api_operation_set

    def _create_transform_function(self, transform: Transform) -> Callable:
        """
        Creates and returns a new function to dynamically attached to the Dataset obj on init

        New funcs docstring, name, and signature (params shown when inspecting/doing . tab on func)
        as well to improve notebook experience of using transforms for users

        Args:
            ds_transform_func: Function pointer of Dataset.transform()
            transform: Transform to read metadata and create new function for
        """

        # Create new function with 'transform_name` param set to this transform's name
        def f(*args, **kwargs) -> Dataset:
            return self.transform(transform_name=transform.name, *args, **kwargs)

        # Update func meta data for better inspection in notebook
        f.__name__ = transform.name
        f.__signature__ = _gen_func_signature(f, transform)
        f.__doc__ = _gen_func_docstring(transform)
        return f

    def _get_op_deps_parents_and_args(
        self,
        arguments: Dict[str, Union[str, int, List, Dict, Dataset]],
    ) -> Tuple[List[str], List[int], List[OperationCreate], Dict[str, Union[str, int, List, Dict, Dataset]]]:
        """
        Based on the input arguments a user supplied for this transform,
        determine and return a many things needed to initialize the next
        offline dataset. This includes
          - Operation Dependencies as list of FQTNs
          - Dataset Dependencies as list of unique dataset ids
          - List of parent operations for the next offline dataset
          - Updated args dict with Dataset objs converted to FQTN stings

        Args:
            arguments: The arguments a user supplied to the transform. This includes
                       'source_table' value we auto-populate

        Returns:
            Tuple of things needed to create next offline dataset
        """
        # Make copy of supplied transform arguments
        # since modifying in function
        arguments = arguments.copy()

        # Init lists to keep track of this operation's deps,
        # parent operations along with op set dependencies
        op_deps = []
        parent_ops = []
        ds_deps = self._dataset_dependencies.copy()

        # Always handle the `source_table` first to keep proper
        # order of parent operations
        source_table: Dataset = arguments.pop(SOURCE_TABLE_ARG_NAME)
        op_deps, parent_ops, ds_deps = self._update_op_deps__ds_deps__and_parent_ops(
            ds_arg=source_table, op_deps=op_deps, parent_ops=parent_ops, ds_deps=ds_deps
        )
        arguments[SOURCE_TABLE_ARG_NAME] = source_table.fqtn

        # Loop through arguments supplied to the transform
        # includes 'source_table' self set Dataset Param
        for arg_name, arg_val in arguments.items():

            # If supplied arg value is a Dataset, update deps
            # and convert arg to fqtn in args dict
            if isinstance(arg_val, self.__class__):
                op_deps, parent_ops, ds_deps = self._update_op_deps__ds_deps__and_parent_ops(
                    ds_arg=arg_val, op_deps=op_deps, parent_ops=parent_ops, ds_deps=ds_deps
                )
                arguments[arg_name] = arg_val.fqtn

            # If supplied arg value is a List, check if any elements in
            # the List are 'Datasets'. If so update deps and convert
            # arg to fqtn in args dict
            elif isinstance(arg_val, list):
                for i, possible_dataset in enumerate(arg_val):
                    if isinstance(possible_dataset, self.__class__):
                        op_deps, parent_ops, ds_deps = self._update_op_deps__ds_deps__and_parent_ops(
                            ds_arg=possible_dataset, op_deps=op_deps, parent_ops=parent_ops, ds_deps=ds_deps
                        )
                        arguments[arg_name][i] = possible_dataset.fqtn

            # If supplied arg value is a Dict, check if any elements in
            # the Dict values are 'Datasets'. If so update deps and
            # convert arg to fqtn in args dict
            elif isinstance(arg_val, dict):
                for key, possible_dataset in arg_val.items():
                    if isinstance(possible_dataset, self.__class__):
                        op_deps, parent_ops, ds_deps = self._update_op_deps__ds_deps__and_parent_ops(
                            ds_arg=possible_dataset, op_deps=op_deps, parent_ops=parent_ops, ds_deps=ds_deps
                        )
                        arguments[arg_name][key] = possible_dataset.fqtn

        # Return op deps, ds deps, parent ops, and updated arguments
        return op_deps, list(set(ds_deps)), parent_ops, arguments

    @staticmethod
    def _update_op_deps__ds_deps__and_parent_ops(
        ds_arg: Dataset, op_deps: List[str], parent_ops: List[OperationCreate], ds_deps: List[int]
    ) -> Tuple[List[str], List[OperationCreate], List[int]]:
        """
        Return updated DS args, deps, and op deps if arg to transform is type Dataset
        """
        op_deps = op_deps.copy()
        parent_ops = parent_ops.copy()
        ds_deps = ds_deps.copy()

        # Add input DS as operation dependency
        op_deps.append(ds_arg.fqtn)

        # If the dataset from the API, make sure is published
        # and has a respective DWTable. If so update dataset deps
        if ds_arg._api_dataset:
            ds_arg._assert_can_transform()
            ds_deps.append(ds_arg._api_dataset.id)
        # If it's an offline dataset, grab it's operations to set
        # as parents to output DS operations.
        # We need to make sure we aren't adding the same operation twice as well
        else:
            for ds_op in ds_arg._operations:
                if ds_op not in parent_ops:
                    parent_ops.append(ds_op)

        return op_deps, parent_ops, ds_deps


def _assert_value_types_of_args(
    transform: Transform,
    supplied_args: List[Dict[str, Union[str, int, List, Dict, Dataset]]],
    base_dataset: Dataset,
) -> None:
    """
    Raise TypeError if any of the supplied arguments are are not a valid type

    We especially need this to make sure args which expect datasets
    are ds objs and not fqtns, so we can add dependencies properly

    TODO: Add validation on other data types like `int_list`

    Args:
        transform: Transform applying
        supplied_args: Arguments of the supplied transform
        base_dataset: The base dataset which we're transforming
                      this is needed we can do `isinstance(arg, dataset.__class__)`
    """
    for transform_arg in transform.arguments:
        # We don't want to assert transform arguments
        # that are optional but not supplied, so skip
        # if not in user supplied args dict
        if transform_arg.name in supplied_args:
            supplied_arg_val = supplied_args[transform_arg.name]

            # If argument expects type 'table'
            # raise ValueError if not of type Dataset
            if transform_arg.type == TABLE_ARG_TYPE:
                if not isinstance(supplied_arg_val, base_dataset.__class__):
                    raise TypeError(
                        f"The {transform.name}() transform's parameter "
                        f"{transform_arg.name!r} requires the value to be "
                        f"a single Dataset obj. Got {type(supplied_arg_val)} instead"
                    )

            # If argument expects type 'table_list'
            # raise ValueError if not of type List[Dataset]
            elif transform_arg.type == TABLE_LIST_ARG_TYPE:
                if not isinstance(supplied_arg_val, list) or any(
                    [not isinstance(x, base_dataset.__class__) for x in supplied_arg_val]
                ):
                    raise TypeError(
                        f"The {transform.name}() transform's parameter "
                        f"{transform_arg.name!r} requires the value to "
                        "be a non-empty list of Dataset objs."
                    )


def _get_transforms() -> List[Transform]:
    """
    Get and set available transforms from the API to be used
    directly as functions of Dataset if not retrieved yet
    """
    # Get available transforms from the API to be used directly as functions of Dataset
    from pyrasgo.api import Get

    try:
        return Get().transforms()
    except Exception:
        print('Unable to fetch available transforms from Rasgo.  Will not be able to transform this Dataset')
        return []


def _gen_func_signature(func: Callable, transform: Transform) -> inspect.Signature:
    """
    Creates and returns a transform param signature.

    This is shown documentation for the parameters when hitting shift tab in a notebook
    """
    # Get current signature of function
    sig = inspect.signature(func)

    # Create Signature Params for Transform Args
    transform_params = []
    for t_arg in transform.arguments:
        p = Parameter(name=t_arg.name, kind=Parameter.KEYWORD_ONLY)
        transform_params.append(p)

    # Add `operation_name` param as last in signature with type annotation
    op_name_param = Parameter(
        name='operation_name',
        kind=Parameter.KEYWORD_ONLY,
        annotation=Optional[str],
        default=None,
    )
    transform_params.append(op_name_param)

    # Return new signature
    return sig.replace(parameters=transform_params)


def _gen_func_docstring(transform: Transform) -> str:
    """
    Generate and return a docstring for a transform func
    with transform description, args, and return specified.
    """
    # Have start of docstring be transform description
    docstring = f"\n{transform.description}"

    # Add transform args to func docstring
    docstring = f"{docstring}\n  Args:"
    for t_arg in transform.arguments:
        docstring = f"{docstring}\n    {t_arg.name}: {t_arg.description}"
    docstring = f"{docstring}\n    operation_name: Name to set for the operation"

    # Add return to docstring
    docstring = (
        f"{docstring}\n\n  Returns:\n    Returns an new dataset with the referenced "
        f"{transform.name!r} added to this dataset's definition"
    )
    return docstring
