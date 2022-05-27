import datetime
from enum import IntEnum
import os
import time
from time import sleep
from threading import Thread
from typing import Any, cast, Dict, List, Optional, Tuple, Union

import numpy as np

import kamzik3
from kamzik3 import DeviceError, units
from kamzik3.constants import (
    ATTR_FRAME_COUNT,
    ATTR_MACRO_PREFIX,
    ATTR_SCAN_COUNT,
    ATTR_STATUS,
    ATTR_TRIGGERS_GENERATED,
    ATTR_TRIGGER_PULSE_WIDTH,
    ATTR_TRIGGERS_SP,
    STATUS_BUSY,
    STATUS_CONFIGURED,
    STATUS_IDLE,
    UNIT,
    VALUE,
)
from kamzik3.devices.device import Device
from kamzik3.devices.deviceTango import DeviceTango
from kamzik3.devices.general.deviceScanner import DeviceScanner
from kamzik3.macro.macro import Macro
from kamzik3.macro.macroServer import MacroServer
from kamzik3.macro.scan import Scan
from kamzik3.macro.step import Step, StepDeviceMethod
from kamzik3.snippets.snippetsDecorators import expose_method


_FRAMES_PER_FILE_SCAN = 1000
_FRAMES_PER_FILE_LIVE = 1_000_000
# any large number is ok, images are not saved in the live-view mode
_MAX_ACQUISITION_RATE = units.Quantity(133, "Hz")


class InterfaceStatus(IntEnum):
    """Status of the Eiger interface (filewriter, eigerstream, monitor)."""

    ENABLED = 0
    DISABLED = 1


class TriggerMode(IntEnum):
    """
    The trigger modes can be found in Eiger2 documentation (v1.5.0).

    Note that this mapping is valid only at P11, which uses a custom Tango device server
    instead of what FS-EC provides.
    """

    EXTE = 0
    EXTS = 1
    INTE = 2
    INTS = 3


