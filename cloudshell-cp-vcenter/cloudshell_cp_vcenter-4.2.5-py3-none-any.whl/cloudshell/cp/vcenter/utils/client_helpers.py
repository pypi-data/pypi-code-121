import atexit
import ssl

from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim  # noqa
from retrying import retry

from cloudshell.cp.vcenter.exceptions import BaseVCenterException, LoginException


class ApiConnectionError(BaseVCenterException):
    def __init__(self, host: str):
        self.host = host
        super().__init__(f"Cannot connect to the vCenter {host} API")


class VcenterConnectionError(BaseVCenterException):
    def __init__(self, host: str):
        self.host = host
        super().__init__(f"Cannot connect to the vCenter {host}")


def _get_si_tls_v1(host: str, user: str, password: str, port: int):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    return SmartConnect(
        host=host,
        user=user,
        pwd=password,
        port=port,
        sslContext=context,
    )


def _get_si_tls_v1_2(host: str, user: str, password: str, port: int):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE
    return SmartConnect(
        host=host,
        user=user,
        pwd=password,
        port=port,
        sslContext=context,
    )


def _get_si_without_ssl(host: str, user: str, password: str, port: int):
    return SmartConnect(
        host=host,
        user=user,
        pwd=password,
        port=port,
    )


def _retry_on_login_failed(exc: Exception) -> bool:
    return isinstance(exc, LoginException)


@retry(
    wait_fixed=1000,
    stop_max_attempt_number=10,
    retry_on_exception=_retry_on_login_failed,
)
def get_si(host: str, user: str, password: str, port: int = 443):
    funcs = (_get_si_tls_v1_2, _get_si_tls_v1, _get_si_without_ssl)
    connect_issue = False
    for func in funcs:
        try:
            si = func(host, user, password, port)
        except (ssl.SSLEOFError, ssl.SSLError):
            continue
        except (vim.fault.HostConnectFault, OSError):
            connect_issue = True
            continue
        except vim.fault.InvalidLogin:
            raise LoginException("Cannot connect to the vCenter. Invalid user/password")
        else:
            atexit.register(Disconnect, si)
            break
    else:
        if connect_issue:
            raise VcenterConnectionError(host)
        else:
            raise ApiConnectionError(host)
    return si
