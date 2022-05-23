from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import Callable

import dataclasses_json
from ..base_client import BaseClient

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageTriggerRequest:
    payload: dict


class EventsHandler(BaseClient):
    def __init__(self, url: str, identity: Callable=None):
        super(EventsHandler, self).__init__(url, identity)

    def trigger_message(self, event_name: str, request: MessageTriggerRequest, options: dict={}):
        url = f"/atlas_engine/api/v1/messages/{event_name}/trigger"

        process_instance_id = options.get('process_instance_id', None)

        if process_instance_id is not None:
            url = f"{url}?process_instance_id={process_instance_id}"

        payload = request.to_dict()

        _ = self.do_post(url, payload, options)

        return True


    def trigger_signal(self, signal_name: str, options: dict={}):
        url = f"/atlas_engine/api/v1/signals/{signal_name}/trigger"

        _ = self.do_post(url, {}, options)

        return True
