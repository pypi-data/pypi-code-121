# spectrometer

import time
from pyAndorSDK2 import atmcd, atmcd_codes, atmcd_errors
from pyAndorSpectrograph.spectrograph import ATSpectrograph

from . import helpers 
from .measurement_parameters import MeasurementParameters
from .enums import (
    ShutterMode,
    FilterPosition,
    Grating,
    ReadOutRate,
    PreampGain,
    ShiftSpeed,
    AcquisitionType
)


class Spectrometer:
    """
    Andor spectrometer controller.
    """
    def __init__(
        self,
        params = None,
        exit_safe = True,
        atmcd_lib: str = None,
        spec_lib: str = None,
    ):
        """
        :param params: Initial measurement parameters.
        :param exit_safe: Whether to shutdown safely by default.
            [Default: True]
        :param atmcd_lib: Path to atmcd library (pyAndorSDK2).
            If None, uses default library provided by package based on the operating system and architecture.
            [Default: None]
        :param spec_lib: Path to spectrometer library (pyAndorSpectrograph).
            If None, uses default library provided by package based on the operating system and architecture.
            [Default: None]
        """
        self.exit_safe = exit_safe

        # initialize camera and spectrometer
        if spec_lib is None:
            spec_lib = helpers.library_path('spectrometer')

        if atmcd_lib is None:
            atmcd_lib = helpers.library_path('sdk')

        self.spectrometer = ATSpectrograph(spec_lib)
        self.camera = atmcd(atmcd_lib)

        spec_init = self.spectrometer.Initialize('')
        cam_init = self.camera.Initialize('')

        helpers.handle_ats_error(spec_init, 'Could not initialize spectrometer')
        helpers.handle_atmcd_error(cam_init, 'Could not initialize camera')

        # initialize measurement parameters
        if params is None:
            params = MeasurementParameters()

        self.params = params
        self.synchronize_spectrometer_parameters()

        # wavelength to pixel mapping
        # retreived at first measurement
        # and after center has been changed
        self._wavelengths = None


    def __del__(self):
        # ensure proper shutdown
        self.shutdown()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()


    @property
    def wavelengths(self):
        """
        :returns: List of wavelength for the pixel at that index.
        """
        return self._wavelengths
    

    # acquisition
    @property
    def acquisition_type(self) -> AcquisitionType:
        return self.params.acquisition_type
    

    @acquisition_type.setter
    def acquisition_type(self, ty: AcquisitionType):
        self.camera.SetAcquisitionType(ty)
        self.params.acquisition_type = ty


    @property
    def acquisition_mode(self) -> atmcd_codes.Acquisition_Mode:
        return self.params.acquisition_mode


    @acquisition_mode.setter
    def acquisition_mode(self, mode: atmcd_codes.Acquisition_Mode):
        self.camera.SetAcquisitionMode(mode.value)
        self.params.acquisition_mode = mode


    def acquisition_single(self):
        """
        [Convenience method]
        Place spectrometer in single scan acquistion mode.
        """
        self.acquisition_mode = atmcd_codes.Acquisition_Mode.SINGLE_SCAN


    def acquisition_accumulate(self):
        """
        [Convenience method]
        Place spectrometer in accumulation acquistion mode.
        """
        self.acquisition_mode = atmcd_codes.Acquisition_Mode.ACCUMULATE


    def acquisition_kinetic(self):
        """
        [Convenience method]
        Place spectrometer in kinetic scan acquistion mode.
        """
        self.acquisition_mode = atmcd_codes.Acquisition_Mode.KINETIC
            

    # accumulation settings
    @property
    def accumulation_scans(self) -> int:
        """
        :returns: Number of scans per accumulation.
        """
        return self.params.accumulation_scans


    @accumulation_scans.setter
    def accumulation_scans(self, scans: int):
        """
        Sets the number of scans to be performed during an accumulation.

        :param scans: Number of scans to perform.
        """
        self.camera.SetNumberAccumulations(scans)
        self.params.accumulation_scans = scans


    @property
    def accumulation_cycle_time(self) -> float:
        return self.params.accumulation_cycle_time


    @accumulation_cycle_time.setter
    def accumulation_cycle_time(self, cycle_time: float):
        self.camera.SetAccumulationCycleTime(cycle_time)
        self.params.accumulation_cycle_time = cycle_time


    # read mode
    @property
    def read_mode(self) -> atmcd_codes.Read_Mode:
        return self.params.read_mode

    
    @read_mode.setter
    def read_mode(self, mode: atmcd_codes.Read_Mode):
        self.camera.SetReadMode(mode.value)
        self.params.read_mode = mode


    def full_vertical_binning(self):
        """
        [Convenience method]
        Places the camera in full vertical binning (FVB) mode.
        """
        self.read_mode = atmcd_codes.Read_Mode.FULL_VERTICAL_BINNING


    # trigger modes
    @property
    def trigger_mode(self) -> atmcd_codes.Trigger_Mode:
        return self.params.trigger_mode
    

    @trigger_mode.setter
    def trigger_mode(self, mode: atmcd_codes.Trigger_Mode):
        self.camera.SetTriggerMode(mode.value)
        self.params.trigger_mode = mode


    def trigger_internal(self):
        self.trigger_mode = atmcd_codes.Trigger_Mode.INTERNAL
        

    def trigger_external(self):
        self.trigger_mode = atmcd_codes.Trigger_Mode.EXTERNAL
        

    # exposure time
    @property
    def exposure_time(self) -> float:
        return self.params.exposure_time


    @exposure_time.setter
    def exposure_time(self, exp_time: float):
        self.camera.SetExposureTime(exp_time)
        self.params.exposure_time = exp_time
    

    # center wavelength
    @property
    def center_wavelength(self) -> float:
        return self.params.center_wavelength


    @center_wavelength.setter
    def center_wavelength(self, center: float):
        # @todo: validate wavelength within range
        if center < 0:
            raise ValueError( "Wavelength can not be negative." )

        self.spectrometer.SetWavelength(0, center)
        self.params.center_wavelength = center

        # reset wavelengths
        self._wavelengths = None


    # filter
    @property
    def filter(self) -> FilterPosition:
        return self.params.filter
    

    @filter.setter
    def filter(self, filt: FilterPosition):
        self.spectrometer.SetFilter(0, filt.value)
        self.params.filter = filt
        

    # grating
    @property
    def grating(self) -> Grating:
        return self.params.grating
    

    @grating.setter
    def grating(self, grating: Grating):
        self.spectrometer.SetGrating(0, grating.value)
        self.params.grating = grating

        
    # read out rate
    @property
    def read_out_rate(self) -> ReadOutRate:
        return self.params.read_out_rate


    @read_out_rate.setter
    def read_out_rate(self, rate: ReadOutRate):
        self.camera.SetHorizontalSpeed(rate.value)
        self.params.read_out_rate = rate
    

    # preamp gain
    @property
    def preamp_gain(self) -> PreampGain:
        return self.params.preamp_gain
    

    @preamp_gain.setter
    def preamp_gain(self, gain: PreampGain):
        self.camera.SetPreAmpGain(gain)
        self.params.pre_amp_gain = gain


    # shift speed
    @property
    def shift_speed(self) -> ShiftSpeed:
        return self.param.shift_speed


    @shift_speed.setter
    def shift_speed(self, speed: ShiftSpeed):
        self.camera.SetVSSpeed(speed.value)
        self.params.shift_speed = speed


    # shutter
    @property
    def shutter_mode(self) -> ShutterMode:
        return self.params.shutter_mode


    @shutter_mode.setter
    def shutter_mode(self, mode: ShutterMode):
        self.camera.SetShutter(1, mode.value, 0, 0)
        self.params.shutter_mode = mode
        

    def close_shutter(self):
        """
        [Convenience method]
        Closes the shutter.
        """
        self.shutter_mode = ShutterMode.CLOSE


    def open_shutter(self):
        """
        [Convenience method]
        Opens the shutter.
        """
        self.shutter_mode = ShutterMode.OPEN


    def automatic_shutter(self):
        """
        [Convenience method]
        Places the shutter in automatic mode.
        """
        self.shutter_mode = ShutterMode.AUTOMATIC


    # temperature
    @property
    def temperature(self) -> float:
        msg, temp = self.camera.GetTemperature()
        return temp


    @temperature.setter
    def temperature(self, temp: float):
        self.camera.SetTemperature(temp)
        self.params.temperature = temp


    def enable_cooler(self):
        self.camera.CoolerON()
        self.cooler_enabled = True


    def disable_cooler(self):
        self.camera.CoolerOFF()
        self.cooler_enabled = False


    def synchronize_spectrometer_parameters(self):
        """
        Synchronizes the spectrometer's settrings with those of the instance.
        """
        # See https://andor.oxinst.com/downloads/uploads/Andor_Software_Development_Kit_2.pdf for more details on every possible parameters
        self.acquisition_mode = self.params.acquisition_mode
        self.accumulation_scans = self.params.accumulation_scans
        self.accumulation_cycle_time = self.params.accumulation_cycle_time
        self.read_mode = self.params.read_mode
        self.trigger_mode = self.params.trigger_mode
        
        (self.ret, self.xpixels, self.ypixels) = self.camera.GetDetector()
        
        self.exposure_time = self.params.exposure_time
        self.center_wavelength = self.params.center_wavelength
        self.filter = self.params.filter
        self.center_wavelength = self.params.center_wavelength
        self.grating = self.params.grating
        self.read_out_rate = self.params.read_out_rate
        self.preamp_gain = self.params.preamp_gain
        self.shift_speed = self.params.shift_speed
        self.shutter_mode = self.params.shutter_mode
        self.temperature = self.params.temperature
        
        
    def acquire(self):
        """
        Acquires a measurement.

        :returns: Numpy array of the measurement.
        """
        # remember original settings
        o_type = self.acquisition_type

        # acquire spectra
        self.acquisition_type = AcquisitionType.SIGNAL

        self.camera.PrepareAcquisition()
        self.camera.StartAcquisition()
        res = self.camera.WaitForAcquisition()
        helpers.handle_atmcd_error(res, 'Acquisition error')

        # @todo: Can be removed?
        # NumberImage = 0
        # while NumberImage < 1:
        #     (ret, First, NumberImage) = self.camera.GetNumberAvailableImages()
        #     time.sleep(0.1)

        (res, data_arr, validfirst, validlast) = self.camera.GetImages16(1, 1, self.xpixels)
        helpers.handle_atmcd_error(res, 'Could not retrieve images')

        if self._wavelengths is None:
            image_size = self.xpixels

            (res, xsize, ysize) = self.camera.GetPixelSize()
            helpers.handle_atmcd_error(res, 'Could not retrieve sensor size')

            self.spectrometer.SetNumberPixels(0, image_size)
            self.spectrometer.SetPixelWidth(0, xsize)
            (res, wavelengths) = self.spectrometer.GetCalibration(0, image_size)
            helpers.handle_ats_error(res)

            self._wavelengths = wavelengths

        # return settings
        self.acquisition_type = o_type

        return data_arr


    def background(self):
        """
        Acquires a background measurement.

        :returns: Numpy array of the measurement.
        """
        # remember original settings
        o_shutter = self.shutter_mode
        o_type = self.acquisition_type

        # take background
        self.acquisition_type = AcquisitionType.BACKGROUND
        self.close_shutter()
        time.sleep(0.01)
        
        bg = self.acquire()
        
        # return settings
        self.shutter_mode = o_shutter 
        self.acquisition_type = o_type

        return bg


    def shutdown(self, safe = None):
        """
        :param safe: Wait for sensor temperature to warm sufficiently before shutting down.
            If None uses the `exit_safe` settings.
            [Default: None] 
        """
        self.disable_cooler()
        
        # safe shutdown
        if safe is None:
            safe = self.exit_safe

        if safe:
            while self.temperature < -15:
                # wait for camera to warm up sufficiently
                time.sleep(10)

        self.camera.ShutDown()
        self.spectrometer.Close()
