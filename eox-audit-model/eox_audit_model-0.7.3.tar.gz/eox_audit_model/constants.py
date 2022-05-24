"""Constants file.

Attributes:
    LOG_FORMAT: Standard output log format.

Classes:
    Status: Possible statuses for eox-audit-model.
"""
from enum import IntEnum

LOG_FORMAT = '%(asctime)s %(levelname)s %(process)d [%(name)s]%(filename)s:%(lineno)d - %(message)s'


class Status(IntEnum):
    """
    Class that defines status for the execution of the hook.
    """
    SUCCESS = 1
    FAIL = 0

    @classmethod
    def choices(cls):
        """Returns choices for the class"""
        return [(key.value, key.name) for key in cls]  # pylint: disable=not-an-iterable, useless-suppression
