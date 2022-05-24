import os
import json

__all__ = ["QueueMessageSchema"]


class QueueMessageSchema:
    __schema = None

    @classmethod
    def get_schema(cls) -> dict:
        if cls.__schema is None:
            with open(
                os.path.join(os.path.dirname(__file__), "utf_queue_models", "schema", "queue_message.json")
            ) as f:
                cls.__schema = json.load(f)
        return cls.__schema
