from dataclasses import dataclass
from pyAndorSDK2.atmcd_codes import (
    Acquisition_Mode,
    Read_Mode,
    Trigger_Mode
)

from .enums import (
    ShutterMode,
    FilterPosition,
    Grating,
    ReadOutRate,
    PreampGain,
    ShiftSpeed,
    AcquisitionType
)


@dataclass
class MeasurementParameters:
        temperature: float = -70
        exposure_time: float = 0.01
        center_wavelength: float = 850
        
        acquisition_mode: Acquisition_Mode = Acquisition_Mode.ACCUMULATE
        acquisition_type: AcquisitionType = AcquisitionType.SIGNAL

        accumulation_scans: int = 5
        accumulation_cycle_time: float = 0.03
        
        read_mode: Read_Mode = Read_Mode.FULL_VERTICAL_BINNING
        trigger_mode: Trigger_Mode = Trigger_Mode.INTERNAL
        
        filter: FilterPosition = FilterPosition.LPF700
        grating: Grating = Grating.G300

        read_out_rate: ReadOutRate = ReadOutRate.kHz50
        preamp_gain: PreampGain = PreampGain.x1_7
        shift_speed: ShiftSpeed = ShiftSpeed.ssp32_25
        shutter_mode: ShutterMode = ShutterMode.AUTOMATIC
