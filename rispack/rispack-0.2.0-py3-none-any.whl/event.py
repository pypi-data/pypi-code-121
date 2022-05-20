import os
from abc import abstractmethod

import boto3
import json

from rispack.logger import logger
from rispack.schema import BaseSchema
from rispack.errors import EventBusNotSetError

class BaseEvent(BaseSchema):
    @abstractmethod
    def get_type(self):
        raise NotImplementedError

    @abstractmethod
    def get_version(self):
        raise NotImplementedError

    def publish(self):
        payload = self.dump()

        event_type = self.get_type()

        logger.info(f"Publishing event {event_type}")

        source = "".join(["rispar", ".", os.environ.get("SERVICE_NAME", "platform")])
        event_bus = os.environ.get('EVENT_BUS')

        if not event_bus:
            raise EventBusNotSetError

        response = self.client.put_events(
            Entries=[
                {
                    "Source": source,
                    "Detail": json.dumps(payload),
                    "EventBusName": event_bus,
                    "DetailType": event_type,
                }
            ]
        )

        return response
