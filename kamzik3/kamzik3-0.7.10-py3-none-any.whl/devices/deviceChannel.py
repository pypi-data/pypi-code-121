from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.observer import Observer


class DeviceChannel(Device, Observer):
    """
    Base class for Device acting as a Channel of parent Device.
    This class serves only as a Template and must be inherited by target Class.
    Typical example is Motor axis, Interferometer channel or any Device which can control multiple sub Devices (Channels).
    Example of config file:

    Motor1_axis_0: &x !Device:kamzik3.devices.dummy.dummyMotor.DummyMotorChannel
        device: *Parent_Device
        channel: 0
        device_id: Motor_axis
    """

    def __init__(self, device, channel, device_id=None, config=None):
        """
        Base logic is to use subject_update method to observe parent Device.
        Parent Device then should call notify method to notify all observers about update.
        On Channel level, we should then filter for channel ID, which is UINT starting from 0.
        You are free to reimplement subject_update to Your needs.
        Usually Parent Device call notify(key, value) with parameters key=(channel_id, ATTR_NAME), value.
        Subject is always parent Device, called notify, since we can observe multiple Devices.
        :param Device device: parent Device to observe
        :param uint channel: channel id starting from 0
        :param str device_id: Device ID
        :param dict config: Device configuration
        """
        self.configured = False
        self.device = device
        self.channel = channel
        self.position_attribute_copy = None
        super().__init__(device_id, config)
        self.set_status(STATUS_CONNECTING)
        self.device.attach_observer(self)

    def _init_attributes(self):
        Device._init_attributes(self)

    def command(self, command, callback=None, with_token=False, returning=True):
        """
        Wrapper for Device command.
        Instead of executing command on this Device, execute it on parent Device.
        :param str command: Request to Device
        :param Callable callback: callback after Device replies to Command
        :param bool with_token: token
        :param returning: bool
        :return int: token
        """
        return self.device.command(command, callback, with_token, returning)

    def subject_update(self, key, value, subject):
        """
        This method should be overloaded in Target class.
        Here should go all the logic, that filters for channel id and does update of Channel Device Attribute.
        :param mixed key: subject name
        :param mixed value: subject value
        :param Subject subject: Subject
        """
        if key == ATTR_STATUS:
            if value in READY_DEVICE_STATUSES:
                self.handle_configuration()
            else:
                self.configured = False
                self.set_status(value)

    def poll_command(self, command, interval):
        """
        Wrapper for poll_command.
        Register polled command on Parent Device.
        :param str command: Request / Command
        :param int interval: interval in ms
        """
        self.device.poll_command(command, interval)

    def remove_poll_command(self, command, interval):
        """
        Wrapper for remove_poll_command.
        Unregister polled command on Parent Device.
        :param str command: Request / Command
        :param int interval: interval in ms
        """
        self.device.remove_poll_command(command, interval)

    def handle_configuration(self):
        raise NotImplementedError("Must be overloaded")

    def disconnect(self):
        self.stop_polling()
        self.configured = False
        self.device.detach_observer(self)
        self.set_status(STATUS_DISCONNECTED)

    # pylint: disable=unused-argument
    def reconnect(self, *args):
        self.device.attach_observer(self)
        self.handle_configuration()
