import base64
import io
import json
import pickle
from typing import Any, Dict

import numpy


class JSONEncoder(json.JSONEncoder):
    """Encode CoSApp object for JSON serialization."""

    def default(self, obj):
        if isinstance(obj, bytes):
            return "data:text/plain;base64," + base64.b64encode(obj).decode("utf-8")
        elif isinstance(obj, numpy.ndarray):
            buf = io.BytesIO()
            numpy.save(buf, obj)
            return "data:application/vnd.numpy.ndarray;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')
        elif hasattr(obj, '__json__'):
            return getattr(obj, '__json__')()
        else:
            try:
                pickled_data = pickle.dumps(obj, protocol=4)
            except (pickle.PicklingError, RecursionError):
                return super(JSONEncoder, self).default(obj)
            else:
                return "data:application/vnd.python3.pickle;base64," + base64.b64encode(pickled_data).decode('utf-8')


def decode_cosapp_dict(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert JSON serialization back."""

    for key, value in document.items():
        if isinstance(value, dict):
            document[key] = decode_cosapp_dict(value)
        elif isinstance(value, str):
            if value.startswith("data:"):
                meta, data = value.split(",", maxsplit=1)
                meta = meta[5:].lower()

                if meta.endswith(";base64"):
                    data = base64.b64decode(bytes(data, encoding="utf-8"))

                if meta.startswith("text/plain;"):
                    document[key] = data
                elif meta.startswith("application/vnd.numpy.ndarray;"):
                    buf = io.BytesIO(data)
                    document[key] = numpy.load(buf)
                elif meta.startswith("application/vnd.python3.pickle;"):
                    document[key] = pickle.loads(data)
                else:
                    raise ValueError(f"Unknown data type {meta}.")

    return document
