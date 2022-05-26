#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-11-11
# @Filename: drift.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import importlib
import struct
from collections import defaultdict

from typing import Any, Callable, Optional, Type, cast

from pymodbus.client.asynchronous.async_io import AsyncioModbusTcpClient
from yaml import SafeLoader, load

from drift import adaptors, log
from drift.exceptions import DriftError


__all__ = ["Device", "Relay", "Module", "MODULES", "Drift"]


MODULES = {
    "750-511": {"mode": "holding_register", "channels": 2},
    "750-450": {"mode": "input_register", "channels": 4},
    "750-497": {"mode": "input_register", "channels": 8},
    "750-530": {"mode": "coil", "channels": 8},
}


class CaseInsensitiveDict(dict):
    """A case insensitive dictionary from https://bit.ly/2ZHgTpq."""

    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super().__getitem__(self.__class__._k(key))

    def __setitem__(self, key, value):
        super().__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key):
        return super().__delitem__(self.__class__._k(key))

    def __contains__(self, key):
        return super().__contains__(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super().pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super().get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super().setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, E={}, **F):
        super().update(self.__class__(E))
        super().update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super().pop(k)
            self.__setitem__(k, v)


class Module(object):
    """A Modbus module with some devices connected.

    Parameters
    ----------
    name
        A name to be associated with this module.
    drift
        The instance of `.Drift` used to communicate with the modbus network.
    model
        The Drift model for this module.
    mode
        The type of object (``coil``, ``discrete``, ``input_register``, or
        ``holding_register``). If `None`, will be determined from the model,
        if possible. The ``mode`` of a module is only used if the `.Device` does
        not specify its own ``mode`` since different devices in a module may
        have different modules.
    channels
        The number of channels in this module. If not provided it will be
        determined from ``model``.
    description
        A description or comment for this module.

    """

    def __init__(
        self,
        name: str,
        drift: Drift,
        model: Optional[str] = None,
        mode: Optional[str] = None,
        channels: Optional[int] = None,
        description: str = "",
    ):

        self.name = name
        self.drift = drift

        self.description = description

        self.model = model

        if self.model:
            if self.model in MODULES:
                default_mode = MODULES[self.model]["mode"]
                default_channels = MODULES[self.model]["channels"]
            else:
                raise DriftError(f"Unknown model {self.model!r}")
        else:
            default_mode = None
            default_channels = None

        if mode is not None:
            self.mode = mode
        else:
            self.mode = default_mode

        if self.mode and self.mode not in [
            "coil",
            "discrete",
            "input_register",
            "holding_register",
        ]:
            raise DriftError(f"Invalid mode {mode!r}.")

        self.channels = channels or default_channels
        self.devices = CaseInsensitiveDict()

        log.info(
            f"Created module {self.name} with mode {self.mode!r} "
            f"and {self.channels or '?'} channels."
        )

    def __repr__(self):
        return (
            f"<Module {self.name} (mode={self.mode!r}, "
            f"channels={self.channels or '?'}, n_devices={len(self.devices)})>"
        )

    def __getitem__(self, name: str) -> Device:
        """Gets a device."""

        return self.devices[name]

    def add_device(
        self,
        name: str | Device,
        address: Optional[int] = None,
        device_class: Optional[Type[Device]] = None,
        **kwargs,
    ) -> Device:
        """Adds a device

        Parameters
        ----------
        name
            The name of the device. It is treated as case-insensitive. It can
            also be a `.Device` instance, in which case the remaining
            parameters will be ignored.
        device_class
            Either `.Device` or a subclass of it.
        kwargs
            Other parameters to pass to `.Device`.

        """

        if isinstance(name, Device):

            device = name

        else:

            device_class = device_class or Device

            if name in self.devices:
                raise DriftError(
                    f"Device {name!r} already exists in module {self.name!r}."
                )

            assert address is not None, "address cannot be None"

            device = device_class(self, name, address, **kwargs)

        self.devices[device.name] = device
        log.info(
            f"Added device {device.name} with addres {address} to module {self.name}."
        )

        return device

    def remove_device(self, name: str) -> Device:
        """Removes a device.

        Parameters
        ----------
        name
            The name of the device to remove.

        """

        device = self.devices.pop(name)
        log.info(f"Removed device {name} from module {self.name}.")

        return device


