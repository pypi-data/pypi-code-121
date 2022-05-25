import sys
from typing import List

from paramiko import SSHClient

from pve_utils.config import settings
from pve_utils.utils import SSHconnectable, pprint
from pve_utils.utils.decorators import with_ssh


class ProxmoxContainer(SSHconnectable):
    name: str
    vmid: int

    def __init__(self, node, name: str, vmid: int, *args, **kwargs):
        self.node = node
        self.name = name
        self.vmid = vmid
        self.host = settings.CT_IP
        self.port = 22
        self.user = "root"
        self.password = settings.CT_PASSWORD
        self.ct = self.__get_ct()

    def __get_ct(self):
        return self.node.lxc(self.vmid)

    @with_ssh
    def exec(self, client: SSHClient, commands: List[str]) -> None:
        pprint.info(
            f"Run commands on CT: {self.vmid} "
            f"{self.host}:{self.port} as: {self.user}"
        )
        for command in commands:
            self.run_command(client, command)

    def run_command(self, client: SSHClient, command: str) -> None:
        stdin, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0:
            pprint.error(
                f"Failed to execute command: {command}. Exit code: {exit_code}"
            )
            output = stdout.readlines()
            if output:
                pprint.info("Info:")
                for line in output:
                    pprint.normal(line.strip())
            traceback = stderr.readlines()
            if traceback:
                pprint.info("Traceback:")
                for line in traceback:
                    pprint.normal(line.strip())
            sys.exit(1)
        else:
            pprint.success(f"Success execute command: {command}")
            output = stdout.readlines()
            if output:
                pprint.info("Output:")
                for line in output:
                    pprint.normal(line.strip())

    def __str__(self):
        return f"CT {self.vmid}: {self.name}"
