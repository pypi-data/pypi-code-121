import asyncore
import logging
from collections import OrderedDict
from threading import Thread, Event, Lock, RLock
from time import sleep

import numpy

from kamzik3.constants import *
from kamzik3.snippets.snippetsTimer import PreciseCallbackTimer, CallbackTimer


class PortReadLoop(PreciseCallbackTimer):
    def __init__(self, interval=5):
        self.interval = interval
        self.logger = logging.getLogger("Console.PortReadLoop")
        PreciseCallbackTimer.__init__(self, interval, self.handle_interval_timeout)
        self.map = []
        self.stopped = Event()

    def run(self):
        self.logger.info("Starting port readout loop Thread")
        PreciseCallbackTimer.run(self)

    def add_device(self, device):
        if device not in self.map.copy():
            self.map.append(device)
            return True
        else:
            return False

    def remove_device(self, device):
        if device in self.map.copy():
            self.map.remove(device)
            return True
        else:
            return False

    def handle_interval_timeout(self):
        for device in self.map.copy():
            try:
                device.handle_read()
            except IOError:
                device.handle_response_error("Port read error")

    def stop(self):
        self.logger.info("Stopping port readout loop Thread")
        PreciseCallbackTimer.stop(self)


class DeviceConnectionPoller(CallbackTimer):
    def __init__(self, interval=2000):
        self.connecting_devices = []
        self.connected_devices = []
        self.interval = interval
        self.logger = logging.getLogger("Console.DeviceConnectionPoller")
        PreciseCallbackTimer.__init__(
            self,
            self.interval,
            self.check_devices_connection_timeout,
            with_correction=False,
        )

    def run(self):
        self.logger.info("Starting devices connection poller Thread")
        CallbackTimer.run(self)

    def add_connecting_device(self, device):
        if device not in self.connecting_devices:
            self.connecting_devices.append(device)

    def remove_connecting_device(self, device):
        try:
            self.connecting_devices.remove(device)
        except ValueError:
            pass  # device was removed already

    def check_devices_connection_timeout(self):
        for device in self.connecting_devices.copy():
            if device.connecting_time >= device.connection_timeout:
                self.remove_connecting_device(device)
                device.handle_connection_error("Connection timeout")
            elif device.connected:
                self.remove_connecting_device(device)
                self.connected_devices.append(device)
            else:
                device.connecting_time += self.interval
        for device in self.connected_devices.copy():
            if not device.is_alive():
                self.connected_devices.remove(device)

    def stop(self):
        self.logger.info("Stopping devices connection poller Thread")
        CallbackTimer.stop(self)


class DevicePoller(PreciseCallbackTimer):
    def __init__(self, interval=5):
        self.interval = interval
        self.commands_buffer = {}
        self.poll_commands_buffer = {}
        self.poll_lock = RLock()
        self.command_lock = RLock()
        self.logger = logging.getLogger("Console.DevicePoller")
        self.polling_schedule = OrderedDict()
        self.schedule = []
        self.schedule_at = numpy.uint64(0)
        PreciseCallbackTimer.__init__(self, self.interval, self.timer_tick)

    def run(self):
        self.logger.info("Starting devices poller Thread")
        PreciseCallbackTimer.run(self)

    def timer_tick(self):
        with self.command_lock:
            # Send pending commands
            for device, commands in self.commands_buffer.items():
                if commands and device.accepting_commands():
                    self.commands_buffer[device] = device.send_command(commands)

        with self.poll_lock:
            # Prepare polling commands
            for pollAt in self.schedule:
                if self.schedule_at % pollAt == 0:
                    for device, attributes in self.polling_schedule[pollAt].items():
                        if (
                            device.accepting_commands()
                            and device in self.poll_commands_buffer
                        ):
                            self.poll_commands_buffer[device] += attributes

        with self.poll_lock:
            # Send polling commands
            for device, commands in self.poll_commands_buffer.items():
                if commands and device.accepting_commands():
                    self.poll_commands_buffer[device] = device.send_command(commands)
                    device.set_value(
                        ATTR_BUFFERED_COMMANDS, len(self.poll_commands_buffer[device])
                    )
        self.schedule_at += self.interval

    def set_timeout(self, timeout):
        PreciseCallbackTimer.set_timeout(self, timeout)
        self.interval = timeout
        self.schedule_at = 0

    def stop(self):
        self.logger.info("Stopping devices poller Thread")
        PreciseCallbackTimer.stop(self)

    def add(
        self, device, attribute, poll_at, callback=None, returning=True, force_add=False
    ):
        with self.poll_lock:
            if poll_at not in self.polling_schedule:
                self.polling_schedule[poll_at] = OrderedDict()
            if device not in self.polling_schedule[poll_at]:
                self.polling_schedule[poll_at][device] = []
            if device not in self.poll_commands_buffer:
                self.poll_commands_buffer[device] = []

            polling_quadruplet = (attribute, None, callback, returning)
            if (
                force_add
                or polling_quadruplet not in self.polling_schedule[poll_at][device]
            ):
                self.polling_schedule[poll_at][device].append(polling_quadruplet)

            self.schedule = sorted(self.polling_schedule.keys())

    def remove(self, device, attribute, poll_at, callback=None, returning=True):
        with self.poll_lock:
            try:
                self.polling_schedule[poll_at][device].remove(
                    (attribute, None, callback, returning)
                )
                if len(self.polling_schedule[poll_at][device]) == 0:
                    del self.polling_schedule[poll_at][device]
                    del self.poll_commands_buffer[device]
                if len(self.polling_schedule[poll_at]) == 0:
                    del self.polling_schedule[poll_at]

                self.schedule = sorted(self.polling_schedule.keys())
            except (ValueError, KeyError):
                pass

    def stop_polling(self, device):
        with self.poll_lock:
            if device in self.poll_commands_buffer:
                del self.poll_commands_buffer[device]
            for polledDevices in self.polling_schedule.values():
                try:
                    if device in polledDevices:
                        del polledDevices[device]
                except (ValueError, KeyError):
                    pass  # device is no longer within polled devices
        with self.command_lock:
            if device in self.commands_buffer:
                del self.commands_buffer[device]

    def prepare_command(self, device, command):
        with self.command_lock:
            try:
                self.commands_buffer[device].append(command)
            except KeyError:
                self.commands_buffer[device] = [command]

    def prepend_command(self, device, command):
        with self.command_lock:
            try:
                self.commands_buffer[device].insert(0, command)
            except KeyError:
                self.commands_buffer[device] = [command]


class DeviceAsyncoreLoop(Thread):
    stopped = False

    def __init__(self):
        self.logger = logging.getLogger("Console.DeviceAsyncoreLoop")
        super(DeviceAsyncoreLoop, self).__init__()
        self.setDaemon(True)

    def run(self):
        self.logger.info("Starting devices asyncore loop Thread")
        self.stopped = False
        # We check if Loop is stopped
        while not self.stopped:
            # If not we start a loop. Loop is breaked when no devices are connected.
            asyncore.loop()
            # Sleep for a second before we tried to start asyncore loop again.
            sleep(1)

    def stop(self):
        self.logger.info("Stopping devices asyncore loop Thread")
        self.stopped = True
        asyncore.close_all()


control_asyncore_loop = DeviceAsyncoreLoop()
control_device_connection_poller = DeviceConnectionPoller()
control_device_poller = DevicePoller()
control_port_read_loop = PortReadLoop()
