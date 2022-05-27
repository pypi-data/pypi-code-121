from pydantic import BaseModel, PrivateAttr
from brevettiai.io import io_tools, IoTools


class IoBaseModel(BaseModel):
    """ Model with private io tools"""
    _io: IoTools = PrivateAttr(default=None)

    def __init__(self, io=io_tools, **data) -> None:
        super().__init__(**data)
        self._io = io

    @property
    def io(self):
        return self._io