class DeviceTangoEigerDetector(DeviceTango):
    """
    Implementation of the Eiger detector at P11.

    The method acquire_frame of this device can be used to take image(s) without scan.
    For a scan, use the device EigerSwTrigger instead.

    :param path: path of the Tango server, e.g.
     tango://haspp11oh:10000/p11/simplon_detector/eh.01
    :param file_writer: instance of a Simplon FileWriter Tango device
    :param eiger_stream: instance of a Simplon Stream Tango device
    :param device_id: str, the name to give to this device
    :param config: a dictionary of configuration parameters
    """

    def __init__(
        self,
        path: str,
        file_writer: Optional[Device] = None,
        eiger_stream: Optional[Device] = None,
        device_id: Optional[str] = None,
        config: Optional[Dict[Tuple[str, str], Any]] = None,
    ) -> None:
        self.file_writer = file_writer
        self.eiger_stream = eiger_stream
        DeviceTango.__init__(self, path, device_id, config)

    def handle_configuration(self) -> None:
        """Configure the Eiger device."""
        try:
            super().handle_configuration()
            self.check_interface()
            if self.file_writer is not None:
                self.share_group(self.file_writer, None, "FileWriter")
            if self.eiger_stream is not None:
                self.share_group(self.eiger_stream, None, "EigerStream")
        except self.tango_exceptions:
            # Exception was handled on DeviceTango level
            pass

    def check_interface(self) -> None:
        """
        Check the configuration of the Eiger interface.

        Either the FileWriter or the Streaming interface has to be enabled (not both).

        Mode 0=enabled, 1=Disabled
        """
        if (
            self.file_writer is not None
            and self.file_writer.get_value("Mode") == str(InterfaceStatus.ENABLED.value)
            and self.eiger_stream is not None
            and self.eiger_stream.get_value("Mode")
            == str(InterfaceStatus.ENABLED.value)
        ):
            raise DeviceError(
                "Enable either the File Writer or the Streaming Interface, not both"
            )

        if self.file_writer is None and self.eiger_stream is None:
            raise DeviceError("No interface provided for the Eiger!")

    def _init_attributes(self) -> None:
        DeviceTango._init_attributes(self)
        self.create_attribute("shotDir")
        self.create_attribute("scanDir")
        self.create_attribute("scanFilenamePattern")
        self.create_attribute(
            ATTR_FRAME_COUNT,
            default_value=0,
            readonly=True,
            description="Internal frame counter",
            default_type=np.uint64,
            min_value=0,
        )

    def _config_interface(
        self, saving_directory: str, prefix: str, nb_frames: int = 1
    ) -> None:
        """
        Configure the Eiger interface.

        :param saving_directory: str, the name of the saving directory
        :param prefix: str, prefix to add to the file names (filewriter) or folder name
         for the dataset (stream subsystem)
        :param nb_frames: int, number of frames to be saved per .h5 file for the
         Filewiter
        """
        now = datetime.datetime.now()
        if self.file_writer is not None:
            path = os.path.join(
                self.get_value(saving_directory),
                f"{prefix}_{self.device_id}_{now.strftime('%Y-%m-%d_%H:%M:%S')}",
            )
            self.set_attribute(
                ["FileWriter", "Mode", VALUE], InterfaceStatus.ENABLED.value
            )
            self.set_attribute(["FileWriter", "NamePattern", VALUE], path)
            self.set_attribute(["FileWriter", "NimagesPerFile", VALUE], nb_frames)
        else:  # use the Stream subsystem
            path = '{"series_name": "' + prefix + '"}'
            self.set_attribute(
                ["EigerStream", "Mode", VALUE], InterfaceStatus.ENABLED.value
            )
            self.set_attribute(["EigerStream", "HeaderAppendix", VALUE], path)
            self.set_attribute(["EigerStream", "ImageAppendix", VALUE], path)

    @expose_method({"Name": "FilePrefix", "Exposure": "FrameTime", "Frames": "Nimages"})
    def acquire_frame(self, Name: str, Exposure: str, Frames: str) -> None:
        nb_frames = int(self.to_device_unit("Nimages", Frames).m)
        self._config_interface(
            saving_directory="shotDir", prefix=Name, nb_frames=nb_frames
        )

        converted_exposure = self.detector.to_device_unit("FrameTime", Exposure)
        min_frame_time = (1 / _MAX_ACQUISITION_RATE).to(
            self.get_value("FrameTime", key=UNIT)
        )
        if converted_exposure < min_frame_time:
            self.logger.error(
                f"Can't acquire data faster than {_MAX_ACQUISITION_RATE}, "
                "defaulting to it"
            )
            frame_time = min_frame_time.m
        else:
            frame_time = float(converted_exposure.m)

        self.set_attribute(["TriggerMode", VALUE], TriggerMode.INTS.value)
        self.set_attribute(["FrameTime", VALUE], frame_time)
        self.set_attribute(["CountTime", VALUE], float(converted_exposure.m))
        self.set_attribute(["Ntrigger", VALUE], 1)
        self.set_attribute(["Nimages", VALUE], nb_frames)
        self.Arm()
        self.Trigger()
        self.set_value(ATTR_FRAME_COUNT, self.get_value(ATTR_FRAME_COUNT) + nb_frames)

    @expose_method({"Exposure": "FrameTime"})
    def live_view(self, Exposure: str) -> None:
        """
        Live view of the Eiger detector.

        This is useful when aligning the optics or the sample. Images will not be saved.

        :param Exposure: desired exposure time per frame
        """
        self.logger.info("Live view has started.")
        self.set_attribute(["TriggerMode", VALUE], TriggerMode.INTS.value)
        if self.file_writer is not None:
            self.logger.info("FileWriter disabled")
            self.set_attribute(
                ["FileWriter", "Mode", VALUE], InterfaceStatus.DISABLED.value
            )
            self.set_attribute(
                ["FileWriter", "NimagesPerFile", VALUE], _FRAMES_PER_FILE_LIVE
            )
        if self.eiger_stream is not None:
            self.logger.info("EigerStream disabled")
            self.set_attribute(
                ["EigerStream", "Mode", VALUE], InterfaceStatus.DISABLED.value
            )

        converted_exposure = self.detector.to_device_unit("FrameTime", Exposure)
        min_frame_time = (1 / _MAX_ACQUISITION_RATE).to(
            self.get_value("FrameTime", key=UNIT)
        )
        if converted_exposure < min_frame_time:
            self.logger.error(
                f"Can't acquire data faster than {_MAX_ACQUISITION_RATE}, "
                "defaulting to it"
            )
            frame_time = min_frame_time.m
        else:
            frame_time = float(converted_exposure.m)

        self.set_attribute(["FrameTime", VALUE], frame_time)
        self.set_attribute(["CountTime", VALUE], float(converted_exposure.m))
        self.set_attribute(["Ntrigger", VALUE], 1)
        self.set_attribute(["Nimages", VALUE], _FRAMES_PER_FILE_LIVE)
        self.Arm()
        self.Trigger()
        self.set_value(
            ATTR_FRAME_COUNT, self.get_value(ATTR_FRAME_COUNT) + _FRAMES_PER_FILE_LIVE
        )

    @expose_method()
    def stop(self) -> None:
        """
        Stop the acquisition.

        It is necessary to call Disarm() if the detector acquisition is stopped manually
        because it forces the filewriter to go back to ON (otherwise it stays RUNNING).
        """
        if self.get_value(ATTR_STATUS) == STATUS_BUSY:
            self.logger.info("Acquisition aborted")
            self.Abort()
            self.Disarm()


