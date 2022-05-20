import logging
import time as ttime
from typing import Tuple

from ophyd import Component as Cpt
from ophyd import Device, EpicsSignal, EpicsSignalRO
from ophyd import FormattedComponent as FCpt
from ophyd.status import SubscriptionStatus

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)


class VectorSignalWithRBV(EpicsSignal):
    """
    An EPICS signal that uses 'pvname-SP' for the setpoint and
    'pvname-I' for the read-back
    """

    def __init__(self, prefix, **kwargs):
        super().__init__(f"{prefix}-I", write_pv=f"{prefix}-SP", **kwargs)


class VectorMotor(Device):
    #
    # Configuration
    #

    # Start position of this motor (in EGU)
    start = FCpt(VectorSignalWithRBV, "{prefix}Pos:{motor_name}Start")

    # End position of this motor (in EGU)
    end = FCpt(VectorSignalWithRBV, "{prefix}Pos:{motor_name}End")

    #
    # Status
    #

    # If true, indicates that the requested motion exceeds the max speed for this motor
    too_fast = FCpt(EpicsSignalRO, "{prefix}Sts:{motor_name}TooFast-Sts")

    #
    # Debugging: calculated motion characteristics
    #

    # Acceleration (ct/ms^2)
    accel = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}Accel-I")

    # Distance travelled during data acquisition motion (ct)
    daq_dist = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}DataAcqDist-I")

    # Desired speed (ct/ms)
    des_speed = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}DesSpeed-I")

    # Time it will take to reach the desired speed (ms)
    time_to_speed = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}TimeToSpeed-I")

    # Motion direction (+1 or -1)
    direction = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}Dir-I")

    # Distance travelled during speedup motion (ct)
    speedup_dist = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}SpeedUpDist-I")

    # Distance travelled during buffer motion (ct)
    buffer_dist = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}BufferDist-I")

    # Distance travelled while the shutter is opening  (ct)
    shutter_open_dist = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}ShutOpenDist-I")

    # Distance travelled during backup motion (ct)
    backup_dist = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}BackUpDist-I")

    # Distance travelled while waiting for the shutter lag (ct)
    shutter_lag_dist = FCpt(EpicsSignalRO, "{prefix}Val:{motor_name}ShutLagDist-I")

    def __init__(self, prefix, motor_name=None, **kwargs):
        self.motor_name = motor_name
        super().__init__(prefix, **kwargs)


