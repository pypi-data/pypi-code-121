from __future__ import annotations

from logging import Logger

from packaging import version

from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig
from cloudshell.cp.vcenter.utils.get_vm_web_console import (
    VCENTER_NEW_CONSOLE_LINK_VERSION,
    get_vm_console_link,
)
from cloudshell.cp.vcenter.utils.vm_console_link_attr import (
    set_deployed_app_vm_console_link_attr,
)


def get_vm_web_console(
    resource_conf: VCenterResourceConfig,
    deployed_app: BaseVCenterDeployedApp,
    logger: Logger,
) -> str:
    logger.info("Get VM Web Console")
    si = SiHandler.from_config(resource_conf, logger)
    dc = DcHandler.get_dc(resource_conf.default_datacenter, si)
    vm = dc.get_vm_by_uuid(deployed_app.vmdetails.uid)

    new_version = version.parse(si.vc_version) >= version.parse(
        VCENTER_NEW_CONSOLE_LINK_VERSION
    )
    link = get_vm_console_link(resource_conf.address, si, vm, new_version)
    set_deployed_app_vm_console_link_attr(deployed_app, resource_conf, vm, si)
    return link
