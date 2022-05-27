import datetime as dt
import json
import uuid
from decimal import Decimal


class JsonSerializer:
    mimetype = "application/json"

    def default(self, data):
        if isinstance(data, dt.date):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, Decimal):
            return float(data)

        raise TypeError("Unable to serialize %r (type: %s)" % (data, type(data)))

    def dumps(self, data: dict):
        return json.dumps(
            data,
            default=self.default,
            ensure_ascii=False,
        )
