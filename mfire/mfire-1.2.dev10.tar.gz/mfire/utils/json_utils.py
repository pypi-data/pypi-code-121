"""
Custom JSON utilities
"""
from datetime import datetime, timedelta
import json
from io import IOBase
from typing import Any, Union

import numpy as np
from pydantic import BaseModel

Jsonable = Union[
    dict, list, tuple, str, int, float, bool, datetime, timedelta, BaseModel
]


class MFireJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder made to easily encode types commonly used in MFire:
            - pydantic.BaseModel
            - datetime.datetime (and custom Datetime in extenso)
            - datetime.timedelta (and custom Timedelta in extenso)
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return json.loads(obj.json(encoder=self.default))
        if isinstance(obj, (datetime, timedelta, np.datetime64, np.timedelta64)):
            return str(obj)
        if isinstance(obj, slice):
            bounds = [obj.start, obj.stop, obj.step]
            return [b for b in bounds if b is not None]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class JsonFile:
    """Custom class for handling text or binary files containing JSON documents.
    This custom class uses the MFireJSONEncoder by default for the dumping process.

    Args:
        filename (Union[str, IOBase]): JSON file's name
        binary (bool, optional): Whether the given file is a binary one or not.
            Defaults to False.
    """

    def __init__(self, filename: Union[str, IOBase]) -> None:
        self.filename = filename

    def load(self, **kwargs) -> Jsonable:
        """Opens a text or binary file containing a JSON document and deserialize it
        to a Python object.

        Returns:
            Jsonable: Deserialized object
        """
        if isinstance(self.filename, IOBase):
            return json.load(self.filename, **kwargs)

        with open(self.filename, "r") as fp:
            return json.load(fp, **kwargs)

    def dump(self, obj: Jsonable, **kwargs) -> None:
        """Serialize obj as a JSON formatted and export it to a text file.
        It uses the MFireJSONEncoder by default.

        Args:
            obj (Jsonable): Serialized object.
        """
        encoder = kwargs.pop("cls", MFireJSONEncoder)
        ensure_ascii = kwargs.pop("ensure_ascii", False)
        if isinstance(self.filename, IOBase):
            return json.dump(
                obj, self.filename, ensure_ascii=ensure_ascii, cls=encoder, **kwargs
            )

        with open(self.filename, "w") as fp:
            return json.dump(obj, fp, ensure_ascii=ensure_ascii, cls=encoder, **kwargs)
