import copy
import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from pydantic import parse_obj_as

from fiddler.utils import logging
from fiddler.v2.constants import FileType
from fiddler.v2.schema.common import DatasetInfo
from fiddler.v2.schema.dataset import Dataset, DatasetIngest
from fiddler.v2.utils.exceptions import FiddlerAPIException, handle_api_error_response
from fiddler.v2.utils.response_handler import (
    APIResponseHandler,
    PaginatedResponseHandler,
)

logger = logging.getLogger(__name__)


class DatasetMixin:
    @handle_api_error_response
    def get_datasets(self, project_name: str) -> List[Dataset]:
        """
        Get all the datasets in a project

        :param project_name:    The project for which you want to get the datasets
        :returns: A list containing `Dataset` objects.
        """

        response = self.client.datasets.get(
            query_params={
                'organization_name': self.organization_name,
                'project_name': project_name,
            }
        )
        _, items = PaginatedResponseHandler(response).get_pagination_details_and_items()
        return parse_obj_as(List[Dataset], items)

    @handle_api_error_response
    def get_dataset(self, project_name: str, dataset_name: str) -> Dataset:
        """
        Get all the details for a given dataset

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name of which you need the details

        :returns: Dataset object which contains the details
        """

        response = self.client.datasets._(
            f'{self.organization_name}:{project_name}:{dataset_name}'
        ).get()
        response_handler = APIResponseHandler(response)
        return Dataset.deserialize(response_handler)

    @handle_api_error_response
    def delete_dataset(self, project_name: str, dataset_name: str) -> None:
        """
        Delete a dataset

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name which you want to delete

        :returns: None
        """

        response = self.client.datasets._(
            f'{self.organization_name}:{project_name}:{dataset_name}'
        ).delete()
        if response.status_code == HTTPStatus.OK:
            logger.info(f'{dataset_name} deleted successfully.')
        else:
            # @TODO: Handle non 200 status response
            logger.info('Delete unsuccessful')

    @handle_api_error_response
    def upload_dataset(
        self,
        project_name: str,
        dataset_name: str,
        files: Dict[str, Path],
        info: Optional[DatasetInfo] = None,
        file_type: Optional[FileType] = None,
        file_schema: Optional[dict] = None,
        is_sync: Optional[bool] = True,
    ) -> dict:
        """
        Upload a dataset.

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name which you want to delete
        :param files:           A dictionary of file name and key and file path as value
        :param dataset_info:    DatasetInfo object to_dict
        :param file_type:       FileType which specifices the filetype csv etc.
        :param file_schema:     <TBD>
        :param is_sync:        A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns: dict stating the response from the server and job_tracking id
        """

        content_type, request_body = DatasetIngest(
            name=dataset_name,
            file_paths=files,
            info=info,
            file_type=file_type,
            file_schema=file_schema,
        ).multipart_form_request()
        # if you explictly pass request_headers while making a request, http_client updates the global request_headers with the new one passed.
        # this updated global request_headers is then used for all the subsequent requests
        # this causes problem in case of multipart/form request because we want the headers to be updated only for this one request. Not for any other requests that we make
        # A workaround is to create a new client object specifically for this request. This way, the update request_headers will only impact this copy and not the original self.client
        # @TODO: Alternate approach is to fork http_client and turn off the global request_header update in it.
        multipart_headers = copy.deepcopy(self.client.request_headers)
        multipart_headers.update({'Content-Type': content_type})
        client = self._get_http_client(request_headers=multipart_headers)
        response = client.datasets._(
            f'{self.organization_name}:{project_name}:{dataset_name}'
        ).ingest.post(
            request_body=request_body,
        )
        # @TODO: Handle invalid file path exception
        # @TODO: handle response from ingestion endpoint
        if response.status_code == HTTPStatus.ACCEPTED:
            resp = APIResponseHandler(response).get_data()
            if is_sync:
                job_id = resp['job_uuid']
                self.poll_job(job_id, interval=1)
            else:
                return resp

        else:
            # raising a generic FiddlerAPIException
            logger.error(f'Failed to upload dataset {dataset_name}.')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.body,
                errors=[],
            )

    def upload_dataset_csv(
        self,
        project_name: str,
        dataset_name: str,
        files: Dict[str, Path],
        info: Optional[DatasetInfo] = None,
        file_schema: Optional[dict] = None,
        is_sync: Optional[bool] = True,
    ):
        """
        Upload dataset as csv file

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name which you want to delete
        :param files:           A dictionary of pathlib.Path as value and name as key
        :param dataset_info:    Dataset Info object to_dict
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns <TBD>
        """
        return self.upload_dataset(
            project_name, dataset_name, files, info, FileType.CSV, file_schema, is_sync
        )

    @handle_api_error_response
    def upload_dataset_dataframe(
        self,
        project_name: str,
        dataset_name: str,
        datasets: Dict[str, pd.DataFrame],
        info: Optional[DatasetInfo] = None,
        is_sync: Optional[bool] = True,
    ) -> dict:
        """
        Upload dataset as pd.DdataFrame

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name which you want to delete
        :param datasets:        A dictionary of dataframe as value and name as key
        :param dataset_info:    Dataset Info object to_dict
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns <TBD>
        """
        with tempfile.TemporaryDirectory() as tmp:
            files = {}
            file_type = FileType.CSV
            for name, df in datasets.items():
                file_path = Path(tmp) / f'{name}{file_type}'
                df.to_csv(file_path, index=False)
                files.update({name: file_path})

            return self.upload_dataset(
                project_name,
                dataset_name,
                files=files,
                info=info,
                file_type=file_type,
                is_sync=is_sync,
            )

    @handle_api_error_response
    def upload_dataset_from_dir(
        self,
        project_name: str,
        dataset_name: str,
        dataset_dir: Path,
        info: Optional[DatasetInfo] = None,
        file_type: FileType = FileType.CSV,
        file_schema: Optional[dict] = None,
        is_sync: bool = True,
    ):
        """
        Upload dataset artefacts (data file and dataset info yaml) from a directory

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name which you want to delete
        :param dataset_dir:     pathlib.Path pointing to the dataset dir to be uploaded
        :param info:            DatasetInfo object
        :param file_type:       FileType
        :param file_schema:     <TBD>
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns:               <TBD>
        """
        # @TODO: Move repetative input validation used accross different methods to utils
        if not dataset_dir.is_dir():
            raise ValueError(f'{dataset_dir} is not a directory')

        files = {
            data_file.name: data_file
            for data_file in dataset_dir.glob(f'*{file_type.value}')
        }

        if not files:
            raise ValueError(f'No data files found in {dataset_dir}.')

        return self.upload_dataset(
            project_name=project_name,
            dataset_name=dataset_name,
            files=files,
            info=info,
            file_schema=file_schema,
            is_sync=is_sync,
        )
