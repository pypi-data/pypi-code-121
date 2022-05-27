# -*- coding: UTF-8 -*-

from configparser import ExtendedInterpolation

from .cfgparser import CfgParser
from ..constants import DEFAULTS, BACKUP
from ..utils import evaluate

cfg = CfgParser(
    interpolation=ExtendedInterpolation(),
    converters={
        "list": evaluate,
        "tuple": evaluate,
        "set": evaluate,
        "dict": evaluate,
    }
)
cfg.set_defaults(**DEFAULTS)
cfg.read_dict(dictionary=BACKUP, source="<backup>")

__all__ = ["CfgParser", "cfg"]