class VectorProgram(Device):
    """
    Wraps PVs that control the vector program.
    """

    def __init__(self, *args, **kwargs):
        self.ready = False
        super().__init__(*args, **kwargs)

    #
    # Configuration
    #

    # Exposure per sample (ms)
    exposure = Cpt(VectorSignalWithRBV, "Val:Exposure")

    # Number of samples
    num_samples = Cpt(VectorSignalWithRBV, "Val:NumSamples")

    # "Buffer" motion time (ms)
    buffer_time = Cpt(VectorSignalWithRBV, "Val:BufferTime")

    # Shutter opening / closing time (ms)
    shutter_time = Cpt(VectorSignalWithRBV, "Val:ShutTime")

    # Shutter lag (ms)
    shutter_lag_time = Cpt(VectorSignalWithRBV, "Val:ShutLagTime")

    # Whether to expose (whether to open the shutter during acquisition)
    expose = Cpt(EpicsSignal, "Expose-Sel")

    # Whether to actually execute the motion
    # If calc_only==True, no motion is performed but the vector profile is calculated
    # (useful for debugging)
    calc_only = Cpt(EpicsSignal, "CalcOnly-Sel")

    # Whether to pause the vector after backing up but before the start of the motion
    hold = Cpt(EpicsSignal, "Hold-Sel")

    #
    # Individual motor configuration / status
    #

    # Omega motor
    o = Cpt(VectorMotor, "", motor_name="O")

    # X motor
    x = Cpt(VectorMotor, "", motor_name="X")

    # Y motor
    y = Cpt(VectorMotor, "", motor_name="Y")

    # Z motor
    z = Cpt(VectorMotor, "", motor_name="Z")

    #
    # Debugging
    #

    # Calculated data acquisition duration (ms)
    data_acq_duration = Cpt(EpicsSignalRO, "Val:DataAcqDuration-I")

    # Calculated maximum time to reach desired speeds (ms)
    max_time_to_speed = Cpt(EpicsSignalRO, "Val:MaxTimeToSpeed-I")

    #
    # Status
    #

    # Indicates whether a vector motion is running
    active = Cpt(EpicsSignalRO, "Sts:Running-Sts")

    # Current state of the vector:
    #   Idle, Backup, Holding or Acquiring
    state = Cpt(EpicsSignalRO, "Sts:State-Sts", string=True)

    # Error reported by the vector program:
    #   None, Aborted, Zero Exposure, Too Fast, Zero Shutter, Too Slow
    error = Cpt(EpicsSignalRO, "Sts:Error-Sts")

    #
    # Commands
    #

    # Start a vector motion
    go = Cpt(EpicsSignal, "Cmd:Go-Cmd")

    # Proceed with the vector motion when it is paused
    # Only needed if hold==True
    proceed = Cpt(EpicsSignal, "Cmd:Proceed-Cmd")

    # Abort the current vector motion
    abort = Cpt(EpicsSignal, "Cmd:Abort-Cmd")

    # Set all vector motors start and end position to their current RBV values
    sync = Cpt(EpicsSignal, "Cmd:Sync-Cmd")

    def prepare_move(
        self,
        o: Tuple[float, float],
        x: Tuple[float, float],
        y: Tuple[float, float],
        z: Tuple[float, float],
        exposure_ms: float,
        num_samples: float,
        buffer_time_ms: float,
        shutter_lag_time_ms: float,
        shutter_time_ms: float,
    ):

        # Configure motion
        self.sync.put(1)

        self.calc_only.put(True)
        self.expose.put(True)
        self.hold.put(False)

        self.exposure.put(exposure_ms)
        self.num_samples.put(num_samples)
        self.buffer_time.put(buffer_time_ms)
        self.shutter_lag_time.put(shutter_lag_time_ms)
        self.shutter_time.put(shutter_time_ms)

        self.o.start.put(o[0])
        self.o.end.put(o[1])

        self.x.start.put(x[0])
        self.x.end.put(x[1])

        self.y.start.put(y[0])
        self.y.end.put(y[1])

        self.z.start.put(z[0])
        self.z.end.put(z[1])

        # Start "motion"
        self.go.put(1)

        # There's no way to know it is done, so wait a little, it should be very fast
        ttime.sleep(1.0)

        # Check for errors
        error = str(self.error.get())
        error_message = self.error.get(as_string=True)

        if error != "0":
            raise Exception(f"\nFailed to run vector.\nError: {error}\n" f"Error message: {error_message}")

        # Estimate total motion time (in ms)

        time_to_speed = int(self.max_time_to_speed.get())
        buffer_time = int(self.buffer_time.get())
        shutter_time = int(self.shutter_time.get())
        daq_duration = int(self.data_acq_duration.get())

        estimated_total_time_ms = 2 * time_to_speed + buffer_time + 2 * shutter_time + daq_duration
        self.timeout = 5 * estimated_total_time_ms / 1000.0
        self.ready = True

    def move(self):
        logger.debug("move: start")
        if not self.ready:
            raise Exception("Must execute prepare_move command before move is allowed.")
        # Start actual motion
        self.calc_only.put(False)

        # Note: 'kwargs' are needed here as extra information is passed to the callback, such as:
        # kwargs: {'timestamp': 1638904545.824989,
        #          'status': <AlarmStatus.NO_ALARM: 0>,
        #          'severity': <AlarmSeverity.NO_ALARM: 0>,
        #          'enum_strs': ('No', 'Yes'),
        #          'sub_type': 'value',
        #          'obj': EpicsSignalRO(read_pv='XF:19IDC-ES{Gon:1-Vec}Sts:Running-Sts',
        #                               name='vector_active', parent='vector', value=0,
        #                               timestamp=1638904545.824989, auto_monitor=False,
        #                               string=False)}
        def start_callback(value, old_value, **kwargs):
            logger.debug(f"move start_callback: {old_value} -> {value}")
            if (old_value == "Backup" and value == "Acquiring") or (old_value == "Idle" and value == "Acquiring"):
                logger.debug(f"move start_callback: Successfully changed {old_value} -> {value}")
                return True
            else:
                logger.debug(f"move start_callback: changing {old_value} -> {value}...")
                return False

        run_status = SubscriptionStatus(self.state, start_callback, run=True)
        logger.debug(f"Subscribed to {self.active.name}")

        self.go.put(1)
        logger.debug("Go.put(1)")

        return run_status

    def track_move(self):
        logger.debug("track_move: start")

        def finished_callback(value, old_value, **kwargs):
            logger.debug(f"track_move finished_callback: {old_value} -> {value}")
            if old_value == "Acquiring" and value == "Idle":
                logger.debug(f"track_move finished_callback: Successfully changed {old_value} -> {value}")
                return True
            else:
                logger.debug(f"track_move finished_callback: Changing {old_value} -> {value}...")
                return False

        run_status = SubscriptionStatus(self.state, finished_callback, run=True)
        logger.debug(f"Subscribed to {self.state.name}")
        return run_status
