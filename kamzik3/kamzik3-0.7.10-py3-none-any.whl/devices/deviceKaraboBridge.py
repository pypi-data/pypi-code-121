import time
from threading import Thread, Event
from time import sleep

import numpy as np

import kamzik3
from kamzik3 import units, DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetDataAccess import get_from_dict, set_in_dict
from kamzik3.snippets.snippetsDecorators import expose_method

try:
    from karabo_bridge import Client as KbClient
except ImportError:
    raise DeviceError("karabo_bridge import error!")


class DeviceKaraboBridge(Device):
    karabo_client = None

    def __init__(self, host, port, device_id=None, config=None):
        self.host = host
        self.port = port
        self.stop_auto_refresh = Event()
        self.counter_running = False
        self.stop_auto_refresh.clear()
        super().__init__(device_id, config)
        self.connect()

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(
            ATTR_REFRESHING, default_value=False, readonly=True, default_type=bool
        )

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...

        :param args: connect attributes
        """
        self.connecting = True
        self.karabo_client = KbClient("tcp://{}:{}".format(self.host, self.port))
        self.handle_configuration_event()
        self.connected = True
        self.connecting = False

    def handle_configuration(self):
        start_at = time.time()
        self._update_attributes()
        self._config_commands()
        self._config_attributes()
        self.start_polling()
        self.set_status(STATUS_CONFIGURED)
        self.auto_refresh()
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def _update_attributes(self):
        """
        To make things general, I'm just getting one next() call from Karabo bridge.

        Saving for now only floats and integer values.
        Ignoring numpy arrays.
        """
        data, metadata = self.karabo_client.next()

        for key, value in data.items():
            self.attributes[key] = {}
            decimals = 0

            for sub_key, sub_value in value.items():
                if isinstance(sub_value, int):
                    default_type = np.int64
                elif isinstance(sub_value, float):
                    default_type = np.float64
                    decimals = 6
                else:
                    continue
                self.create_attribute(
                    sub_key,
                    key,
                    default_value=sub_value,
                    readonly=True,
                    default_type=default_type,
                    decimals=decimals,
                )

        self.create_attribute(
            ATTR_MIN_UPDATE_TIMEOUT,
            default_value=0,
            default_type=np.float64,
            unit="ms",
            decimals=0,
        )
        self.create_attribute(
            ATTR_TRAIN_TIMEOUT,
            default_value=100,
            default_type=np.float64,
            unit="ms",
            decimals=0,
        )
        self.create_attribute(
            ATTR_REMOTE_TIMESTAMP,
            default_type=np.float64,
            unit="sec",
            readonly=True,
            decimals=6,
        )
        self.create_attribute(
            ATTR_LOCAL_TIMESTAMP,
            default_type=np.float64,
            unit="sec",
            readonly=True,
            decimals=6,
        )
        self.create_attribute(
            ATTR_DELTA_TIMESTAMP,
            default_value=0,
            default_type=np.int64,
            unit="ms",
            readonly=True,
            decimals=6,
        )
        self.create_attribute(
            ATTR_COUNTER,
            default_value=0,
            default_type=np.uint16,
            set_value_when_set_function=False,
            set_function=self.count_trains,
        )
        self.create_attribute(
            ATTR_LOCAL_TRAIN_ID, default_value=0, default_type=np.int64, readonly=True
        )
        self.create_attribute(
            ATTR_REMOTE_TRAIN_ID, default_value=0, default_type=np.int64, readonly=True
        )
        self.create_attribute(ATTR_TRAIN_OFFSET, default_value=0, default_type=np.int64)

        self.update_metadata(list(metadata.values())[0])

    def _set(self, attribute, value, callback=None):
        """
        This sets Device attribute.

        Use this function when You want to set attribute by tuple or list key.
        Example: Device.set((ATTR_STATUS, VALUE), STATUS_IDLE)
        Attribute value is pushed into server if Device is connected on any.
        To reduce amount of pushed attributes we check if value is different from previous one.

        :param attribute: tuple, list, str
        :param value: mixed
        """
        token = 0
        if isinstance(attribute, (tuple, list)):
            current_value = get_from_dict(self.attributes, attribute)
            if isinstance(value, np.ndarray):
                if np.array_equal(value, current_value):
                    return
            elif value == current_value and attribute[0] != ATTR_COUNTER:
                return

            set_in_dict(self.attributes, attribute, value)
            if attribute[-1] == VALUE:
                # Get new value possibly affected by offset and factor
                value = get_from_dict(self.attributes, attribute)
            token = "{}.{}".format(TOKEN_ATTRIBUTE, ".".join(attribute))
        else:
            current_value = self.attributes[attribute]
            if isinstance(value, np.ndarray):
                if np.array_equal(value, current_value):
                    return
            elif value == current_value and attribute[0] != ATTR_COUNTER:
                return

            self.attributes[attribute] = value
            if attribute == VALUE:
                # Get new value possibly affected by offset and factor
                value = self.attributes[attribute]
            token = "{}.{}".format(TOKEN_ATTRIBUTE, attribute)

        if (
            token
            and kamzik3.session.publisher is not None
            and not isinstance(value, np.ndarray)
        ):
            kamzik3.session.publisher.push_message(
                self.device_id, (attribute, value), token
            )

    def command(self, command, callback=None, with_token=False, returning=True):
        raise DeviceError("Device does not accept any commands.")

    def count_trains(self, counts):
        self.reset_counter()
        start_train = self.get_value(ATTR_LOCAL_TRAIN_ID)

        def counter(counts):
            self.set_status(STATUS_BUSY)
            counted = 0
            self.counter_running = True
            while counted < counts and self.counter_running:
                counted = self.get_value(ATTR_LOCAL_TRAIN_ID) - start_train
                self.set_raw_value(ATTR_COUNTER, counted)
                sleep(0.02)
            self.set_raw_value(ATTR_COUNTER, counts)
            self.counter_running = False
            self.set_status(STATUS_IDLE)

        Thread(target=counter, args=[counts]).start()

    @expose_method()
    def reset_counter(self):
        self.set_value(ATTR_COUNTER, 0)

    @expose_method()
    def refresh(self):
        """Get one next() call from Karabo bridge."""
        start_time = time.time()
        self.set_attribute([ATTR_REFRESHING, VALUE], True)

        def _thread():
            self.karabo_next()
            end_time = time.time() - start_time
            self.set_value(ATTR_LATENCY, end_time * 1e3)
            self.set_attribute([ATTR_REFRESHING, VALUE], False)

        Thread(target=_thread).start()

    @expose_method()
    def auto_refresh(self):
        """
        Start routine which will automatically call next() until stopped.

        To save CPU and potentially bandwidth set ATTR_MIN_UPDATE_TIMEOUT attribute.
        Take into account, that next() is blocking!
        """
        self.reset_counter()
        if self.get_attribute([ATTR_REFRESHING, VALUE]):
            return

        self.logger.info("Starting auto refresh routine")
        self.set_attribute([ATTR_REFRESHING, VALUE], True)
        self.stop_auto_refresh.clear()

        def _thread():
            while not self.stop_auto_refresh.is_set():
                start_time = time.time()
                self.karabo_next()
                end_time = time.time() - start_time
                sleep_for = (
                    self[ATTR_MIN_UPDATE_TIMEOUT][VALUE] - end_time * 1e3
                ) / 1e3
                if sleep_for > 0:
                    sleep(sleep_for)
                self.set_value(ATTR_LATENCY, end_time * 1e3)

            self.set_attribute([ATTR_REFRESHING, VALUE], False)
            self.logger.info("Auto refresh routine stopped")

        Thread(target=_thread).start()

    def karabo_next(self):
        """
        Get one next() call from Karabo bridge.

        Take into account, that next() is blocking!
        """
        data, metadata = self.karabo_client.next()
        for key, value in data.items():
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, (int, float)):
                    self.set_value([key, sub_key], sub_value)
        self.update_metadata(list(metadata.values())[0])

    def update_metadata(self, metadata_values):
        """
        This routine is important to get and correct train ID from Karabo bridge.

        ATTR_REMOTE_TRAIN_ID: Karabo train ID
        ATTR_REMOTE_TIMESTAMP: Karabo timestamp
        ATTR_LOCAL_TIMESTAMP: Local computer timestamp
        ATTR_DELTA_TIMESTAMP: Delta timestamp
        (ATTR_LOCAL_TIMESTAMP - ATTR_REMOTE_TIMESTAMP)

        ATTR_TRAIN_OFFSET: User configurable train offset

        ATTR_LOCAL_TRAIN_ID: Interpolated train id using delta timestamp.
        train_id_delta = ATTR_DELTA_TIMESTAMP / ATTR_TRAIN_TIMEOUT
        (ATTR_REMOTE_TRAIN_ID + train_id_delta + ATTR_TRAIN_OFFSET)
        """
        remote_timestamp, local_timestamp = (
            np.float64(metadata_values["timestamp"]),
            time.time(),
        )
        time_delta = (local_timestamp - remote_timestamp) * 1e3
        train_id_delta = (
            units.Quantity(time_delta, "ms") / self[ATTR_TRAIN_TIMEOUT].value()
        )
        self.set_attribute(
            (ATTR_REMOTE_TRAIN_ID, VALUE), metadata_values["timestamp.tid"]
        )
        self.set_attribute((ATTR_REMOTE_TIMESTAMP, VALUE), remote_timestamp)
        self.set_attribute((ATTR_LOCAL_TIMESTAMP, VALUE), np.float64(time.time()))
        self.set_attribute((ATTR_DELTA_TIMESTAMP, VALUE), time_delta)
        self.set_attribute(
            (ATTR_LOCAL_TRAIN_ID, VALUE),
            int(
                round(
                    metadata_values["timestamp.tid"]
                    + train_id_delta.m
                    + self[ATTR_TRAIN_OFFSET][VALUE]
                )
            ),
        )

    @expose_method()
    def stop(self):
        """Stop auto refresh routine by setting stop_auto_refresh flag."""
        self.logger.info("Stopping auto refresh routine")
        self.counter_running = False
        self.stop_auto_refresh.set()

    def close(self):
        self.stop()
        return super().close()
