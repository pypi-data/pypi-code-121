import os
from LinuxServerStatsTelegramBot.commmand.Command import Command


class DockerStats(Command):
    def execute(self) -> str:
        docker_stats_file = "/tmp/docker-stats.txt"
        command = 'docker stats $(docker ps --format "{{.Names}}") --no-stream > ' + docker_stats_file
        os.system(command)
        with open(docker_stats_file, "r") as file:
            data = file.read()
        return data
