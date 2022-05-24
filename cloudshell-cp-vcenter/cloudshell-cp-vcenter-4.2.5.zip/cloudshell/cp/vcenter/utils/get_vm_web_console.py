from __future__ import annotations

import ssl
from urllib.parse import quote

import OpenSSL

from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler

HTTPS_PORT = 443

VCENTER_NEW_CONSOLE_LINK_VERSION = "6.7.0"

VM_WEB_CONSOLE_OLD_LINK_TPL = (
    "https://{vcenter_ip}:9443/vsphere-client/webconsole.html?"
    "vmId={vm_moid}"
    "&vmName={vm_name}"
    "&serverGuid={server_guid}"
    "&host={vcenter_host}:443"
    "&sessionTicket={session_ticket}"
    "&thumbprint={thumbprint}"
)
VM_WEB_CONSOLE_NEW_LINK_TPL = (
    "https://{vcenter_ip}/ui/webconsole.html?"
    "vmId={vm_moid}"
    "&vmName={vm_name}"
    "&serverGuid={server_guid}"
    "&host={vcenter_host}:443"
    "&sessionTicket={session_ticket}"
    "&thumbprint={thumbprint}"
)


def get_vm_console_link(
    vcenter_host: str,
    si: SiHandler,
    vm: VmHandler,
    new_version: bool,
) -> str:
    vc_cert = ssl.get_server_certificate((vcenter_host, HTTPS_PORT)).encode()
    vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, vc_cert)
    thumbprint = vc_pem.digest("sha1")

    link = VM_WEB_CONSOLE_NEW_LINK_TPL if new_version else VM_WEB_CONSOLE_OLD_LINK_TPL
    return link.format(
        vcenter_ip=vcenter_host,
        vm_moid=vm._moId,
        vm_name=quote(vm.name),
        server_guid=si.instance_uuid,
        vcenter_host=si.vcenter_host,
        https_port=HTTPS_PORT,
        session_ticket=quote(si.acquire_session_ticket()),
        thumbprint=quote(thumbprint.decode()),
    )
