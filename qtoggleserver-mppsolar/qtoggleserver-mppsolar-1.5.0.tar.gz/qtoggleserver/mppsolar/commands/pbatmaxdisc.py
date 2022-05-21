
from .base import Command


class PBATMAXDISC(Command):
    REQUEST_FMT = 'PBATMAXDISC{battery_max_discharging_current:03.0f}'
