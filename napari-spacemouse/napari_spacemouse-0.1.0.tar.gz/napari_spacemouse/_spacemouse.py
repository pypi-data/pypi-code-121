"""Forked and modified from https://github.com/johnhw/pyspacenavigator

MIT License (MIT)
Copyright (c) 2015 johnhw

(forked for multi-platform support, typing, and distribution)

[For the SpaceNavigator]
The HID data is in the format
[id, a, b, c, d, e, f]
each pair (a,b), (c,d), (e,f) is a 16 bit signed value representing the absolute
device state [from -350 to 350]

if id==1, then the mapping is
(a,b) = y translation
(c,d) = x translation
(e,f) = z translation

if id==2 then the mapping is
(a,b) = x tilting (roll)
(c,d) = y tilting (pitch)
(d,e) = z tilting (yaw)

if id==3 then the mapping is
a = button. Bit 1 = button 1, bit 2 = button 2

Each movement of the device always causes two HID events, one
with id 1 and one with id 2, to be generated, one after the other.
"""
from __future__ import annotations

import atexit
import contextlib
import copy
import threading
import timeit
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypedDict,
)

import hid

if TYPE_CHECKING:

    class hid_device:
        def open(
            self,
            vendor_id: int = 0,
            product_id: int = 0,
            serial_number: Optional[str] = None,
        ) -> None:
            ...

        def read(self, max_length: int, timeout_ms: int = 0) -> List[int]:
            ...

        def close(self) -> None:
            ...

        def write(self, buff: Iterable[int]) -> None:
            ...

        def get_manufacturer_string(self) -> str:
            ...

        def get_serial_number_string(self) -> str:
            ...

        def get_product_string(self) -> str:
            ...

    class HIDDevDict(TypedDict):
        path: bytes
        vendor_id: int
        product_id: int
        serial_number: str
        release_number: int
        manufacturer_string: str
        product_string: str
        usage_page: int
        usage: int
        interface_number: int


# clock for timing
get_time = timeit.default_timer


def to_int16(y1: int, y2: int) -> int:
    """Simple HID code to read data from the 3dconnexion devices

    convert two 8 bit bytes to a signed 16 bit integer
    """
    x = (y1) | (y2 << 8)
    if x >= 32768:
        x = -(65536 - x)
    return x


class AxisSpec(NamedTuple):
    """Axis mappings.

    axis mappings are specified as: [channel, byte1, byte2, scale]; scale is usually
    just -1 or 1 and multiplies the result by this value (but per-axis scaling can also
    be achieved by setting this value) byte1 and byte2 are indices into the HID array
    indicating the two bytes to read to form the value for this axis For the
    SpaceNavigator, these are consecutive bytes following the channel number.
    """

    channel: int
    byte1: int
    byte2: int
    scale: int


class ButtonSpec(NamedTuple):
    """Button mappings

    button states are specified as:
    [channel, data byte,  bit of byte, index to write to]
    If a message is received on the specified channel, the value of the data byte
    is set in the button bit array
    """

    byte: int
    bit: int
    hint: str = ""


class ButtonState(list):
    def __int__(self):
        return sum((b << i) for (i, b) in enumerate(reversed(self)))


class MouseState(NamedTuple):
    # tuple for 6DOF results
    t: float
    x: int
    y: int
    z: int
    roll: int
    pitch: int
    yaw: int
    buttons: ButtonState

    def fmt(self) -> str:
        return " ".join(
            [f"{k:>5s} {v:+.2f}" for k, v in self._asdict().items() if k != "buttons"]
        )


class _StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, dev: DeviceSpec, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dev = dev
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped():
            try:
                self._dev.read(8, timeout_ms=100)
            except OSError:
                return


