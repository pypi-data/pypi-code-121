"""Pretty-printing for host model classes"""
from colorama import Back, Style

from omniversion.models import Host


def _pretty_print_host(host: Host) -> str:
    return "\n".join([
        f"{Back.BLUE} {host.name} {Style.RESET_ALL}",
    ])