class Device(object):
    """A device connected to a modbus `.Module`.

    Parameters
    ----------
    module
        The `.Module` to which this device is connected to.
    name
        The name of the device. It is treated as case-insensitive.
    address
        The address of the device. This is the address passed to ``pymodbus``
        (i.e., the one encoded in the TCP packet) so it should have any offset
        already removed.
    mode
        The type of object (``coil``, ``discrete``, ``input_register``, or
        ``holding_register``). If `None`, uses the mode from the module.
    channel
        For multi-bit registers, the bit to return. If `None`, returns the entire
        register value.
    category
        A user-defined category for this device. This can be used to group
        devices of similar type from different modules, for example ``'temperature'``
        to indicate temperature sensors.
    offset
        A numerical offset to be added to the read value after running the
        adaptor.
    description
        A description of the purpose of the device.
    units
        The units of the values returned, if an adaptor is used.
    data_type
        The data type for the raw values read. If not set, assumes unsigned
        integer. The format is the same as ``struct`` data types. For example,
        if reading a signed integer use ``h``.
    adaptor
        The adaptor to be used to convert read registers to physical values.
        It can be a string indicating one of the provided :ref:`adaptors
        <adaptors>`, a string with the format ``module1.module2:function``
        (in this case ``module1.module2`` will be imported and ``function``
        will be called), a function or lambda function, or a mapping of
        register value to return value. If the adaptor is a function it must
        accept a raw value from the register and return the physical value,
        or a tuple of ``(value, unit)``.
    adaptor_extra_params
        A tuple of extra parameters to be passed to the adaptor after the
        raw value.

    """

    __type__ = None

    def __init__(
        self,
        module: Module,
        name: str,
        address: int,
        mode: Optional[str] = None,
        channel: Optional[int] = None,
        description: str = "",
        offset: float = 0.0,
        units: Optional[str] = None,
        category: Optional[str] = None,
        data_type: Optional[str] = None,
        adaptor: Optional[str | dict | Callable] = None,
        adaptor_extra_params: tuple[Any] = tuple(),
    ):

        assert isinstance(module, Module), "module not a valid Module object."

        self.module = module
        self.name = name
        self.address = address
        self.channel = channel
        self.description = description
        self.units = units
        self.category = category
        self.offset = offset
        self.data_type = data_type
        self.adaptor = self._parse_adaptor(adaptor)
        self._adaptor_extra_params = adaptor_extra_params

        self.mode = mode or self.module.mode

        if not self.mode:
            raise DriftError(
                f"{self.name}@{self.address}: mode not specified for device or module."
            )

        if self.mode not in [
            "coil",
            "discrete",
            "input_register",
            "holding_register",
        ]:
            raise DriftError(f"Invalid mode {mode!r}.")

        if self.channel is not None and self.module.channels:
            assert self.channel < self.module.channels

        log.info(
            f"Created device {self.name}@{self.address}"
            + (f":{self.channel}." if self.channel is not None else ".")
        )

    def __repr__(self):
        return f"<Device {self.name}@{self.address}" + (
            f":{self.channel}>" if self.channel is not None else ">"
        )

    @staticmethod
    def _parse_adaptor(adaptor):
        """Parses the adaptor."""

        if adaptor is None:
            return None

        elif isinstance(adaptor, str):

            if ":" in adaptor:
                try:
                    module_str, adaptor = adaptor.split(":")
                except ValueError:
                    raise DriftError(f"Badly formatted adaptor {adaptor}.")
                module = importlib.import_module(module_str)
            else:
                module = adaptors

            if hasattr(module, adaptor) is False:
                raise DriftError(f"Cannot find adaptor {adaptor}.")
            else:
                return getattr(module, adaptor)

        elif isinstance(adaptor, (tuple, list, dict)):
            return dict(adaptor)

    @property
    def client(self) -> AsyncioModbusTcpClient | None:
        """Returns the ``pymodbus`` client."""

        return self.module.drift.client

    async def read(
        self,
        adapt=True,
        connect=True,
    ) -> tuple[int | float, None | str]:
        """Reads the value of the coil or register.

        If ``adapt=True`` and a valid adaptor was provided, the value returned
        is the one obtained after applying the conversion function to the
        raw register value. Otherwise returns the raw value.

        If ``connect=False``, the user is responsible for connecting and disconnecting.
        This is sometimes useful for bulk reading, when one does not want to
        recreate the socket for each device.


        Returns
        -------
        read_value
            A tuple in which the first element is the read raw or converted
            value and the second is the associated unit. If ``adapt=False`` no
            units are returned.

        """

        if connect:
            async with self.module.drift:
                return await self._read(adapt=adapt)
        else:
            return await self._read(adapt=adapt)

    async def _read(self, adapt=True):

        assert self.client and self.client.protocol

        protocol = self.client.protocol

        raw_type: str = ""
        if self.mode == "coil":
            reader = protocol.read_coils
            raw_type = "?"
        elif self.mode == "discrete":
            reader = protocol.read_discrete_inputs
            raw_type = "?"
        elif self.mode == "input_register":
            reader = protocol.read_input_registers
            raw_type = "H"
        elif self.mode == "holding_register":
            reader = protocol.read_holding_registers
            raw_type = "H"
        else:
            raise DriftError(f"invalid mode {self.mode!r}.")

        resp = await reader(self.address, count=1)

        if resp.function_code > 0x80:
            raise DriftError(
                f"Invalid response for device "
                f"{self.name!r}: 0x{resp.function_code:02X}."
            )

        if self.mode == "coil" or self.mode == "discrete":
            value = resp.bits[0]
        else:
            value = resp.registers[0]
            if self.channel is not None:
                value = (value & (1 << self.channel)) > 0

        if self.data_type is not None:
            value = struct.unpack(self.data_type, struct.pack(f"={raw_type}", value))[0]

        if not adapt:
            return value

        if adapt and self.adaptor is not None:
            if callable(self.adaptor):
                value = self.adaptor(value, *self._adaptor_extra_params)
            else:
                if value not in self.adaptor:
                    raise DriftError(
                        f"Cannot find associated value for "
                        f"{value} in adaptor mapping."
                    )
                else:
                    value = self.adaptor[value]

        if isinstance(value, (tuple, list)):
            value, units = value
            if units is None:
                units = self.units
        else:
            units = self.units

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            value += self.offset

        return value, units

    async def write(self, value, connect=True) -> bool:
        """Writes values to a coil or register.

        Parameters
        ----------
        value
            The value to write to the device.
        connect
            Whether to connect to the client and disconnect after writing. If
            ``connect=False``, the user is responsible for connecting and disconnecting.
            This is sometimes useful for bulk writing, when one does not want to
            recreate the socket for each device.

        """

        if self.mode != "coil" and self.mode != "holding_register":
            raise DriftError("Writing is not allowed to this device.")

        if connect:
            async with self.module.drift:
                return await self._write(value)
        else:
            return await self._write(value)

    async def _write(self, value):

        assert self.client and self.client.protocol

        protocol = self.client.protocol

        if self.mode == "coil":
            resp = await protocol.write_coil(self.address, value)
        else:
            if self.channel is not None:
                resp = await protocol.read_holding_registers(self.address)
                current_value = resp.registers[0]
                if value is True or value > 0:
                    value = current_value | (1 << self.channel)
                else:
                    value = current_value & (~(1 << self.channel))
            resp = await protocol.write_register(self.address, value)

        if resp.function_code > 0x80:
            raise DriftError(
                f"Invalid response for device {self.name!r}: "
                f"0x{resp.function_code:02X}."
            )

        return True


