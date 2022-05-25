import json
import logging
import time
import typing

from pydantic import BaseModel

logger = logging.getLogger("django")

# Used by EventEnvelope
EventRegistry = typing.Dict[str, typing.Type["Event"]]
_event_registry: EventRegistry = {}


class Event(BaseModel):
    @classmethod
    @property
    def name(cls) -> str:
        return cls.__name__


class EventEnvelope(BaseModel):
    """Use this class to publish events via messaging (e.g. Pub/Sub)"""

    event_type: str
    timestamp: int
    data: Event

    @classmethod
    def create(cls, event: Event) -> "EventEnvelope":
        return cls(
            event_type=event.name,
            timestamp=int(time.time()),
            data=event,
        )

    @classmethod
    def from_published_json(cls, message: bytes) -> "EventEnvelope":
        """Instantiate EventEnvelope from a received message (e.g. from Pub/Sub).
        This facilitates using Event instances in worker handler registries e.g.:

        event_envelope = EventEnvelope.from_published_json(message.data)

        EVENT_HANDLERS = {
            events.PaymentSubmitted: [handle_payment_submitted],
        }

        handlers = EVENT_HANDLERS.get(event_envelope.event_type, [])

        for handler in handlers:
            handler(event_envelope.data)
        """

        json_msg = json.loads(message)

        try:
            data = json_msg["data"]
            event_type_name = json_msg["event_type"]
        except KeyError:
            raise RuntimeError("Message doesn't have a valid EventEnvelope schema")

        # Reconstitute Event
        try:
            event_type = get_registered_events()[event_type_name]
        except KeyError:
            raise RuntimeError(
                f"Received message with unknown event type {event_type_name!r}"
            )
        else:
            json_msg["data"] = event_type(**data)

            return cls(**json_msg)

    @property
    def event(self) -> Event:
        return self.data

    def to_publishable_json(self) -> bytes:
        return self.json().encode("utf-8")


def register_event(event: typing.Type[Event]):
    logger.debug("Registered event %s", event)
    _event_registry[event.name] = event

    return event


def get_registered_events() -> EventRegistry:
    return _event_registry
