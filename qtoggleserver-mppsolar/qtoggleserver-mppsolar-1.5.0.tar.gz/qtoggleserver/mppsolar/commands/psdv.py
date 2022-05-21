
from .base import Command


class PSDV(Command):
    REQUEST_FMT = 'PSDV{battery_cut_off_voltage:04.1f}'
