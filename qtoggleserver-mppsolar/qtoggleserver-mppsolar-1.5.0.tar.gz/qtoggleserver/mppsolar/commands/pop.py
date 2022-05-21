
from .base import Command


class POP(Command):
    REQUEST_FMT = 'POP{output_source_priority:02.0f}'
