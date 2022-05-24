from __future__ import annotations

from logging import Logger

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import CustomSpecNotFound, SiHandler
from cloudshell.cp.vcenter.models.custom_spec import get_custom_spec_params_from_json
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig
from cloudshell.cp.vcenter.utils.customization_params import prepare_custom_spec


class CustomSpecExists(BaseVCenterException):
    def __init__(self, spec_name: str):
        self.spec_name = spec_name
        super().__init__(
            f"Unable to apply customization spec '{spec_name}'. Customization spec for "
            f"the given VM already exists. Specify the 'Override Customization Spec' "
            f"flag to override it."
        )


def customize_guest_os(
    resource_conf: VCenterResourceConfig,
    deployed_app: BaseVCenterDeployedApp,
    custom_spec_name: str,
    custom_spec_params: str,
    override_custom_spec: bool,
    logger: Logger,
):
    si = SiHandler.from_config(resource_conf, logger)
    dc = DcHandler.get_dc(resource_conf.default_datacenter, si)
    vm = dc.get_vm_by_uuid(deployed_app.vmdetails.uid)
    custom_spec_params = get_custom_spec_params_from_json(
        custom_spec_params, vm, logger
    )

    if override_custom_spec:
        logger.info(
            "The override flag is set. Deleting the previous Customization spec "
            "if such exists"
        )
        si.delete_customization_spec(vm.name)
    else:
        try:
            custom_spec = si.get_customization_spec(vm.name)
        except CustomSpecNotFound:
            pass
        else:
            logger.info(f"Found existing Customization spec: '{custom_spec.name}'")
            if custom_spec_name:
                raise CustomSpecExists(custom_spec_name)
            else:
                custom_spec_name = custom_spec.name

    prepare_custom_spec(custom_spec_params, custom_spec_name, vm, vm.name, si)
