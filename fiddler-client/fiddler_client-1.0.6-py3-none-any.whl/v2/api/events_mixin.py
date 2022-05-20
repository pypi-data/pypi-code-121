import copy
import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from fiddler.utils import logging
from fiddler.v2.constants import FiddlerTimestamp, FileType
from fiddler.v2.schema.events import EventIngest, EventsIngest
from fiddler.v2.utils.exceptions import FiddlerAPIException, handle_api_error_response
from fiddler.v2.utils.response_handler import APIResponseHandler

logger = logging.getLogger(__name__)


class EventsMixin:
    @handle_api_error_response
    def publish_events_batch(
        self,
        project_name: str,
        model_name: str,
        events_path: Path,
        batch_id: Optional[str] = None,
        events_schema: Optional[str] = None,
        id_field: Optional[str] = None,
        is_update: Optional[bool] = None,
        timestamp_field: Optional[str] = None,
        timestamp_format: Optional[FiddlerTimestamp] = None,
        group_by: Optional[str] = None,
        file_type: Optional[FileType] = None,
        is_sync: Optional[bool] = True,
    ) -> Union[dict, None]:
        """
        Publishes a batch events object to Fiddler Service.
        :param project_name: The project to which the model whose events are being published belongs.
        :param model_name: The model whose events are being published.
        :param events_path: pathlib.Path pointing to the events file to be uploaded
        :param batch_id: <TBD>
        :param events_schema: <TBD>
        :param id_field: Column to extract id value from.
        :param is_update: Bool indicating if the events are updates to previously published rows
        :param timestamp_field: Column to extract timestamp value from.
                                Timestamp must match the specified format in `timestamp_format`.
        :param timestamp_format: Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param group_by: Column to group events together for Model Performance metrics. For example,
                        in ranking models that column should be query_id or session_id, used to
                        compute NDCG and MAP. Be aware that the batch_source file/dataset provided should have
                        events belonging to the SAME query_id/session_id TOGETHER and cannot be mixed
                        in the file. For example, having a file with rows belonging to query_id 31,31,31,2,2,31,31,31
                        would not work. Please sort the file by group_by group first to have rows with
                        the following order: query_id 31,31,31,31,31,31,2,2.
        :param file_type: FileType which specifices the filetype csv etc.
        :param is_sync: A boolean value which determines if the upload method works in synchronous mode or async mode
        :returns: Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        content_type, request_body = EventsIngest(
            events_path=events_path,
            batch_id=batch_id,
            events_schema=events_schema,
            id_field=id_field,
            is_update=is_update,
            timestamp_format=timestamp_format,
            timestamp_field=timestamp_field,
            group_by=group_by,
            file_type=file_type,
        ).multipart_form_request()
        # refer comment in dataset_mixin.py/upload_dataset for reason behind copying client
        multipart_headers = copy.deepcopy(self.client.request_headers)
        multipart_headers.update({'Content-Type': content_type})
        client = self._get_http_client(request_headers=multipart_headers)
        response = client.events._(
            f'{self.organization_name}:{project_name}:{model_name}'
        ).ingest.post(
            request_body=request_body,
        )
        # @TODO: Handle invalid file path exception
        if response.status_code == HTTPStatus.ACCEPTED:
            resp = APIResponseHandler(response).get_data()
            if is_sync:
                job_id = resp['job_uuid']
                self.poll_job(job_id, interval=1)
            else:
                return resp
        else:
            # raising a generic FiddlerAPIException
            logger.error('Failed to publish events')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.body,
                errors=[],
            )

    @handle_api_error_response
    def publish_event(
        self,
        project_name: str,
        model_name: str,
        event: dict,
        event_id: Optional[str] = None,
        id_field: Optional[str] = None,
        is_update: Optional[bool] = None,
        event_timestamp: Optional[str] = None,
        timestamp_format: Optional[str] = None,
    ) -> Union[str, None]:
        """
        Publishes an event to Fiddler Service.
        :param project_name: The project to which the model whose events are being published belongs
        :param model_name: The model whose events are being published
        :param dict event: Dictionary of event details, such as features and predictions.
        :param event_id: Unique str event id for the event
        :param event_timestamp: The UTC timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param timestamp_format:   Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :returns: Unique event id incase of successful submitted request.
        """
        request_body = EventIngest(
            event=event,
            event_id=event_id,
            id_field=id_field,
            is_update=is_update,
            event_timestamp=event_timestamp,
            timestamp_format=timestamp_format,
        ).dict()
        response = self.client.events._(
            f'{self.organization_name}:{project_name}:{model_name}'
        ).ingest.event.post(request_body=request_body)
        if response.status_code == HTTPStatus.ACCEPTED:
            response_dict = APIResponseHandler(response).get_data()
            logger.info(response_dict.get('message'))
            return response_dict.get('__fiddler_id')
        else:
            # raising a generic FiddlerAPIException
            logger.error('Failed to publish events')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.body,
                errors=[],
            )

    @handle_api_error_response
    def publish_events_batch_dataframe(
        self,
        project_name: str,
        model_name: str,
        events_df: pd.DataFrame,
        batch_id: Optional[str] = None,
        id_field: Optional[str] = None,
        is_update: Optional[bool] = None,
        timestamp_field: Optional[str] = None,
        timestamp_format: Optional[FiddlerTimestamp] = None,
        group_by: Optional[str] = None,
        is_sync: Optional[bool] = True,
    ) -> Union[str, None]:
        """
        Publishes a batch events object to Fiddler Service.
        :param project_name: The project to which the model whose events are being published belongs.
        :param model_name: The model whose events are being published.
        :param events_df: pd.DataFrame object having the events
        :param batch_id: <TBD>
        :param id_field: Column to extract id value from.
        :param is_update: Bool indicating if the events are updates to previously published rows
        :param timestamp_field: Column to extract timestamp value from.
                                Timestamp must match the specified format in `timestamp_format`.
        :param timestamp_format: Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param group_by: Column to group events together for Model Performance metrics. For example,
                        in ranking models that column should be query_id or session_id, used to
                        compute NDCG and MAP. Be aware that the batch_source file/dataset provided should have
                        events belonging to the SAME query_id/session_id TOGETHER and cannot be mixed
                        in the file. For example, having a file with rows belonging to query_id 31,31,31,2,2,31,31,31
                        would not work. Please sort the file by group_by group first to have rows with
                        the following order: query_id 31,31,31,31,31,31,2,2.
        :param is_sync: A boolean value which determines if the upload method works in synchronous mode or async mode
        :returns: Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        file_type = FileType.CSV
        with tempfile.NamedTemporaryFile(suffix=file_type, mode='w') as temp:
            events_df.to_csv(temp, index=False)
            events_path = Path(temp.name)
            return self.publish_events_batch(
                project_name=project_name,
                model_name=model_name,
                events_path=events_path,
                batch_id=batch_id,
                id_field=id_field,
                is_update=is_update,
                timestamp_field=timestamp_field,
                timestamp_format=timestamp_format,
                group_by=group_by,
                is_sync=is_sync,
            )
