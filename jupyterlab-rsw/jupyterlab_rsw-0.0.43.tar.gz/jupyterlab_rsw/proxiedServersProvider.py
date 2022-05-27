'''
  proxiedServersProvider.py

  Copyright (C) 2022 by RStudio, PBC

'''

import re
import jupyterlab_rsw.network as net
import jupyterlab_rsw.process as ps
from jupyterlab_rsw.constants import PORT_TOKEN, QUARTO_APP, SHINY_APP

import json
import subprocess
from typing import List, Dict

class ProxiedServersProvider:
    def __init__(self):
        self.start_up: bool = True
        self.servers: Dict[int, List[Server]] = {}
        self.ignore_servers: Dict[int, str] = {}

    def refresh(self):
        self.start_up = True
        self.servers = {}
        self.ignore_servers = {}

    def ignore_process(self, pid: int, name: str) -> bool:
        # If the process name is different, this PID got re-used so remove it from the
        # ignore list.
        if pid in self.ignore_servers and self.ignore_servers[pid] != name:
            self.ignore_servers.pop(pid)

        return pid in self.ignore_servers

    def remove_server(self, pid: int):
        if pid in self.servers:
            del self.servers[pid]

    def get_servers_json(self):
        json_str = '{"servers": ['
        for index, s in enumerate(self.servers.values()):
            for server in s:
                if index:
                    json_str += ','
                json_str += server.to_json()
        json_str += ']}'
        return json.loads(json_str)


    async def load_running_servers(self):
        listeners: List[net.ListeningProcess] = await net.get_listening_processes()

        for process in listeners:
            if self.start_up:
                self.ignore_servers[process.pid] = process.name
            elif process.pid not in self.servers and process.pid:
                if not self.ignore_process(process.pid, process.name):
                    name: str = resolve_pretty_name(process)
                    servers: List[Server] = []
                    for address in process.addresses:
                        servers.append(Server(process.pid, name, address))
                    self.servers[process.pid] = servers
                    ps.watch_for_exit(process.pid, self.remove_server, [process.pid])
        self.start_up = False

class Server:
    def __init__(self, pid: int, name: str, tcpInfo: net.TcpInfo):
        self.pid = pid
        self.label = name
        self.secure_port = self.transform_port(PORT_TOKEN, tcpInfo.port)
        self.ip = tcpInfo.address
        self.port = tcpInfo.port

    def transform_port(self, token, port):
        cmd = f'/usr/lib/rstudio-server/bin/rserver-url {port} {token}'
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        return proc.stdout.decode('utf-8')
    
    def to_json(self):
        return f'{{ "pid": "{self.pid}", "label": "{self.label}", "secure_port": "{self.secure_port}", "ip": "{self.ip}", "port": "{self.port}" }}'
    
def resolve_pretty_name(proc: net.ListeningProcess) -> str:
    shortProcName: str = proc.name.split('/').pop().strip() if '/' in proc.name else proc.name

    if len([arg for arg in proc.args if 'shiny::runApp' in arg or 'shiny' in arg]) > 0:
        shortProcName = SHINY_APP
    elif len([arg for arg in proc.args if arg.endswith('bin/quarto.js')]) > 0:
        shortProcName = QUARTO_APP
    elif re.compile('python(?:[0-9](?:\\.[0-9])?)?').match(shortProcName) or shortProcName == 'R':
        if len(proc.args) > 0 and re.compile('(/|^)streamlit$').match(proc.args[0]):
            proc.args.pop()
        
        for arg in proc.args:
            if re.compile('^\\/?(?:[^/]*\\/)+[^/]*$').match(arg):
                split: List[str] = arg.split('/')
                if len(split) > 1:
                    shortProcName = split[len(split) - 2]

    if proc.wd != '':
        return f"{proc.wd.split('/').pop()} - {shortProcName} "
    return shortProcName
