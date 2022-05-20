from typing import Dict

from marshmallow.utils import EXCLUDE
from marshmallow_dataclass import dataclass


class BaseSchema:
    @classmethod
    def load(cls, data: Dict, unknown=EXCLUDE, **kwargs):
        return cls.Schema().load(data, unknown=unknown, **kwargs)

    def dump(self, **kwargs):
        return self.Schema(**kwargs).dump(self)
