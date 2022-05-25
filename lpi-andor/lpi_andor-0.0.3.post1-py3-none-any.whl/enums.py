from enum import IntEnum, unique


@unique
class ShutterMode(IntEnum):
	AUTOMATIC = 0
	OPEN = 1
	CLOSE = 2


@unique
class FilterPosition(IntEnum):
    """
    Filter Position options
    """
    EMPTY = 1
    LPF450 = 2
    LPF700 = 3
    BPF650 = 4
    BPF420 = 5
    ND4 = 6


@unique
class Grating(IntEnum):
    """
    Grating options
    """
    G300 = 1
    G600 = 2


@unique
class ReadOutRate(IntEnum):
    """
    Horizontal read out rate options
    """
    kHz33 = 0
    kHz50 = 1
    kHz100 = 2


@unique
class PreampGain(IntEnum):
    """
    PreampGain options
    """
    x1 = 0
    x1_7 = 1


@unique
class ShiftSpeed(IntEnum):
    """
    Vertical shift speed options
    """
    ssp16_5 = 0
    ssp32_25 = 1
    ssp64_25 = 2


@unique
class AcquisitionType(IntEnum):
	SIGNAL = 0
	BACKGROUND = 1
	REFERENCE = 2
	CALIBRATION = 3