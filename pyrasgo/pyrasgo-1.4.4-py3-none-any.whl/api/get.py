from typing import List, Optional

from .error import APIError
from pyrasgo import schemas
from pyrasgo import primitives


class Get:
    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self._dw = None

    @property
    def data_warehouse(self):
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        if self._dw:
            return self._dw
        self._dw: SnowflakeDataWarehouse = DataWarehouse.connect()
        return self._dw

    def accelerator(self, accelerator_id: int) -> schemas.Accelerator:
        """
        Return an Accelerator with specified id
        """
        response = self.api._get(f"/accelerators/{accelerator_id}", api_version=2).json()
        return schemas.Accelerator(**response)

    def accelerators(self) -> List[schemas.Accelerator]:
        """
        Return a list of all Accelerator's available to user
        """
        # Make API call get get bulk Accelerator Json objs
        response = self.api._get("/accelerators", api_version=2).json()

        # Convert response to Accelerator Primitives
        accelerators = []
        for accelerator_json in response:
            api_accelerator = schemas.Accelerator(**accelerator_json)
            accelerators.append(api_accelerator)
        return accelerators

    def dataset(
        self,
        dataset_id: Optional[int] = None,
        fqtn: Optional[str] = None,
        resource_key: Optional[str] = None,
        version: Optional[int] = None,
    ) -> primitives.Dataset:
        """
        Return a Rasgo dataset primitive by Id or FQTN
        """
        no_input_supplied = dataset_id is None and not fqtn and not resource_key
        too_many_inputs_supplied = (bool(dataset_id) + bool(fqtn) + bool(resource_key or version)) > 1
        if no_input_supplied or too_many_inputs_supplied:
            raise ValueError(
                "Valid Dataset retrieval options are:\n1. id\n2. fqtn\n3. resource_key\n4. resource_key and version"
            )

        try:
            if dataset_id:
                response = self.api._get(f"/datasets/{dataset_id}", api_version=2).json()
            elif fqtn:
                response = self.api._get(f"/datasets/match/{fqtn}", api_version=2).json()
            elif resource_key:
                response = self.api._get(
                    f"/datasets/rk/{resource_key}{f'/{version}' if version else ''}",
                    api_version=2,
                ).json()
            dataset_schema = schemas.Dataset(**response)

            operation_set_schema = None
            if dataset_schema.dw_operation_set_id:
                response = self.api._get(
                    f"/operation-sets/{dataset_schema.dw_operation_set_id}",
                    api_version=2,
                ).json()
                operation_set_schema = schemas.OperationSet(**response)
            return primitives.Dataset(
                api_dataset=dataset_schema,
                api_operation_set=operation_set_schema,
            )
        except Exception:
            if dataset_id:
                raise APIError(f"Dataset with id '{dataset_id!r}' does not exist or this API key does not have access.")
            elif fqtn:
                raise APIError(f"Dataset with fqtn '{fqtn}' does not exist or this API key does not have access.")

    def datasets(
        self,
        published_only: bool = False,
        include_community: bool = False,
    ) -> List[primitives.Dataset]:
        """
        Return all datasets in Rasgo attached to your organization

        Params
        `only_published` boolean:
            Instructs whether to return all datasets (including drafts) or
            only published datasets
        """
        # Get transforms so we can cache them for use in transforming datasets
        transforms = self.transforms()
        PAGE_SIZE = 100
        offset = 0

        datasets = []
        while True:
            response = self.api._get(
                f"/datasets?page_size={PAGE_SIZE}&page_start={offset}"
                f"&include_community={include_community}"
                f"&published_only={published_only}",
                api_version=2,
            ).json()
            for r in response:
                dataset_schema = schemas.Dataset(**r)
                dataset = primitives.Dataset(
                    api_dataset=dataset_schema,
                    transforms=transforms,
                )
                datasets.append(dataset)
            if len(response) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
        return datasets

    def dataset_py(self, dataset_id: int) -> str:
        """
        Return the pyrasgo code which will create an offline copy
        of a dataset (by ds id)  whether DS is in draft or
        unpublished status
        """
        resp = self.api._get(
            f"/datasets/{dataset_id}/export/python",
            api_version=2,
        ).json()
        return resp

    def dataset_yaml(
        self,
        dataset_id: Optional[int] = None,
    ) -> str:
        try:
            return self.api._get(f"/datasets/{dataset_id}/yaml", api_version=2).text
        except Exception:
            raise APIError(f"Dataset with id '{dataset_id!r}' does not exist or this API key does not have access.")

    def transform(self, transform_id: int) -> schemas.Transform:
        """Returns an individual transform"""
        try:
            response = self.api._get(f"/transform/{transform_id}", api_version=1).json()
            return schemas.Transform(**response)
        except Exception:
            raise APIError(f"Transform with id '{transform_id}' does not exist or this API key does not have access.")

    def transforms(self) -> List[schemas.Transform]:
        """Returns a list of available transforms"""
        response = self.api._get("/transform", api_version=1).json()
        return [schemas.Transform(**r) for r in response]

    def community_transforms(self) -> List[schemas.Transform]:
        response = self.api._get("/transform/community", api_version=1).json()
        return [schemas.Transform(**r) for r in response]

    def user(self):
        response = self.api._get("/users/me", api_version=1).json()
        return schemas.User(**response)

    # ----------------------------------
    #  Internal/Private Get Calls
    # ----------------------------------

    def _dataset_columns(self, dataset_id: int) -> List[schemas.DatasetColumn]:
        """
        Return the dataset columns for a specific dataset

        Args:
            dataset_id: Id of dataset to retrieve columns for
        """
        response = self.api._get(
            f"/dataset-columns/ds/{dataset_id}",
            api_version=2,
        ).json()
        return [schemas.DatasetColumn(**x) for x in response]

    def _operation_set(self, operation_set_id: int) -> schemas.OperationSet:
        """
        Return a Rasgo operation set by id
        """
        response = self.api._get(
            f"/operation-sets/{operation_set_id}",
            api_version=2,
        ).json()
        return schemas.OperationSet(**response)

    def _operation_set_async_status(self, task_id: int) -> schemas.OperationSetAsyncTask:
        """
        Returns the status of an Operation Set creation task by id
        """
        response = self.api._get(
            f"/operation-sets/async/{task_id}",
            api_version=2,
        ).json()
        return schemas.OperationSetAsyncTask(**response)

    def _operation_set_offline_async_status(self, task_id: int) -> schemas.OperationSetOfflineAsyncTask:
        """
        Returns the status of an Operation Set creation task by id
        """
        response = self.api._get(
            f"/operation-sets/offline/async/{task_id}",
            api_version=2,
        ).json()
        return schemas.OperationSetOfflineAsyncTask(**response)
