import sys

import click
from proxmoxer import ProxmoxAPI

from pve_utils.config import settings
from pve_utils.resources import ProxmoxNode


@click.command()
@click.option(
    "-N", "--node-name", required=True, type=str, help="Name of Proxmox Node."
)
@click.option("-H", "--host-name", required=True, type=str, help="Name of CT.")
@click.argument("command")
def shell_lxc(node_name: str, host_name: str, command: str):
    """
    Run commands in CT via SSH
    command provides like a string
    (shell_lxc -N ktiib -H new1.rsue.ru "echo 1421")
    other settings provides with env
    """

    conn = ProxmoxAPI(
        settings.PROXMOX_URL,
        port=settings.PROXMOX_PORT,
        user=settings.PROXMOX_USER,
        password=settings.PROXMOX_PASSWORD,
        verify_ssl=settings.PROXMOX_VERIFY_SSL,
    )

    node_worker = ProxmoxNode(conn, node_name)
    ct = node_worker.get_lxc(host_name, create=False)
    if not ct:
        sys.exit(1)
    ct.exec([command])


if __name__ == "__main__":
    shell_lxc()
