""" Status Response Module """
from __future__ import absolute_import
from enum import auto
from yk_utils.models import Error, BaseEnum


class StatusResultType(BaseEnum):
    """
    Camera status operation type.
    """
    CAMERA_OK = auto()
    CAMERA_UNAVAILABLE = auto()
    CAMERA_READ_FAILED = auto()
    CAMERA_RESET_NEEDED = auto()
    CAMERA_OVER_HEATING = auto()
    CAMERA_SENSOR_DAMAGED = auto()
    CAMERA_TIMEOUT = auto()
    CAMERA_OPERATION_IN_PROGRESS = auto()
    NONE = auto()


StatusResponseSchema = \
    {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Description of device status.",
                "enum": StatusResultType.to_str_list()
            }
        }
    }


class StatusResponse(Error):
    """
    Add proper name to message.
    """
