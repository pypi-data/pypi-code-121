import os
from LinuxServerStatsTelegramBot.commmand.Command import Command


class CleanMemory(Command):
    def execute(self) -> str:
        docker_stats_file = "/tmp/clean-memory-stats.txt"
        command = '/bin/sync; echo 1 > /proc/sys/vm/drop_caches; echo "Memory cleaned > " ' + docker_stats_file
        os.system(command)
        with open(docker_stats_file, "r") as file:
            data = file.read()
        return data
