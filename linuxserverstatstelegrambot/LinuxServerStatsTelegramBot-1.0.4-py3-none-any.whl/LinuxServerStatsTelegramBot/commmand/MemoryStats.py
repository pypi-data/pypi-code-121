import os
from LinuxServerStatsTelegramBot.commmand.Command import Command


class MemoryStats(Command):
    def execute(self) -> str:
        memory_stats_file = "/tmp/memory-stats.txt"
        command = f"free -h > {memory_stats_file}"
        os.system(command)
        with open(memory_stats_file, "r") as file:
            data = file.read()
        return data
