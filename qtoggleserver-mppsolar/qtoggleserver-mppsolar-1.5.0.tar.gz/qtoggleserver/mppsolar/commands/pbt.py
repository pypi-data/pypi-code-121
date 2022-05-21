
from .base import Command


class PBT(Command):
    REQUEST_FMT = 'PBT{battery_type:02.0f}'
