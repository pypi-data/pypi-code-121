import psutil
from dataclasses import dataclass


@dataclass
class SystemInfo:
    cpu_count: int
    ram_total: float
    swap_total: float
    disk_total: float
    disk_percent: float

    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.ram_total = format(psutil.virtual_memory().total / 1024**3, ".2f")
        self.swap_total = format(psutil.swap_memory().total / 1024**3, ".2f")
        self.disk_total = format(psutil.disk_usage("/").total / 1024**3, ".2f")
        self.disk_percent = psutil.disk_usage("/").percent
