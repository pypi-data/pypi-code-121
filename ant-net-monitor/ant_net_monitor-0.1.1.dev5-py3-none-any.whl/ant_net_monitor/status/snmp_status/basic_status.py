from datetime import datetime
from dataclasses import dataclass

from . import cpu_status, ram_status, disk_status, network_status, swap_status


@dataclass
class BasicStatus:
    cpu_percent: float
    ram_percent: float  # The percent of memory used to the system.
    swap_percent: float
    time_stamp: datetime

    def __init__(self, cpu_percent, ram_percent, swap_percent):
        self.cpu_percent = cpu_percent
        self.ram_percent = ram_percent
        self.swap_percent = swap_percent
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    def __str__(self):
        return f"cpu:{self.cpu_percent}%, memory:{round(self.ram_percent/(1024**3),2)}G, disk:{round(self.disk/(1024**3),2)}G"

    @classmethod
    def get_last(cls, agent):
        cpu_percent = cpu_status.CPUStatusInfo.get_last(agent).used_percent
        ram_percent = ram_status.RAMStatusInfo.get_last(agent).used_percent
        swap_percent = swap_status.SwapStatusInfo.get_last(agent).percent
        return cls(cpu_percent, ram_percent, swap_percent)