class EigerTrigger(Device):
    """
    Base class for triggering the Eiger detector.

    The method _acquisition_thread needs to be overriden depending on which trigger
    is used.
    """

    def __init__(
        self,
        detector: DeviceTangoEigerDetector,
        device_id: Optional[str] = None,
        config: Optional[Dict[Tuple[str, str], Any]] = None,
    ) -> None:
        self.detector = detector
        Device.__init__(self, device_id, config)
        self.connect()

    def handle_configuration(self) -> None:
        start_at = time.time()
        self._config_attributes()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def _init_attributes(self) -> None:
        Device._init_attributes(self)
        self.create_attribute(
            ATTR_TRIGGERS_SP,
            default_value=0,
            description="Number of triggers to generate",
            default_type=np.uint64,
            min_value=0,
        )
        self.create_attribute(
            ATTR_TRIGGERS_GENERATED,
            default_value=0,
            readonly=True,
            description="Number of generated triggers",
            default_type=np.uint64,
            min_value=0,
        )
        self.create_attribute(
            ATTR_TRIGGER_PULSE_WIDTH,
            default_value=0,
            description="Width of the trigger pulse",
            default_type=np.float64,
            min_value=0,
            decimals=3,
            unit="sec",
        )

    @expose_method({"Exposure": ATTR_TRIGGER_PULSE_WIDTH, "Frames": ATTR_TRIGGERS_SP})
    def acquire_frame(self, Exposure: str, Frames: str) -> None:
        nb_frames = self.to_device_unit(ATTR_TRIGGERS_SP, Frames).m
        exposure_time = self.to_device_unit(ATTR_TRIGGER_PULSE_WIDTH, Exposure).m
        self.set_value(ATTR_TRIGGERS_SP, nb_frames)
        self.set_value(ATTR_TRIGGER_PULSE_WIDTH, exposure_time)
        self.set_value(ATTR_TRIGGERS_GENERATED, 0)
        Thread(target=self._acquisition_thread).start()

    def _acquisition_thread(self) -> None:
        raise NotImplementedError

    @expose_method()
    def stop(self) -> None:
        self.set_value(ATTR_STATUS, STATUS_IDLE)
        self.detector.stop()


class EigerSwTrigger(EigerTrigger):
    """
    Use this class as the Device in the macro templates if you want to do a scan, with
    the EigerSwScanner as the Scanner.

    This class expects that the trigger mode is set as INTS (see the method
    EigerSwScanner._init_new_scan). In that mode, the detector records nimages frames
    per trigger and stays armed until ntrigger are received.
    """

    def _acquisition_thread(self) -> None:
        self.set_status(STATUS_BUSY)
        while (
            self.get_value(ATTR_TRIGGERS_GENERATED) != self.get_value(ATTR_TRIGGERS_SP)
            and self.get_value(ATTR_STATUS) == STATUS_BUSY
        ):
            self.detector.Trigger()
            sleep(self.get_value(ATTR_TRIGGER_PULSE_WIDTH))
            self.set_value(
                ATTR_TRIGGERS_GENERATED, self.get_value(ATTR_TRIGGERS_GENERATED) + 1
            )
        self.set_status(STATUS_IDLE)


