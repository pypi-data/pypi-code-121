from typing import Any
import os
from LinuxServerStatsTelegramBot.commmand.Command import Command


class DiskStats(Command):
    def execute(self) -> Any:
        disk_stats_file = "/tmp/disks-stats.txt"
        command = f'df -h | grep -Ev "shm|overlay|loop|tmpfs|udev|none" > {disk_stats_file}'
        os.system(command)
        with open(disk_stats_file, "r") as file:
            data = file.read()
        return data
