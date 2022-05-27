import datetime
import os
import pathlib
import time
from threading import Thread
import numpy as np

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.dummy.deviceDummy import DeviceDummy
from kamzik3.devices.dummy.dummyDetector import DummyDetector
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units


class DeviceDummyEiger(DummyDetector):
    """
    Implementation of a dummy Eiger detector.

    TriggerMode 0 corresponds to "EXTE" in Eiger documentation.
    TriggerMode 3 corresponds to "INTS" in Eiger documentation.
    """

    def __init__(
        self, path, file_writer=None, eiger_stream=None, device_id=None, config=None
    ):
        self.path = path
        self.file_writer = file_writer
        self.eiger_stream = eiger_stream
        DummyDetector.__init__(self, device_id=device_id, config=config)

    def _init_attributes(self):
        DummyDetector._init_attributes(self)
        self.create_attribute("NamePattern", readonly=False)
        self.create_attribute("shotDir", default_value="./")
        self.create_attribute("scanDir", default_value="./")
        self.create_attribute("scanFilenamePattern")
        self.create_attribute(
            "Nimages", default_value=1, default_type=np.uint, min_value=1
        )
        self.create_attribute(
            "Ntrigger", default_value=1, default_type=np.uint, min_value=1
        )
        self.create_attribute(
            ATTR_FRAME_COUNT,
            default_value=0,
            readonly=True,
            description="Internal frame counter",
            default_type=np.uint64,
            min_value=0,
        )
        self.create_attribute(
            "TriggerMode",
            default_value=1,
            default_type=np.uint,
            min_value=1,
            max_value=3,
        )
        self.create_attribute(
            "FrameTime",
            default_value=0.001,
            default_type=np.float,
            min_value=0.001,
            max_value=9999,
            decimals=3,
            unit="s",
        )
        self.create_attribute(
            "CountTime",
            default_value=0.001,
            default_type=np.float,
            min_value=0.001,
            max_value=9999,
            decimals=3,
            unit="s",
            set_function=lambda v: self.set_value(ATTR_EXPOSURE_TIME, v),
        )

    def handle_configuration(self):
        start_at = time.time()
        self._config_attributes()
        self.check_interface()
        if self.file_writer is not None:
            self.share_group(self.file_writer, None, "FileWriter")
        if self.eiger_stream is not None:
            self.share_group(self.eiger_stream, None, "EigerStream")
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def check_interface(self):
        """
        Check the configuration of the Eiger interface.

        Either the FileWriter or the Streaming interface has to be enabled (not both).

        Mode 0=enabled, 1=Disabled
        """
        if (
            self.file_writer is not None
            and self.file_writer.get_value("Mode") == "0"
            and self.eiger_stream is not None
            and self.eiger_stream.get_value("Mode") == "0"
        ):
            raise DeviceError(
                "Enable either the File Writer or the Streaming Interface, not both"
            )

        if self.file_writer is None and self.eiger_stream is None:
            raise DeviceError("No interface provided for the Eiger!")

    @expose_method({"Name": "FilePrefix", "Exposure": "FrameTime", "Frames": "Nimages"})
    def acquire_frame(self, Name, Exposure, Frames):
        now = datetime.datetime.now()
        Frames = device_units(self, "Nimages", Frames).m
        self.set_attribute(["TriggerMode", VALUE], 3)

        if self.file_writer is not None:
            path = os.path.join(
                self.get_value("shotDir"),
                f"{Name}_{self.device_id}_{now.strftime('%Y-%m-%d_%H:%M:%S')}",
            )
            self.set_attribute(["FileWriter", "Mode", VALUE], 0)
            self.set_attribute(["FileWriter", "NamePattern", VALUE], path)
            self.set_attribute(["FileWriter", "NimagesPerFile", VALUE], int(Frames))
        else:  # use the Stream subsystem
            path = '{"series_name": "' + Name + '"}'
            self.set_attribute(["EigerStream", "Mode", VALUE], 0)
            self.set_attribute(["EigerStream", "HeaderAppendix", VALUE], path)
            self.set_attribute(["EigerStream", "ImageAppendix", VALUE], path)

        Exposure = device_units(self, "FrameTime", Exposure).m
        # According to Jan 10ms is lowest frame time
        frame_time = 10e-3 if Exposure < 10e-3 else Exposure
        self.set_attribute(["FrameTime", VALUE], frame_time)
        self.set_attribute(["CountTime", VALUE], float(Exposure))
        self.set_attribute(["Ntrigger", VALUE], int(1))
        self.set_attribute(["Nimages", VALUE], int(Frames))
        self.Arm()
        self.Trigger()
        self.set_value(ATTR_FRAME_COUNT, self.get_value(ATTR_FRAME_COUNT) + int(Frames))

    @expose_method({"Name": "FilePrefix", "Exposure": "FrameTime", "Frames": "Nimages"})
    def acquire_scan_frame(self, Name, Exposure, Frames):
        now = datetime.datetime.now()
        Exposure = float(device_units(self, "FrameTime", Exposure).m)
        if Exposure != self.get_value("CountTime"):
            frame_time = 10e-3 if Exposure < 10e-3 else Exposure
            self.set_attribute(["FrameTime", VALUE], frame_time)
            self.set_attribute(["CountTime", VALUE], Exposure)
        Frames = int(float(device_units(self, "Nimages", Frames).m))
        if Frames != self.get_value("Nimages"):
            self.set_attribute(["Nimages", VALUE], Frames)

        self.set_attribute(["TriggerMode", VALUE], 3)
        if self.file_writer is not None:
            path = os.path.join(
                self.get_value("scanDir"),
                f"{Name}_{self.device_id}_{now.strftime('%Y-%m-%d_%H:%M:%S')}",
            )
            self.set_attribute(["FileWriter", "Mode", VALUE], 0)
            self.set_attribute(["FileWriter", "NimagesPerFile", VALUE], Frames)
            self.set_attribute(["FileWriter", "NamePattern", VALUE], path)

        else:  # use the Stream subsystem
            path = '{"series_name": "' + Name + '"}'
            self.set_attribute(["EigerStream", "Mode", VALUE], 0)
            self.set_attribute(["EigerStream", "HeaderAppendix", VALUE], path)
            self.set_attribute(["EigerStream", "ImageAppendix", VALUE], path)

        self.Arm()
        self.Trigger()
        self.set_value(ATTR_FRAME_COUNT, self.get_value(ATTR_FRAME_COUNT) + int(Frames))

    @expose_method(
        {
            "Name": ATTR_FRAME_NAME,
            "Frames": ATTR_SUMMED_FRAMES,
            "Exposure": ATTR_EXPOSURE_TIME,
        }
    )
    def start_acquisition(self, Name, Frames, Exposure):
        self.acquisition_running.set()
        Frames = device_units(self, ATTR_SUMMED_FRAMES, Frames)
        Exposure = device_units(self, ATTR_EXPOSURE_TIME, Exposure)

        self.set_status(STATUS_BUSY)
        self.set_value(ATTR_FRAME_NAME, Name)
        self.set_value(ATTR_SUMMED_FRAMES, Frames)
        self.set_value(ATTR_EXPOSURE_TIME, Exposure)
        self.set_value(ATTR_ACQUIRED_FRAMES, 0)

        def _acquire():
            exposure_time_increment = 10
            current_exposure_time = 0
            last_frame_number = 0
            while self.acquisition_running.isSet():
                time.sleep(exposure_time_increment * 1e-3)
                current_exposure_time += exposure_time_increment
                acquired_frames = int(current_exposure_time / Exposure.m)
                if last_frame_number != acquired_frames:
                    self.set_value(["Output", "Frame"], self._generate_frame())
                    last_frame_number = acquired_frames

                if acquired_frames >= Frames:
                    self.set_value(ATTR_ACQUIRED_FRAMES, Frames)
                    break
                else:
                    self.set_value(ATTR_ACQUIRED_FRAMES, acquired_frames)

            if self.connected:
                self.acquisition_running.clear()
                self.set_status(STATUS_IDLE)

        Thread(target=_acquire).start()

    @expose_method()
    def Trigger(self):
        self.file_writer._create_dir()
        Name = self.get_value(self.get_value(["FileWriter", "NamePattern"]))
        Frames = self.get_value("Nimages")
        Exposure = self.get_value("CountTime") * 1e3
        self.start_acquisition(Name, Frames, Exposure)

    @expose_method()
    def Arm(self):
        self.set_status(STATUS_BUSY)

    @expose_method()
    def Disarm(self):
        self.set_status(STATUS_IDLE)

    @expose_method()
    def Abort(self):
        self.set_status(STATUS_IDLE)

    @expose_method()
    def stop(self):
        if self.get_value(ATTR_STATUS) == STATUS_BUSY:
            self.Abort()
        DummyDetector.stop(self)


class DeviceDummyEigerWriter(DeviceDummy):
    def __init__(self, path, device_id=None, config=None):
        self.path = path
        DeviceDummy.__init__(self, device_id=device_id, config=config)

    def _init_attributes(self):
        DeviceDummy._init_attributes(self)
        self.create_attribute("NimagesPerFile", default_type=np.uint, min=0)
        self.create_attribute("NamePattern")
        self.create_attribute("Mode", default=0)

    def _create_dir(self):
        pathlib.Path(self.get_value("NamePattern")).parent.mkdir(
            parents=True, exist_ok=True
        )
