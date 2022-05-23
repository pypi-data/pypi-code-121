from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from typing import Callable, List, Optional

from dataclasses_json.undefined import Undefined

from ..base_client import BaseClient
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FetchAndLockRequestPayload:
    worker_id: str
    topic_name:	str
    max_tasks:	int = 10
    long_polling_timeout: int = (10 * 1000)
    lock_duration: int = (100 * 1000)
    payload_filter: str = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ExternalTask:
    id: str
    worker_id: str
    topic: str
    flow_node_instance_id: str
    correlation_id: str
    process_definition_id: str
    process_instance_id: str
    owner_id: str = None
    payload: dict = None
    lock_expiration_time: str = None
    state: str = None                  # ExternalTaskStatestring(pending = pending, finished = finished)
    created_at: str = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ExtendLockRequest:
    worker_id: str
    additional_duration: int

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FinishExternalTaskRequestPayload:
    worker_id: str
    result: dict

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BpmnError:
    error_code: str
    error_message: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BpmnErrorRequest:
    worker_id: str
    bpmn_error: BpmnError

@dataclass_json(letter_case=LetterCase)
@dataclass
class ServiceError:
    error_code: str
    error_message: str
    error_details: dict = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ServiceErrorRequest:
    worker_id: str
    error: ServiceError

class ExternalTaskHandler(BaseClient):

    def __init__(self, url: str, identity: Callable=None):
        super(ExternalTaskHandler, self).__init__(url, identity)

    def fetch_and_lock(self, request: FetchAndLockRequestPayload, options: dict={}) -> List[ExternalTask]:
        path = '/atlas_engine/api/v1/external_tasks/fetch_and_lock'

        payload = request.to_dict()

        response_list_of_dict = self.do_post(path, payload, options)

        response = ExternalTask.schema().load(response_list_of_dict, many=True)

        return response

    def extend_lock(self, external_task_id: str, request: ExtendLockRequest, options: dict={}):
        path = f"/atlas_engine/api/v1/external_tasks/{external_task_id}/finish"

        payload = request.to_dict()

        _ = self.do_put(path, payload, options)

        return True

    def finish(self, external_task_id: str, request: FinishExternalTaskRequestPayload, options: dict={}):
        path = f"/atlas_engine/api/v1/external_tasks/{external_task_id}/finish"

        payload = request.to_dict()

        _ = self.do_put(path, payload, options)

        return True

    def handle_bpmn_error(self, external_task_id, str, request: ServiceErrorRequest, options: dict={}):
        path = f"/atlas_engine/api/v1/external_tasks/{external_task_id}/handle_bpmn_error"

        payload = request.to_dict()

        _ = self.do_put(path, payload, options)

        return True

    def handle_service_error(self, external_task_id, str, request: BpmnErrorRequest, options: dict={}):
        path = f"/atlas_engine/api/v1/external_tasks/{external_task_id}/handle_service_error"

        payload = request.to_dict()

        _ = self.do_put(path, payload, options)

        return True