@dataclass
class DeviceSpec:
    """Holds the specification of a single 3Dconnexion device.

    Parameters
    ----------
    name : str
        Name of device.
    hid_id : Tuple[int, int]
        2-tuple of (vendorID, productID)
    led_id : Tuple[int, int]
        2-tuple of LED HID usage code pair
    mappings : AxisMappings
        mapping of {axis_name -> AxisSpec}. Axis names are x, y, z, roll, pitch, yaw.
    button_mapping : Sequence[ButtonSpec]
        ButtonsSpecs supported by the device.
    axis_scale : float, optional
        Axis scale supported by the device, by default 350.0
    """

    name: str
    hid_id: Tuple[int, int]
    led_id: Tuple[int, int]
    mappings: Dict[str, AxisSpec]
    button_mapping: Sequence[ButtonSpec]
    axis_scale: float = 350.0
    _device: Optional[hid_device] = None

    def __post_init__(self):

        # initialise to a vector of 0s for each state
        self.dict_state = {
            "t": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "roll": 0,
            "pitch": 0,
            "yaw": 0,
            "buttons": ButtonState([0] * len(self.button_mapping)),
        }
        self.tuple_state = MouseState(**self.dict_state)  # type: ignore

        # start in disconnected state
        self.callback: Optional[Callable[[MouseState], Any]] = None
        self.button_callback: Optional[Callable[[MouseState], Any]] = None
        self._thread: Optional[_StoppableThread] = None

    def describe_connection(self) -> str:
        """Return string representation of the device, including the connection state"""
        if self._device is None:
            return f"{self.name} [disconnected]"
        return (
            f"{self.name} connected to {self.vendor_name} {self.product_name} "
            f"[serial: {self.serial_number}]"
        )

    @property
    def connected(self) -> bool:
        """True if the device has been connected"""
        return self._device is not None

    @property
    def state(self) -> Optional[MouseState]:
        """Return the current/last state of the device."""
        return self.tuple_state if self.connected else None

    def open(self):
        """Open a connection to the device, if possible"""
        if self._device is None:
            self._device: hid_device = hid.device()
            try:
                self._device.open(*self.hid_id)
            except OSError as e:
                raise OSError(
                    f"Failed to open/access {self.name!r} device. "
                    "Please check that the device is available and unused. On macOS, "
                    "check that '3DconnexionHelper' is not running in Activity Monitor."
                ) from e
            self.product_name = self._device.get_product_string()
            self.vendor_name = self._device.get_manufacturer_string()
            # self.serial_number = self._device.get_serial_number_string()
            self.serial_number = ""

    def close(self) -> None:
        """Close the connection, if it is open"""
        if self._device is not None:
            self.stop()
            self._device.close()
            self._device = None

    def read(self, max_length: int = 8, timeout_ms=0) -> MouseState:
        if not self._device:
            raise RuntimeError("not connected")
        self.process(self._device.read(max_length, timeout_ms))
        return self.tuple_state

    def process(self, data: Sequence[int]):
        """
        Update the state based on the incoming data

        This function updates the state of the DeviceSpec object, giving values for each
        axis [x,y,z,roll,pitch,yaw] in range [-1.0, 1.0]
        The state tuple is only set when all 6 DoF have been read correctly.

        The timestamp (in fractional seconds since the start of the program)
        is written as element "t"

        If callback is provided, it is called on with a copy of the current state tuple.
        If button_callback is provided, it is called only on button state changes with
        the argument (state, button_state).

        Parameters:
            data    The data for this HID event, as returned by the HID callback

        """
        if not data:
            return

        channel = data[0]
        self.dict_state["t"] = get_time()

        if channel == CHANNEL.BTN:
            btns: ButtonState = self.dict_state["buttons"]  # type: ignore
            for button_index, (byte, bit, _) in enumerate(self.button_mapping):
                # update the button vector
                btns[button_index] = 1 if (data[byte] & 1 << bit) != 0 else 0
        else:
            for name, (chan, b1, b2, flip) in self.mappings.items():
                if channel == chan:
                    val = flip * to_int16(data[b1], data[b2]) / float(self.axis_scale)
                    self.dict_state[name] = val

        # must receive both channels of the 6DOF state before we update state
        if channel != CHANNEL.XYZ:
            self.tuple_state = MouseState(**self.dict_state)  # type: ignore

        # call any attached callbacks
        if channel == CHANNEL.BTN:
            if self.button_callback:
                self.button_callback(self.tuple_state)
        elif channel == CHANNEL.PRY:
            if self.callback:
                self.callback(self.tuple_state)

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def run(self):
        self._thread = _StoppableThread(self, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread is not None:
            self._thread.stop()
            self._thread.join()
            self._thread = None


class CHANNEL:
    XYZ = 1
    PRY = 2
    BTN = 3


# the IDs for the supported devices
# Each ID maps a device name to a DeviceSpec object
DEVICE_SPECS = {
    "SpaceNavigator": DeviceSpec(
        name="SpaceNavigator",
        hid_id=(0x46D, 0xC626),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=2, byte1=1, byte2=2, scale=-1),
            "roll": AxisSpec(channel=2, byte1=3, byte2=4, scale=-1),
            "yaw": AxisSpec(channel=2, byte1=5, byte2=6, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=1, bit=0, hint="LEFT"),
            ButtonSpec(byte=1, bit=1, hint="RIGHT"),
        ],
        axis_scale=350.0,
    ),
    "SpaceMouse Compact": DeviceSpec(
        name="SpaceMouse Compact",
        hid_id=(0x256F, 0xC635),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=2, byte1=1, byte2=2, scale=-1),
            "roll": AxisSpec(channel=2, byte1=3, byte2=4, scale=-1),
            "yaw": AxisSpec(channel=2, byte1=5, byte2=6, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=1, bit=0, hint="LEFT"),
            ButtonSpec(byte=1, bit=1, hint="RIGHT"),
        ],
        axis_scale=350.0,
    ),
    "SpaceMouse Pro Wireless": DeviceSpec(
        name="SpaceMouse Pro Wireless",
        hid_id=(0x256F, 0xC632),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=1, byte1=7, byte2=8, scale=-1),
            "roll": AxisSpec(channel=1, byte1=9, byte2=10, scale=-1),
            "yaw": AxisSpec(channel=1, byte1=11, byte2=12, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=1, bit=0, hint="MENU"),
            ButtonSpec(byte=3, bit=7, hint="ALT"),
            ButtonSpec(byte=4, bit=1, hint="CTRL"),
            ButtonSpec(byte=4, bit=0, hint="SHIFT"),
            ButtonSpec(byte=3, bit=6, hint="ESC"),
            ButtonSpec(byte=2, bit=4, hint="1"),
            ButtonSpec(byte=2, bit=5, hint="2"),
            ButtonSpec(byte=2, bit=6, hint="3"),
            ButtonSpec(byte=2, bit=7, hint="4"),
            ButtonSpec(byte=2, bit=0, hint="ROLL CLOCKWISE"),
            ButtonSpec(byte=1, bit=2, hint="TOP"),
            ButtonSpec(byte=4, bit=2, hint="ROTATION"),
            ButtonSpec(byte=1, bit=5, hint="FRONT"),
            ButtonSpec(byte=1, bit=4, hint="REAR"),
            ButtonSpec(byte=1, bit=1, hint="FIT"),
        ],
        axis_scale=350.0,
    ),
    "SpaceMouse Pro": DeviceSpec(
        name="SpaceMouse Pro",
        hid_id=(0x46D, 0xC62B),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=2, byte1=1, byte2=2, scale=-1),
            "roll": AxisSpec(channel=2, byte1=3, byte2=4, scale=-1),
            "yaw": AxisSpec(channel=2, byte1=5, byte2=6, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=1, bit=0, hint="MENU"),
            ButtonSpec(byte=3, bit=7, hint="ALT"),
            ButtonSpec(byte=4, bit=1, hint="CTRL"),
            ButtonSpec(byte=4, bit=0, hint="SHIFT"),
            ButtonSpec(byte=3, bit=6, hint="ESC"),
            ButtonSpec(byte=2, bit=4, hint="1"),
            ButtonSpec(byte=2, bit=5, hint="2"),
            ButtonSpec(byte=2, bit=6, hint="3"),
            ButtonSpec(byte=2, bit=7, hint="4"),
            ButtonSpec(byte=2, bit=0, hint="ROLL CLOCKWISE"),
            ButtonSpec(byte=1, bit=2, hint="TOP"),
            ButtonSpec(byte=4, bit=2, hint="ROTATION"),
            ButtonSpec(byte=1, bit=5, hint="FRONT"),
            ButtonSpec(byte=1, bit=4, hint="REAR"),
            ButtonSpec(byte=1, bit=1, hint="FIT"),
        ],
        axis_scale=350.0,
    ),
    "SpaceMouse Wireless": DeviceSpec(
        name="SpaceMouse Wireless",
        hid_id=(0x256F, 0xC62E),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=1, byte1=7, byte2=8, scale=-1),
            "roll": AxisSpec(channel=1, byte1=9, byte2=10, scale=-1),
            "yaw": AxisSpec(channel=1, byte1=11, byte2=12, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=1, bit=0, hint="LEFT"),
            ButtonSpec(byte=1, bit=1, hint="RIGHT"),
        ],
        axis_scale=350.0,
    ),
    "3Dconnexion Universal Receiver": DeviceSpec(
        name="3Dconnexion Universal Receiver",
        hid_id=(0x256F, 0xC652),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=1, byte1=7, byte2=8, scale=-1),
            "roll": AxisSpec(channel=1, byte1=9, byte2=10, scale=-1),
            "yaw": AxisSpec(channel=1, byte1=11, byte2=12, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=1, bit=0, hint="MENU"),
            ButtonSpec(byte=3, bit=7, hint="ALT"),
            ButtonSpec(byte=4, bit=1, hint="CTRL"),
            ButtonSpec(byte=4, bit=0, hint="SHIFT"),
            ButtonSpec(byte=3, bit=6, hint="ESC"),
            ButtonSpec(byte=2, bit=4, hint="1"),
            ButtonSpec(byte=2, bit=5, hint="2"),
            ButtonSpec(byte=2, bit=6, hint="3"),
            ButtonSpec(byte=2, bit=7, hint="4"),
            ButtonSpec(byte=2, bit=0, hint="ROLL CLOCKWISE"),
            ButtonSpec(byte=1, bit=2, hint="TOP"),
            ButtonSpec(byte=4, bit=2, hint="ROTATION"),
            ButtonSpec(byte=1, bit=5, hint="FRONT"),
            ButtonSpec(byte=1, bit=4, hint="REAR"),
            ButtonSpec(byte=1, bit=1, hint="FIT"),
        ],
        axis_scale=350.0,
    ),
    "SpacePilot Pro": DeviceSpec(
        name="SpacePilot Pro",
        hid_id=(0x46D, 0xC629),
        led_id=(0x8, 0x4B),
        mappings={
            "x": AxisSpec(channel=1, byte1=1, byte2=2, scale=1),
            "y": AxisSpec(channel=1, byte1=3, byte2=4, scale=-1),
            "z": AxisSpec(channel=1, byte1=5, byte2=6, scale=-1),
            "pitch": AxisSpec(channel=2, byte1=1, byte2=2, scale=-1),
            "roll": AxisSpec(channel=2, byte1=3, byte2=4, scale=-1),
            "yaw": AxisSpec(channel=2, byte1=5, byte2=6, scale=1),
        },
        button_mapping=[
            ButtonSpec(byte=4, bit=0, hint="SHIFT"),
            ButtonSpec(byte=3, bit=6, hint="ESC"),
            ButtonSpec(byte=4, bit=1, hint="CTRL"),
            ButtonSpec(byte=3, bit=7, hint="ALT"),
            ButtonSpec(byte=3, bit=1, hint="1"),
            ButtonSpec(byte=3, bit=2, hint="2"),
            ButtonSpec(byte=2, bit=6, hint="3"),
            ButtonSpec(byte=2, bit=7, hint="4"),
            ButtonSpec(byte=3, bit=0, hint="5"),
            ButtonSpec(byte=1, bit=0, hint="MENU"),
            ButtonSpec(byte=4, bit=6, hint="-"),
            ButtonSpec(byte=4, bit=5, hint="+"),
            ButtonSpec(byte=4, bit=4, hint="DOMINANT"),
            ButtonSpec(byte=4, bit=3, hint="PAN/ZOOM"),
            ButtonSpec(byte=4, bit=2, hint="ROTATION"),
            ButtonSpec(byte=2, bit=0, hint="ROLL CLOCKWISE"),
            ButtonSpec(byte=1, bit=2, hint="TOP"),
            ButtonSpec(byte=1, bit=5, hint="FRONT"),
            ButtonSpec(byte=1, bit=4, hint="REAR"),
            ButtonSpec(byte=2, bit=2, hint="ISO"),
            ButtonSpec(byte=1, bit=1, hint="FIT"),
        ],
        axis_scale=350.0,
    ),
}


