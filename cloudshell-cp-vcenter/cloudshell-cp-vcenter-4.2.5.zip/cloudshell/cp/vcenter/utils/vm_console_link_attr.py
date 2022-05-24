from __future__ import annotations

from urllib.parse import urlencode

from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cp.core.request_actions.models import Attribute

from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.models.deploy_app import BaseVCenterDeployApp
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig
from cloudshell.cp.vcenter.utils.get_vm_web_console import get_vm_console_link

WEB_CONSOLE_ATTR_NAME = "VM Console Link"


def set_deployed_app_vm_console_link_attr(
    deployed_app: BaseVCenterDeployedApp,
    resource_config: VCenterResourceConfig,
    vm: VmHandler,
    si: SiHandler,
):
    if WEB_CONSOLE_ATTR_NAME in deployed_app.attributes:
        link = get_vm_console_link(resource_config.address, si, vm, new_version=True)
        params = {
            "username": resource_config.user,
            "password": resource_config.password,
            "link": link,
        }
        query = urlencode(params)

        cs_api: CloudShellAPISession = deployed_app.cs_api
        cs_api.SetAttributeValue(deployed_app.name, WEB_CONSOLE_ATTR_NAME, query)


def get_deploy_app_vm_console_link_attr(
    deploy_app: BaseVCenterDeployApp,
    resource_config: VCenterResourceConfig,
    vm: VmHandler,
    si: SiHandler,
) -> Attribute | None:
    if WEB_CONSOLE_ATTR_NAME not in deploy_app.attributes:
        return None

    link = get_vm_console_link(resource_config.address, si, vm, new_version=True)
    params = {
        "username": resource_config.user,
        "password": resource_config.password,
        "link": link,
    }
    query = urlencode(params)
    return Attribute(WEB_CONSOLE_ATTR_NAME, query)
