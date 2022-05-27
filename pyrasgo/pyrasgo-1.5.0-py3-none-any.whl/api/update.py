"""
API Update Functions
"""
import time
from typing import List, Optional, Union

try:
    from typing import Literal  # Only available on 3.8+ directly
except ImportError:
    from typing_extensions import Literal

from pyrasgo import errors, primitives, schemas
from pyrasgo.config import MAX_POLL_ATTEMPTS, POLL_RETRY_RATE


class Update:
    """
    API Update Class
    """

    def __init__(self):
        from pyrasgo.api import Get
        from pyrasgo.api.connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.get = Get()
        self._dw = None

    def dataset(
        self,
        dataset: primitives.Dataset,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        attributes: Optional[dict] = None,
    ) -> primitives.Dataset:
        """
        Update a dataset name, description, and/or attributes in Rasgo
        """
        # Raise error if trying to update a dataset in offline mode
        if not dataset._api_dataset:
            raise errors.RasgoRuleViolation(
                "Can not update dataset. Needs to be saved first with `rasgo.save.dataset()`"
            )

        dataset_update = schemas.DatasetUpdate(
            # Possible Changed Fields
            name=name,
            description=description,
            # Persist other fields in update contract so no fields set to None in update
            status=dataset._api_dataset.status,
            owner_id=dataset._api_dataset.owner_id,
            dw_table_id=dataset._api_dataset.dw_table_id,
            attributes=attributes,
        )
        response = self.api._put(
            f"/datasets/{dataset._api_dataset.id}",
            dataset_update.dict(exclude_unset=True, exclude_none=True),
            api_version=2,
        ).json()
        dataset_schema = schemas.Dataset(**response)
        return primitives.Dataset(api_dataset=dataset_schema)

    def dataset_column(
        self,
        dataset_column_id: int,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        attributes: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> schemas.DatasetColumn:
        """
        Update metadata about a dataset column

        Args:
            dataset_column_id: Dataset column id to updated. Use `dataset.columns[x].id` to retrieve
            display_name: Display name to update for this dataset column if set
            description: Description to update for this dataset column if set
            attributes: Attributes to add or update for this dataset column. Set as Key Value pairs dict
            tags: Tags to add to this dataset column

        Returns:
            Updated Dataset Column Obj
        """
        ds_col_update = schemas.DatasetColumnUpdate(
            display_name=display_name,
            description=description,
            attributes=attributes,
            tags=tags,
        )
        resp = self.api._put(
            f"/dataset-columns/{dataset_column_id}",
            ds_col_update.dict(exclude_unset=True, exclude_none=True),
            api_version=2,
        ).json()
        return schemas.DatasetColumn(**resp)

    def dataset_table(self, dataset: primitives.Dataset, verbose: bool = False, timeout: Optional[int] = None) -> None:
        """
        Kicks off a query for re-materializing a dataset's set Dw Table.

        The dataset needs to be published first in order call this function

        Args:
            dataset: Published dataset to refresh table for
            verbose: If True will print information related to refreshing table
            timeout: Approximate timeout for creating the table in seconds. Raise an APIError if the reached
        """
        # We need to ensure that the API dataset is exists and is published
        if not dataset._api_dataset or dataset.status.lower() != "published":
            raise errors.RasgoRuleViolation('Can not refresh table. Dataset must first be published')

        if verbose:
            print(f"Refreshing table for dataset with id '{dataset.id}' at fqtn: '{dataset.fqtn}'")

        # Call endpoint to kick off Query to re-create table in worker
        response = self.api._put(f"/datasets/{dataset._api_dataset.id}/table-refresh", api_version=2).json()
        status_tracking = schemas.StatusTracking(**response)

        # Poll the async job until completion, failure, or timeout
        for i in range(1, MAX_POLL_ATTEMPTS):
            status_tracking = schemas.StatusTracking(
                **self.api._get(f"/status-tracking/{status_tracking.tracking_uuid}", api_version=2).json()
            )
            if status_tracking.status == "completed":
                if verbose:
                    print(f"Done Refreshing table for dataset with id '{dataset.id}' " f"at fqtn: '{dataset.fqtn}'")
                break
            if status_tracking.status == "failed":
                raise errors.APIError(f"Could not refresh dataset table: {status_tracking.message}")
            if timeout and (POLL_RETRY_RATE * i) > timeout:
                raise errors.APITimeoutWarning("Timeout reached waiting for dataset table refreshing")
            time.sleep(POLL_RETRY_RATE)
            if verbose:
                print("Query still executing...")

    def dataset_schema(self, dataset_id: int) -> None:
        """
        Queries the information_schema to get column metadata from Snowflake
        Then updates this dataset's column metadata in Rasgo to match
        """
        self.api._put(
            f"/datasets/{dataset_id}/sync-schema",
            api_version=2,
        ).json()

    def transform(
        self,
        transform_id: int,
        name: Optional[str] = None,
        source_code: Optional[str] = None,
        type: Optional[str] = None,
        arguments: Optional[List[dict]] = None,
        description: Optional[str] = None,
        tags: Optional[Union[List[str], str]] = None,
        dw_type: Optional[Literal["SNOWFLAKE", "BIGQUERY", "UNSET"]] = None,
    ) -> schemas.Transform:
        """
        Updates a transform in Rasgo

        Args:
            transform_id: Id of transform to update
            name: Name of the Transform
            source_code: Source code of transform
            type: Type of transform it is. Used for categorization only
            arguments: A list of arguments to supply to the transform
                       so it can render them in the UI. Each argument
                       must be a dict with the keys: 'name', 'description', and 'type'
                       values all strings for their corresponding value
            description: Description of Transform
            tags: List of tags, or a tag (string), to set on this dataset
            dw_type: DataWarehouse provider: SNOWFLAKE, BIGQUERY or UNSET
        """
        # Init tag array to be list of strings
        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]

        # Make request to update transform and return
        transform_update = schemas.TransformUpdate(
            name=name,
            type=type,
            description=description,
            sourceCode=source_code,
            arguments=arguments,
            tags=tags,
            dw_type=dw_type.upper() if dw_type else None,
        )
        response = self.api._put(
            f"/transform/{transform_id}",
            transform_update.dict(exclude_unset=True, exclude_none=True),
            api_version=1,
        ).json()
        return schemas.Transform(**response)
