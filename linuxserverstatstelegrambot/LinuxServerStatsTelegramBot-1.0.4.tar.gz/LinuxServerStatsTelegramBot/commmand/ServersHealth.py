import os
import nmap
import socket
from LinuxServerStatsTelegramBot.commmand.Command import Command


class ServersHealth(Command):
    def execute(self) -> str:
        docker_stats_file = "/tmp/servers-health-stats.txt"
        servers_status = self.server_health()
        with open(docker_stats_file, "w") as destFile:
            for status in servers_status:
                destFile.write(f'{status.get("serverName")} '
                               f'({status.get("serverIp")}) '
                               f'is {status.get("serverState")}{os.linesep}')

        with open(docker_stats_file, "r") as file:
            data = file.read()
        return data

    def server_health(self):
        scanner = nmap.PortScanner()
        server_status = []
        for server in self.server_list():
            ip_addr = server.get("ip")
            host = socket.gethostbyname(ip_addr)
            scanner.scan(host, "1", "-v")
            status = {"serverName": server.get("name"), "serverState": scanner[host].state(), "serverIp": server.get("ip")}
            server_status.append(status)
        return server_status

    def server_list(self):
        servers = [
            {"ip": "10.8.0.6", "name": "Server SEB"},
            {"ip": "10.8.0.10", "name": "Server Canada 1"},
            {"ip": "10.8.0.13", "name": "Server Canada 2"},
            {"ip": "10.8.0.15", "name": "Server Canada 3"},
        ]
        return servers