class Relay(Device):
    """A device representing a relay.

    The main difference with a normal `.Device` is that the adaptor is defined
    by the ``relay_type``, which can be normally closed (NC) or normally open
    (NO).

    """

    __type__ = "relay"

    def __init__(self, module: Module, *args, relay_type="NC", **kwargs):

        self.relay_type = relay_type

        if relay_type == "NC":
            adaptor = [(False, "closed"), (True, "open")]
        else:
            adaptor = [(False, "open"), (True, "closed")]

        kwargs["adaptor"] = adaptor

        super().__init__(module, *args, **kwargs)

        assert self.mode in ["coil", "holding_register"]

    async def open(self):
        """Opens the relay."""

        if self.relay_type == "NC":
            await self.write(True)
        else:
            await self.write(False)

    async def close(self):
        """Closes the relay."""

        if self.relay_type == "NC":
            await self.write(False)
        else:
            await self.write(True)

    async def switch(self):
        """Switches the state of the relay."""

        await self.write(not await self.read(adapt=False))

    async def cycle(self, delay=1):
        """Cycles a relay, waiting ``delay`` seconds."""

        await self.switch()
        await asyncio.sleep(delay)
        await self.switch()


class Drift(object):
    """Interface to the modbus network.

    `.Drift` manages the TCP connection to the modbus ethernet module
    using `Pymodbus <pymodbus.readthedocs.io/en/latest/index.html>`__. The
    ``AsyncioModbusTcpClient`` object can be accessed as ``Drift.client``.

    In general the connection is opened and closed using the a context
    manager ::

        drift = Drift('localhost')
        async with drift:
            coil = drift.client.protocol.read_coils(1, count=1)

    This is not needed when using `.Device.read` or `.Device.write`, which
    handle the connection to the server.

    Parameters
    ----------
    address
        The IP of the TCP modbus server.
    port
        The port of the TCP modbus server.
    lock
        Whether to lock the client while it's in use, preventing
        multiple connections. Only used with the contextual manager.

    """

    def __init__(self, address: str, port: int = 502, lock: bool = True):

        self.address = address
        self.port = port
        self.client = AsyncioModbusTcpClient(address, port=port)

        self.lock = asyncio.Lock() if lock else None

        self.modules = CaseInsensitiveDict()

    def __repr__(self):
        return f"<Drift @ {self.address}>"

    async def __aenter__(self):
        """Initialises the connection to the server."""

        if self.lock:
            await self.lock.acquire()

        try:
            await asyncio.wait_for(self.client.connect(), timeout=1)
        except asyncio.TimeoutError:
            if self.lock:
                self.lock.release()
            raise DriftError(f"Failed connecting to server at {self.address}.")

        if not self.client.connected:
            if self.lock:
                self.lock.release()
            raise DriftError(f"Failed connecting to server at {self.address}.")

        log.debug(f"Connected to {self.address}.")

        return

    async def __aexit__(self, exc_type, exc, tb):
        """Closes the connection to the server."""

        self.client.stop()
        log.debug(f"Disonnected from {self.address}.")

        if self.lock:
            self.lock.release()

        return

    def __getitem__(self, name: str) -> Module:
        """Gets a module."""

        return self.modules[name]

    @property
    def devices(self):
        """Lists the devices connected across all modules."""

        devices = []
        for module in self.modules:
            for device in self[module].devices:
                devices.append(device)

        return devices

    def add_module(self, name: str, **kwargs) -> Module:
        """Adds a new module.

        Parameters
        ----------
        name
            The name of the module.
        kwargs
            Arguments to be passed to `.Module` for initialisation.

        """

        if name in self.modules:
            raise ValueError(f"Module {name} is already connected.")

        self.modules[name] = Module(name, self, **kwargs)

        return self.modules[name]

    def get_device(self, device: str) -> Device:
        """Gets the `.Device` instance that matches ``device``.

        If the case-insensitive name of the device is unique within the pool
        of connected devices, the device name is sufficient. Otherwise the
        device must be provided as ``module.device``.


        """

        if "." in device:
            module, device = device.split(".")
            return self.modules[module].devices[device]

        device = device.lower()

        dev_to_mod = defaultdict(list)
        for module in self.modules:
            for dev in self.modules[module].devices:
                dev_to_mod[dev.lower()].append(module.lower())

        if device not in dev_to_mod:
            raise ValueError(f"Device {device} is not connected.")

        elif len(dev_to_mod[device]) == 1:
            return self.modules[dev_to_mod[device.lower()][0]].devices[device]

        else:
            raise ValueError(
                f"Multiple devices with name {device} found. "
                "Use a module-qualified name."
            )

    async def read_device(self, name: str, adapt: bool = True):
        """Reads a device.

        Parameters
        ----------
        name
            The device to read.
        adapt
            If possible, convert the value to real units.

        Returns
        -------
        read_value
            The read value and its associated units.

        """

        return await self.get_device(name).read(adapt=adapt)

    async def read_devices(
        self,
        devices: list[str],
        adapt: bool = True,
        lock: bool | None = None,
    ):
        """Reads a list of devices minimising the number of connections to the client.

        Parameters
        ----------
        devices
            The list of devices to read.
        adapt
            If possible, convert the value to real units.
        lock
            If `True`, lock the client while reading the devices. If `None`, use
            the default locking mechanism.

        Returns
        -------
        read_values
            A list of read values. If `adapt=True`, each element is a tuple of
            value and unit.

        """

        lock = lock if lock is not None else (self.lock is not None)

        tasks = []
        for device in devices:
            tasks.append(self.get_device(device).read(adapt=adapt, connect=False))

        if lock and self.lock:
            await self.lock.acquire()

        try:
            await asyncio.wait_for(self.client.connect(), timeout=1)
            results = await asyncio.gather(*tasks)
        finally:
            if self.client.connected:
                self.client.stop()

            if lock and self.lock:
                self.lock.release()

        return results

    async def read(self, *args, **kwargs):
        """Alias for `.read_device`."""

        return await self.read_device(*args, **kwargs)

    async def read_category(
        self,
        category: str,
        adapt: bool = True,
        connect: bool = True,
    ) -> dict[str, Any]:
        """Reads all the devices of a given category.

        Parameters
        ----------
        category
            The category to match.
        adapt
            If possible, convert the value to real units.
        connect
            Whether to connect to the client and disconnect after each read. If
            ``connect=False``, the user is responsible for connecting and disconnecting.

        Returns
        -------
        read_values
            A dictionary of module-qualified device names and read values,
            along with their units.

        """

        values = {}

        for module in self.modules:
            for device in self.modules[module].devices.values():
                name = f"{module}.{device.name.lower()}"
                if device.category and device.category.lower() == category:
                    values[name] = await device.read(adapt=adapt, connect=connect)

        return values

    @classmethod
    def from_config(cls, config: str | dict, **kwargs):
        """Loads a Drift from a dictionary or YAML file.

        Parameters
        ----------
        config
            A properly formatted configuration dictionary or the path to a
            YAML file from which it can be read. Refer to :ref:`config-file`
            for details on the format.

        """

        if isinstance(config, str):
            config = cast(dict, load(open(config, "r"), Loader=SafeLoader))

        address = config["address"]
        port = config.get("port", 502)

        new_drift = cls(address, port, **kwargs)

        for module in config.get("modules", {}):

            module_config = config["modules"][module]
            devices = module_config.pop("devices", {})

            new_drift.add_module(module, **module_config)

            for device in devices:

                device_config = devices[device].copy()
                address = device_config.pop("address")
                device_class = None
                type_ = device_config.pop("type", None)

                if type_:
                    for subclass in Device.__subclasses__():
                        if subclass.__type__ == type_:
                            device_class = subclass
                            break
                else:
                    device_class = Device

                if device_class is None:
                    raise DriftError("Cannot find valid device class for type {type_}.")

                new_drift.modules[module].add_device(
                    device,
                    address,
                    device_class,
                    **device_config,
                )

        return new_drift