class EigerSwScanner(DeviceScanner):
    def __init__(
        self,
        detector: DeviceTangoEigerDetector,
        device_id: Optional[str] = None,
        config: Optional[Dict[Tuple[str, str], Any]] = None,
    ) -> None:
        self.detector = detector
        DeviceScanner.__init__(self, device_id, config)
        self.connect()

    @staticmethod
    def _recount_steps(
        parent_macro: Macro, to_link: Optional[Union[Scan, Step]] = None
    ) -> int:
        total_frames = 1
        for link in parent_macro.chain:
            if link == to_link:
                break
            if isinstance(link, Scan) and total_frames > 0:
                repeat_step = link.step_attributes.get("repeat_count", 0) + 1
                repeat_scan = link.repeat_count + 1
                total_frames *= (link.steps_count + 1) * repeat_step * repeat_scan
            else:
                total_frames *= link.get_total_points_count()
        return total_frames

    @expose_method()
    def get_scanner_attributes(self) -> List[str]:
        return []

    def on_macro_done(self) -> None:
        self.detector.stop()

    @expose_method()
    def get_scanner_macro(
        self,
        scanner_input: StepDeviceMethod,
        scanner_attributes: Dict[str, Any],
        parent_macro: Macro,
    ) -> StepDeviceMethod:
        if kamzik3.session is None:
            raise DeviceError(
                "kamzik session is None, can't get the device MacroServer"
            )
        macro_server = cast(MacroServer, kamzik3.session.get_device("MacroServer"))
        current_scan_count = macro_server.get_macro_count()
        if current_scan_count != self.last_scan_count:
            self._init_new_scan(scanner_input, scanner_attributes, parent_macro)
            self.last_scan_count = current_scan_count
        scanner_input.on_macro_done = self.on_macro_done  # type:ignore
        # see https://github.com/python/mypy/issues/2427
        return scanner_input

    def _init_new_scan(
        self,
        scanner_input: StepDeviceMethod,
        scanner_attributes: Dict[str, Any],
        parent_macro: Macro,
    ) -> None:
        if kamzik3.session is None:
            raise DeviceError("kamzik session is None, can't get the scan number")
        self.logger.info(
            "Initiating new scan number {}".format(
                kamzik3.session.get_value(ATTR_SCAN_COUNT)
            )
        )
        macro_server = cast(MacroServer, kamzik3.session.get_device("MacroServer"))
        scan_prefix = macro_server.get_value(ATTR_MACRO_PREFIX)
        scan_count = macro_server.get_macro_count()
        scan_dir_name = "{}_{}".format(scan_prefix, scan_count - 1)

        params = scanner_input.method_parameters
        if any(val not in params for val in ["Exposure", "Frames"]):
            raise DeviceError(
                "The input parameters 'Exposure' and 'Frames' are required in"
                f"scanner_input, got {params.keys()}"
            )
        converted_exposure = units.Quantity(params["Exposure"]).to(
            self.detector.get_value("FrameTime", key=UNIT)
        )
        min_frame_time = (1 / _MAX_ACQUISITION_RATE).to(
            self.get_value("FrameTime", key=UNIT)
        )
        if converted_exposure < min_frame_time:
            self.logger.error(
                f"Can't acquire data faster than {_MAX_ACQUISITION_RATE}, "
                "defaulting to it"
            )
            frame_time = min_frame_time.m
        else:
            frame_time = float(converted_exposure.m)

        self.detector.set_attribute(["FrameTime", VALUE], frame_time)
        self.detector.set_attribute(["CountTime", VALUE], float(converted_exposure.m))

        frames_count = int(float(params["Frames"]))
        total_frames = self._recount_steps(parent_macro, scanner_input) * frames_count

        self.detector.set_value(ATTR_FRAME_COUNT, 0)
        self.detector.set_attribute(["TriggerMode", VALUE], TriggerMode.INTS.value)
        self.detector.set_attribute(["Nimages", VALUE], frames_count)
        self.detector.set_attribute(["Ntrigger", VALUE], total_frames)

        path = os.path.join(
            self.detector.get_value("scanDir"), scan_dir_name, f"{scan_dir_name}"
        )
        self.detector.set_attribute(
            ["FileWriter", "Mode", VALUE], InterfaceStatus.ENABLED.value
        )
        self.detector.set_attribute(["FileWriter", "NamePattern", VALUE], path)
        self.detector.set_attribute(
            ["FileWriter", "NimagesPerFile", VALUE], _FRAMES_PER_FILE_SCAN
        )

        self.detector.Arm()
