from enum import Enum


class ErrorMitigationMethod(str, Enum):
    COMPLETE_CALIBRATION = "Complete Calibration"
    TENSORED_CALIBRATION = "Tensored Calibration"
