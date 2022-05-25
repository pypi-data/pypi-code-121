import time
from typing import Any, Dict, List, Optional, Union
from urllib import parse

try:
    from typing import Literal  # Only available on 3.8+ directly
except ImportError:
    from typing_extensions import Literal

import yaml

from pyrasgo.api.error import APIError
from pyrasgo.config import MAX_POLL_ATTEMPTS, POLL_RETRY_RATE
from pyrasgo.api.error import APIError
from pyrasgo.api.get import Get
from pyrasgo.utils import polling
from pyrasgo import primitives, schemas
from pyrasgo.schemas.dataset import DatasetSourceType


class Create:
    def __init__(self):
        from pyrasgo.config import get_session_api_key

        from .connection import Connection

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self._get = Get()

    def accelerator(self, *, accelerator_create: schemas.AcceleratorCreate) -> schemas.Accelerator:
        """
        Create a new accelerator Definition
        """
        # Create Accelerator in API and return the new object
        resp = self.api._post("/accelerators", _json=accelerator_create.dict(), api_version=2).json()
        return schemas.Accelerator(**resp)

    def accelerator_from_yaml(self, *, yaml_string: str) -> schemas.Accelerator:
        """
        Create a new accelerator Definition from a yml string
        Parses yml document to correct format that Rasgo expects

        Example format:
            name: Accelerator Name
            description: Accelerator Description
            arguments:
                base_dataset:
                    description: the base dataset
                    type: dataset
                column_name:
                    description: the column to drop
                    type: column
                column_name_two:
                    description: the column to drop
                    type: column
            operations:
                operation_1_name:
                    description: Drop a column
                    transform_name: drop_columns
                    transform_arguments:
                        source_table: '{{dataset_id}}'
                        json_string_arguments: '{"exclude_cols": ["{{column_name}}"]}'
                operation_2_name:
                    description: Drops another column
                    transform_name: drop_columns
                    transform_arguments:
                        source_table: '{{operation_1_name}}'
                        json_string_arguments: '{"exclude_cols": ["{{column_name_two}}"]}'
        """
        available_transforms = self._get.transforms()

        # Create Accelerator object
        yaml_dict = yaml.safe_load(yaml_string)
        yaml_dict['arguments'] = [{**{'name': k}, **v} for k, v in yaml_dict['arguments'].items()]
        yaml_dict['operations'] = [{**{'name': k}, **v} for k, v in yaml_dict['operations'].items()]

        # replace transform names with transform Ids
        for i, operation in enumerate(yaml_dict['operations']):
            transform_name = operation.pop('transform_name' if 'transform_name' in operation else 'transformName', None)
            if transform_name:
                transform_available = [x for x in available_transforms if x.name == transform_name]
                if transform_available:
                    operation['transform_id'] = transform_available[0].id
                    yaml_dict['operations'][i] = operation
                else:
                    raise APIError(f'Transform {transform_name} does not exist or is not available')

        accelerator_create = schemas.AcceleratorCreate(**yaml_dict)

        return self.accelerator(accelerator_create=accelerator_create)

    def dataset_from_accelerator(self, id: int, arguments: Dict[str, Any], name: str) -> None:
        """
        Applies the given set of arguments to an Accelerator to generate
        a new DRAFT Dataset in the Rasgo, with the given name

        Args:
            accelerator_id: Id of Accelerator to apply
            accelerator_arguments: Arguments of the Accelerator
            name: Name of the created dataset
        """
        if not name:
            raise ValueError("Please supply a name for the Dataset to create with an Accelerator")

        # Create a Draft Dataset in the Rasgo from the Accelerator
        apply_request = schemas.AcceleratorApply(name=name, arguments=arguments)
        resp = self.api._post(f"/accelerators/{id}/apply", _json=apply_request.dict(), api_version=2)

        # Print message telling users Dataset creation in progress,
        # give the URL to access it, and tell them how to get the
        # PyRasgo code of the created Accelerator Dataset
        api_dataset = schemas.Dataset(**resp.json())
        draft_dataset = primitives.Dataset(api_dataset=api_dataset)
        print(
            f"Draft dataset named {name!r} with id {draft_dataset.id} is being created in Rasgo.\n"
            f"View it's creation progress at {draft_dataset.profile()}\n\n"
            f"After the dataset is finished being built, get the PyRasgo code to re-create it using\n"
            f"    ds = rasgo.get.dataset({draft_dataset.id})\n"
            f"    print(ds.generate_py())"
        )

    def transform(
        self,
        *,
        name: str,
        source_code: str,
        type: Optional[str] = None,  # TODO: name this something other than a Python reserved word
        arguments: Optional[List[dict]] = None,
        description: Optional[str] = None,
        tags: Optional[Union[List[str], str]] = None,
        context: Optional[Dict[str, Any]] = None,
        dw_type: Optional[Literal["SNOWFLAKE", "BIGQUERY", "UNSET"]] = None,
    ) -> schemas.Transform:
        """
        Create and return a new Transform in Rasgo
        Args:
            name: Name of the Transform
            source_code: Source code of transform
            type: Type of transform it is. Used for categorization only
            arguments: A list of arguments to supply to the transform
                       so it can render them in the UI. Each argument
                       must be a dict with the keys: 'name', 'description', and 'type'
                       values all strings for their corresponding value
            description: Description of Transform
            tags: List of tags, or a tag (string), to set on this dataset
            context: Object used to add context to transforms for client use
            dw_type: DataWarehouse provider: SNOWFLAKE, BIGQUERY or UNSET
                     if not provided, will be set to your current DataWarehouse

        Returns:
            Created Transform obj
        """
        arguments = arguments if arguments else []

        # Init tag array to be list of strings
        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]

        transform = schemas.TransformCreate(
            name=name,
            type=type,
            sourceCode=source_code,
            description=description,
            tags=tags,
            context=context,
            dw_type=dw_type.upper() if dw_type else None,
        )
        transform.arguments = [schemas.TransformArgumentCreate(**x) for x in arguments]
        response = self.api._post("/transform", transform.dict(), api_version=1).json()
        return schemas.Transform(**response)

    # ----------------------------------
    #  Internal/Private Create Calls
    # ----------------------------------

    def _dataset(
        self,
        *,
        name: str,
        source_type: DatasetSourceType,
        resource_key: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = 'published',
        dw_table_id: Optional[int] = None,
        dw_operation_set_id: Optional[int] = None,
        fqtn: Optional[str] = None,
        attributes: Optional[dict] = None,
        publish_ds_table_type: Optional[str] = "VIEW",
        publish_ds_table_name: Optional[str] = None,
        generate_stats: bool = True,
        timeout: Optional[int] = None,
    ) -> schemas.Dataset:
        """
        Create a Dataset in Rasgo.

        Args:
            name: Name of the dataset
            source_type: Type of Dataset we're publishing (Rasgo vs. Snowflake. vs DataFrame)
            description: Description of the dataset
            status: Status of whether this datasets is published or not
            dw_table_id: DW table to associate with this Dataset
            dw_operation_set_id: Id of the Operation Set to associate with this Dataset
            fqtn: Fully qualified table name of the table to register this Dataset as
            attributes: Dictionary containing dataset attributes to be published
            publish_ds_table_type: If publishing an operations set's set DWTable after creating,
                                   select the table type for the published node ('VIEW' or 'TABLE')
            publish_ds_table_name: Optional user supplied table name to set on the
                                   published node/operation
            timeout: Approximate timeout for creating the table in seconds. Raise an APIError if the reached
        Returns:
            Created Dataset Obj
        """
        if not publish_ds_table_type or publish_ds_table_type.upper() not in ("TABLE", "VIEW"):
            raise ValueError(
                f"table_type {publish_ds_table_type} is not usable. "
                "Please make sure you select either 'TABLE' or 'VIEW'."
            )

        dataset_create = schemas.DatasetCreate(
            name=name,
            resource_key=resource_key,
            description=description,
            status=status,
            dw_table_id=dw_table_id,
            dw_operation_set_id=dw_operation_set_id,
            attributes=attributes,
            auto_generate_stats=generate_stats,
            source_type=source_type.value,
        )
        path = "/datasets/async"
        if fqtn:
            path = f"{path}?fqtn={parse.quote(fqtn)}"
        else:
            path = f"{path}?table_type={publish_ds_table_type}"
            if publish_ds_table_name:
                encoded_table_name = parse.quote(publish_ds_table_name)
                path = f"{path}&publish_ds_table_name={encoded_table_name}"
        response = self.api._post(path, dataset_create.dict(), api_version=2).json()
        status_tracking = schemas.StatusTracking(**response)
        for i in range(1, MAX_POLL_ATTEMPTS):
            status_tracking = schemas.StatusTracking(
                **self.api._get(f"/status-tracking/{status_tracking.tracking_uuid}", api_version=2).json()
            )
            if status_tracking.status == "completed":
                return schemas.Dataset(**self.api._get(f"/datasets/{status_tracking.message}", api_version=2).json())
            if status_tracking.status == "failed":
                raise APIError(f"Could not publish dataset: {status_tracking.message}")
            if timeout and (POLL_RETRY_RATE * i) > timeout:
                raise APIError("Timeout reached waiting for dataset creation.")
            time.sleep(POLL_RETRY_RATE)
        raise APIError(f"Never received confirmation dataset was published.")

    def _operation_set_non_async(
        self, operations: List[schemas.OperationCreate], dataset_dependency_ids: List[int]
    ) -> schemas.OperationSet:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids, in a  non-async status
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations, dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post("/operation-sets", operation_set_create.dict(), api_version=2).json()
        return schemas.OperationSet(**response)

    def _operation_set_async(
        self, operations: List[schemas.OperationCreate], dataset_dependency_ids: List[int]
    ) -> schemas.OperationSetAsyncTask:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations, dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post("/operation-sets/async", operation_set_create.dict(), api_version=2).json()
        return schemas.OperationSetAsyncTask(**response)

    def _operation_set_preview(
        self, operations: List[schemas.OperationCreate], dataset_dependency_ids: List[int]
    ) -> str:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations, dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post("/operation-sets/offline", operation_set_create.dict(), api_version=2).json()
        return response

    def _operation_set_preview_async(
        self, operations: List[schemas.OperationCreate], dataset_dependency_ids: List[int]
    ) -> schemas.OperationSetOfflineAsyncTask:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids in an async fashion
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations, dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post("/operation-sets/offline/async", operation_set_create.dict(), api_version=2).json()
        return schemas.OperationSetOfflineAsyncTask(**response)

    def _dataset_correlation_stats(self, *, table_id: int, only_if_data_changed: Optional[bool] = True) -> None:
        """
        Trigger stats generation on a dataset
        """

        # Note: dimension_column_id should not be passed, as it has already been set at publish time
        stats_create = schemas.GenerateStat(
            dwTableId=table_id, dimensionColumnId=None, onlyIfDataChanged=only_if_data_changed
        )
        self.api._post("/stats", stats_create.dict(), api_version=2)

    def _operation_render(self, operation: schemas.OperationCreate) -> str:
        """
        Test the rendering of an operation
        """
        response = self.api._post("/operation/render", operation.dict(), api_version=2).json()
        return response

    def _operation_set(
        self,
        operations: List[schemas.OperationCreate],
        dataset_dependency_ids: List[int],
        async_compute: bool = True,
        async_verbose: bool = False,
    ) -> schemas.OperationSet:
        """
        Create and return an Operation set based on the input
        operations and dataset dependencies

        Set param `async_compute` to False to not create op with async

        Args:
            operations: List of operations to add to operation set.
                         Should be in ordered by time operation added.
            dataset_dependency_ids: Dataset ids to set as a parent for this operation set
            async_compute: Set to False not create op set in async fashion in backend/API
            async_verbose: If creating op set in async mode, set verbose to True to have verbose output

        Returns:
            Created Operation Set
        """
        if async_compute:
            from pyrasgo.api import Get

            # Submit the task request
            task_request = self._operation_set_async(
                operations=operations, dataset_dependency_ids=dataset_dependency_ids
            )
            operation_set_id = polling.poll_operation_set_async_status(task_request=task_request, verbose=async_verbose)
            return Get()._operation_set(operation_set_id)
        else:
            return self._operation_set_non_async(operations=operations, dataset_dependency_ids=dataset_dependency_ids)
