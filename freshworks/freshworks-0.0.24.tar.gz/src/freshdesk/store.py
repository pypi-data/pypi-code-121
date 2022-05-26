from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from freshdesk._constants import ENCODING


@dataclass
class LimitInfo:
    """Represents limit rate information."""

    datetime: datetime

    calls_per_minute: int
    calls_remaining: int
    calls_consumed: int
    retry_time: int  # seconds

    @classmethod
    def from_bytes(cls, data: bytes) -> LimitInfo:
        (
            timestamp,
            calls_per_minute,
            calls_remaining,
            calls_consumed,
            retry_time,
        ) = data.decode(ENCODING).split(
            ";"
        )  # noqa: E501
        return cls(
            datetime=datetime.fromtimestamp(float(timestamp)),
            calls_per_minute=int(calls_per_minute),
            calls_remaining=int(calls_remaining),
            calls_consumed=int(calls_consumed),
            retry_time=int(retry_time),
        )

    def to_bytes(self) -> bytes:
        return ";".join(
            map(
                str,
                [
                    self.datetime.timestamp(),
                    self.calls_per_minute,
                    self.calls_remaining,
                    self.calls_consumed,
                    self.retry_time,
                ],
            )
        ).encode(ENCODING)
