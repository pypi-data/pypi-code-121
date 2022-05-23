from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from enum import IntFlag
from typing import Callable, Optional

from ..base_client import BaseClient

class StartCallbackType(IntFlag):
    CallbackOnProcessInstanceCreated = 1
    CallbackOnProcessInstanceFinished = 2
    CallbackOnEndEventReached = 3

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProcessStartRequest:
    process_model_id: str
    return_on: StartCallbackType = StartCallbackType.CallbackOnEndEventReached
    end_event_id: str = None
    start_event_id: str = None
    correlation_id: str = None
    initial_token: dict = None
    parent_process_instance_id: str = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProcessStartResponse:
    process_instance_id: str
    correlation_id: str
    end_event_id: Optional[str] = None
    token_payload: dict = field(default_factory=dict)

class ProcessModelHandler(BaseClient):

    def __init__(self, url: str, identity: Callable=None):
        super(ProcessModelHandler, self).__init__(url, identity)

    def start(self, process_model_id: str, request: ProcessStartRequest, options: dict={}) -> ProcessStartResponse:
        path = f"/atlas_engine/api/v1/process_models/{process_model_id}/start" 

        payload = request.to_dict()

        response_json = self.do_post(path, payload, options)

        response = ProcessStartResponse.from_dict(response_json)

        return response
