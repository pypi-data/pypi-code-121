
from .base import Command


class MCHGC(Command):
    REQUEST_FMT = 'MCHGC{battery_max_charging_current:03.0f}'
