from __future__ import annotations

from typing import Union

from cloudshell.cp.vcenter.handlers.custom_spec_handler import (
    CustomSpecHandler,
    create_custom_spec_from_spec_params,
)
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.models.custom_spec import (
    LinuxCustomizationSpecParams,
    WindowsCustomizationSpecParams,
)

CUSTOM_SPEC_PARAMS_TYPE = Union[
    WindowsCustomizationSpecParams, LinuxCustomizationSpecParams, None
]


def prepare_custom_spec(
    custom_spec_params: CUSTOM_SPEC_PARAMS_TYPE,
    custom_spec_name: str,
    vm_template: VmHandler,
    vm_name: str,
    si: SiHandler,
) -> CustomSpecHandler | None:
    spec = None

    if custom_spec_name:
        if custom_spec_name != vm_name:
            si.duplicate_customization_spec(custom_spec_name, vm_name)
        spec = si.get_customization_spec(vm_name)
    elif custom_spec_params:
        spec = create_custom_spec_from_spec_params(custom_spec_params, vm_name)

    if spec:
        num_of_nics = len(vm_template.vnics)
        if custom_spec_params:
            spec.set_custom_spec_params(custom_spec_params, num_of_nics)

        if custom_spec_name:
            si.overwrite_customization_spec(spec)
        else:
            si.create_customization_spec(spec)

    return spec
