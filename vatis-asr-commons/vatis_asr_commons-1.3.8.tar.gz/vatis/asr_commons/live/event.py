import dataclasses
import time
from enum import Enum
from typing import Optional, List


class Status(Enum):
    # Stream is available for usage
    AVAILABLE = 'AVAILABLE'
    # Stream was picked for reservation but is not reserved yet
    LOCKED = 'LOCKED'
    # Stream in process of being reserved
    RESERVING = 'RESERVING'
    # Stream was reserved for a client that didn't connect yet
    RESERVED = 'RESERVED'
    # A client is connected to the stream
    CONNECTED = 'CONNECTED'
    # The client unexpectedly disconnected from the stream
    DISCONNECTED = 'DISCONNECTED'


@dataclasses.dataclass
class StreamEvent:
    CURRENT_TIMESTAMP = None

    timestamp: Optional[float]

    def __post_init__(self):
        if self.timestamp is StreamEvent.CURRENT_TIMESTAMP:
            self.timestamp = time.time()


@dataclasses.dataclass
class StatusChangedEvent(StreamEvent):
    old_status: Status
    new_status: Status
    ip: str


@dataclasses.dataclass
class StreamCreatedEvent(StreamEvent):
    ip: str
    hostname: str
    initial_status: Status
    models: List[str]
    user: Optional[str] = None


@dataclasses.dataclass
class StreamDeletedEvent(StreamEvent):
    ip: str
    hostname: str


@dataclasses.dataclass
class StreamIdleEvent(StreamEvent):
    ip: str
    hostname: str
    current_status: Status
