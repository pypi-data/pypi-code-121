import click
from proxmoxer import ProxmoxAPI

from pve_utils.config import settings
from pve_utils.resources import ProxmoxNode


@click.command()
@click.option(
    "-N", "--node-name", required=True, type=str, help="Name of Proxmox Node."
)
@click.option("-H", "--host-name", required=True, type=str, help="Name of CT.")
@click.option(
    "-C",
    "--create",
    is_flag=True,
    default=False,
    type=bool,
    help="Create CT if doesn`t exist.",
)
def create_lxc(node_name: str, host_name: str, create: bool):
    conn = ProxmoxAPI(
        settings.PROXMOX_URL,
        port=settings.PROXMOX_PORT,
        user=settings.PROXMOX_USER,
        password=settings.PROXMOX_PASSWORD,
        verify_ssl=settings.PROXMOX_VERIFY_SSL,
    )

    node_worker = ProxmoxNode(conn, node_name)
    node_worker.get_lxc(host_name, create=create)


if __name__ == "__main__":
    create_lxc()
