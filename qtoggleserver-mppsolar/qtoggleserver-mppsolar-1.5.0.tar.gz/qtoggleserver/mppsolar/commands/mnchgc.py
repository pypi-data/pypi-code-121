
from .base import Command


class MNCHGC(Command):
    pass


class MNCHGC_Single(MNCHGC):
    REQUEST_FMT = 'MNCHGC{battery_max_charging_current:03.0f}'


class MNCHGC_Parallel(MNCHGC):
    REQUEST_FMT = 'MNCHGC{_parallel_no:d}{battery_max_charging_current:03.0f}'
    REQUEST_DEFAULT_VALUES = {
        '_parallel_no': 0
    }
