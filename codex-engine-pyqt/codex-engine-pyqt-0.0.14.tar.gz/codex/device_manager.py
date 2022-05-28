from codex import SerialDevice, UnknownDevice, DeviceStates
from serial.tools.list_ports import comports
import time
import logging
from qtstrap import *
from .bundles import SigBundle, SlotBundle
from .subscriptions import SubscriptionManager


class DeviceManager(QObject):
    # forward these method calls, for backwards compatibility
    subscribe = SubscriptionManager.subscribe
    subscribe_to = SubscriptionManager.subscribe_to

    @staticmethod
    def profiles():
        return {p.profile_name: p for p in SerialDevice.__subclasses__()}

    @staticmethod
    def profile_names():
        return sorted({p.profile_name: p for p in SerialDevice.__subclasses__()})

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.log = logging.getLogger(__name__)
        self.log.info("Initializing DeviceManager...")

        self.signals = SigBundle({'device_added':[SerialDevice], 'device_removed': [str]})
        self.slots = SlotBundle({'add_device':[SerialDevice], 'remove_device': [str]})
        self.slots.link_to(self)

        self.devices = {}
        self.new_devices = []
        self.first_scan = True
        self.ports = []

        self.sub_manager = SubscriptionManager(self)
        
        prev = QSettings().value('starting_devices', [])
        if isinstance(prev, str):
            prev = [prev]
        self.starting_devices = prev

        prev = QSettings().value('ignored_ports', [])
        if isinstance(prev, str):
            prev = [prev]
        self.ignored_ports = prev

        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(lambda: self.scan())
        self.scan_timer.start(250)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(lambda: self.update())
        self.update_timer.start(1)
        
        self.sub_manager.check_for_new_subscribers()

        UnknownDevice.register_autodetect_info(self.profiles())
        
    def set_starting_devices(self, devices):
        self.starting_devices = devices
        QSettings().setValue('starting_devices', devices)

    def set_ignored_ports(self, ports):
        self.ignored_ports = ports
        QSettings().setValue('ignored_ports', ports)

    def close(self):
        self.scan_timer.stop()
        self.update_timer.stop()
        for _, device in self.devices.items():
            device.close()

    def on_add_device(self, device):
        self.devices[device.guid] = device
        self.signals.device_added.emit(device)

    def on_remove_device(self, guid):
        self.signals.device_removed.emit(guid)
        self.devices[guid].close()
        self.devices.pop(guid)

    def do_first_scan(self, new_ports):
        if self.starting_devices:
            for string in self.starting_devices:
                parts = string.split(':')
                profile = parts[0]
                port = parts[1]
                baud = parts[2] if len(parts) == 3 else None
                if profile in DeviceManager.profile_names():
                    if port in new_ports or port == 'DummyPort':
                        if baud:
                            self.on_add_device(self.profiles()[profile](port=port, baud=baud))
                        else:
                            self.on_add_device(self.profiles()[profile](port=port))
                        if port != 'DummyPort':
                            self.ports.append(port)
            self.first_scan = False

    def scan(self):
        self.sub_manager.check_for_new_subscribers()

        new_ports = [p.device for p in sorted(comports())]
        
        if self.first_scan:
            self.do_first_scan(new_ports)

        for port in [p for p in new_ports if p not in self.ports]:
            if port not in self.ignored_ports:
                self.log.debug(f"New device connected at ({port}), enumerating...")
                device = UnknownDevice(port=port)
                self.new_devices.append(device)

        for port in [p for p in self.ports if p not in new_ports]:            
            self.log.debug(f"Existing device removed from ({port}), cleaning up...")
            
            for k in self.devices.keys():
                if self.devices[k].port == port:
                    self.on_remove_device(self.devices[k].guid)
                    break

        self.ports = new_ports

    def update(self):
        for device in self.new_devices:
            device.communicate()

            if device.state == DeviceStates.enumeration_failed:
                self.log.debug(f"Enumeration failed on ({device.port})")
                device.close()
                self.new_devices.remove(device)
        
            elif device.state == DeviceStates.enumeration_succeeded:
                if device.name in DeviceManager.profile_names():
                    device.close()
                    new_device = self.profiles()[device.name](device=device)

                    self.log.debug(f"Enumeration succeeded on ({new_device.port})")

                    self.devices[new_device.guid] = new_device
                    self.new_devices.remove(device)

                    self.signals.device_added.emit(new_device)

        for guid in self.devices.keys():
            self.devices[guid].communicate()