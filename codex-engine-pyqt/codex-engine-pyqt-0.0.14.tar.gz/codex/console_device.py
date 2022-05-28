from qtstrap import *
from codex import SerialDevice, NullFilter


class ConsoleDevice(SerialDevice):
    profile_name = "ConsoleDevice"

    def __init__(self, port=None, baud=115200, device=None):
        super().__init__(port=port, baud=baud, device=device)

        self.filter = NullFilter()
        self.message_tree = None