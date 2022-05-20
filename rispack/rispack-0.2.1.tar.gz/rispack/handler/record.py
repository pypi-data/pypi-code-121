import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from rispack.errors import UnhandledSourceError


class RecordBuilder:
    def __init__(self, event):
        self.event = event

    def build(self):
        try:
            return self._get_record()
        except UnhandledSourceError:
            print("unhandled soruce")
            return self.event

    def _get_record(self):
        source = self._get_source()

        if source == "s3":
            file = self.event.get("s3")

            return FileRecord(
                bucket=file["bucket"]["name"],
                bucket_arn=file["bucket"]["arn"],
                key=file["object"]["key"],
                size=file["object"]["size"],
                etag=file["object"]["eTag"],
            )

        if source == "sqs":
            body = self.event["body"]

            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return body

            if body.get("detail"):
                isotime = body.get("time").replace("Z", "+00:00")
                return EventRecord(
                    id=body.get("id"),
                    detail=body.get("detail"),
                    detail_type=body.get("detail-type"),
                    source=body.get("source"),
                    time=datetime.fromisoformat(isotime),
                    version=body.get("version"),
                )
            else:
                message = json.loads(body.get("Message"))
                isotime = message.get("at").replace("Z", "+00:00")

                return EventRecord(
                    id=message.get("id"),
                    detail=message.get("payload"),
                    detail_type=message.get("type"),
                    source=message.get("category"),
                    time=datetime.fromisoformat(isotime),
                    version=message.get("version"),
                )

    def _get_source(self):
        source = self.event

        try:
            return source.get("eventSource").split(":")[1]
        except Exception:
            raise UnhandledSourceError("No eventSource key found")


@dataclass
class FileRecord:
    bucket: str
    bucket_arn: str
    key: str
    size: datetime
    etag: str


@dataclass
class EventRecord:
    id: UUID
    detail: Dict[str, Any]
    detail_type: str
    source: str
    time: datetime
    version: str