supported_devices = list(DEVICE_SPECS.keys())
_active_device: Optional[DeviceSpec] = None


def close():
    """Close the active device, if it exists"""
    if _active_device is not None:
        _active_device.close()


def read() -> Optional[MouseState]:
    """Return the current state of the active navigation controller."""
    return _active_device.read() if _active_device is not None else None


def run():
    return _active_device.run() if _active_device is not None else None


def stop():
    return _active_device.stop() if _active_device is not None else None


def _find_all_hid_devices() -> List[HIDDevDict]:
    "Finds all HID devices connected to the system"
    return hid.enumerate()


def list_connected_devices() -> List[str]:
    """Return a list of the supported devices connected

    Returns:
        A list of string names of the devices supported which were found.
        Empty if no supported devices found
    """
    devices: Set[str] = set()
    for device in _find_all_hid_devices():
        for device_name, spec in DEVICE_SPECS.items():
            if (device["vendor_id"], device["product_id"]) == spec.hid_id:
                devices.add(device_name)
    return list(devices)


def open(
    callback: Callable[[MouseState], Any] = None,
    button_callback: Callable[[MouseState], Any] = None,
    device: str = None,
) -> DeviceSpec:
    """Open a 3D space navigator device.

    Makes this device the current active device, which enables the module-level read()
    and close() calls. For multiple devices, use the read() and close() calls on the
    returned object instead, and don't use the module-level calls.

    Parameters
    ----------
    callback : Callable, optional
        If callback is provided, it is called on each HID update with a copy of the
        current state namedtuple, by default None
    button_callback : Callable, optional
        If button_callback is provided, it is called on each button push, with the
        arguments (state_tuple, button_state), by default None
    device : str, optional
        name of device to open. Must be one of the values in supported_devices. If None,
        chooses the first supported device found., by default None

    Returns
    -------
    _type_
         Device object if the device was opened successfully

    Raises
    ------
    RuntimeError
        _description_
    """
    # only used if the module-level functions are used
    global _active_device

    # if no device name specified, look for any matching device and choose the first
    if not (_connected := list_connected_devices()):
        raise RuntimeError("No connected devices found.")

    if device is None:
        spec = DEVICE_SPECS[_connected[0]]
    else:
        try:
            spec = DEVICE_SPECS[device]
        except KeyError as e:
            raise KeyError(f"Unrecognized device name {device!r}") from e

    # create a copy of the device specification
    dev = copy.deepcopy(spec)
    dev.callback = callback
    dev.button_callback = button_callback
    dev.open()

    @atexit.register
    def _tryclose():
        with contextlib.suppress(Exception):
            dev.stop()

    _active_device = dev
    return dev


def _main():
    import sys

    with contextlib.suppress(ImportError):
        from rich import print

    def print_state(state: MouseState):
        print(state.fmt())

    if connected := list_connected_devices():
        print("Devices found: ", ", ".join(connected))

        dev = open(callback=print_state, button_callback=None)
        print(dev.describe_connection())

        if dev:
            while True:
                try:
                    dev.read()
                except KeyboardInterrupt:
                    sys.exit()
    else:
        print("nothing connected")


if __name__ == "__main__":
    _main()
