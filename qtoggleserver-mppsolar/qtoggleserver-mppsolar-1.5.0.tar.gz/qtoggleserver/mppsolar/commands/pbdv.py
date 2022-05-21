
from .base import Command


class PBDV(Command):
    REQUEST_FMT = 'PBDV{battery_back_to_discharging_voltage:04.1f}'
