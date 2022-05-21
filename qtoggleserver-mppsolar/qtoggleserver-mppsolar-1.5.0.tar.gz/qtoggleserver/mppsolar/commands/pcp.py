
from .base import Command


class PCP(Command):
    REQUEST_FMT = 'PCP{charging_source_priority:02.0f}'
