""" Hardware Reset Request Module """
from __future__ import absolute_import
from enum import auto
from yk_utils.models import Error, BaseEnum


class HardwareResetResultType(BaseEnum):
    """
    Camera status operation type.
    """
    CAMERA_RESET_OK = auto()
    CAMERA_RESET_FAILED = auto()
    CAMERA_OPERATION_IN_PROGRESS = auto()
    NONE = auto()


HardwareResetResponseSchema = \
    {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Result of the hardware reset operation.",
                "enum": HardwareResetResultType.to_str_list()
            }
        }
    }


class HardwareResetResponse(Error):
    """
    Add proper name to message.
    """
