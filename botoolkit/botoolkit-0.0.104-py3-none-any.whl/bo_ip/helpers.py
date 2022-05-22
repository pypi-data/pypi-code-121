import platform
import subprocess

from botoolkit.bo_ip.enums import (
    IPAddressStateEnum,
)


def ping_ip_address(
    ip_address: str,
) -> IPAddressStateEnum:
    command_key = (
        'n' if
        platform.system().lower() == 'windows' else
        'c'
    )
    output = ''

    try:
        output = subprocess.check_output(
            f'ping -{command_key} 1 {ip_address}',
            shell=True,
            universal_newlines=True,
        )
    except Exception:
        pass

    state = (
        IPAddressStateEnum.REACHABLE if
        output and IPAddressStateEnum.UNREACHABLE.value not in output else
        IPAddressStateEnum.UNREACHABLE
    )

    return state
