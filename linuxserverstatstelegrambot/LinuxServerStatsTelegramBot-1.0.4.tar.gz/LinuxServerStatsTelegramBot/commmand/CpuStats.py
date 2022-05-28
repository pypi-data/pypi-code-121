import os
from typing import Any

from LinuxServerStatsTelegramBot.commmand.Command import Command


class CpuStats(Command):
    def execute(self) -> Any:
        cpu_stats_file = "/tmp/disks-stats.txt"
        command = f'top -b -n1 -o +%MEM | head -n 30 > {cpu_stats_file}'
        os.system(command)
        with open(cpu_stats_file, "r") as file:
            data = file.read()
        return data
