from typing import Optional

from pydantic import Field

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectionParamsModel,
    ConnectivityActionModel,
    VlanServiceModel,
)


class VcenterVlanServiceModel(VlanServiceModel):
    port_group_name: Optional[str] = Field(None, alias="Port Group Name")


class VcenterConnectionParamsModel(ConnectionParamsModel):
    vlan_service_attrs: VcenterVlanServiceModel = Field(
        ..., alias="vlanServiceAttributes"
    )


class VcenterConnectivityActionModel(ConnectivityActionModel):
    connection_params: VcenterConnectionParamsModel = Field(
        ..., alias="connectionParams"
    )
