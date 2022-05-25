import sys
from typing import List, Optional

from proxmoxer import ProxmoxAPI

from pve_utils.config import settings
from pve_utils.utils import pprint

from .proxmox_container import ProxmoxContainer


class ProxmoxNode:
    conn: ProxmoxAPI
    name: str
    lxc: List[ProxmoxContainer]

    def __init__(self, conn: ProxmoxAPI, name: str):
        self.conn = conn
        self.name = name
        self.node = self.conn.nodes(self.name)
        self.lxc = self.__get_aviable_lxc()

    def __get_aviable_lxc(self) -> List[ProxmoxContainer]:
        return [
            ProxmoxContainer(
                node=self.node, vmid=ct.pop("vmid"), name=ct.pop("name"), **ct
            )
            for ct in self.node.lxc.get()
        ]

    def __get_next_free_vmid(self) -> int:
        return self.conn.cluster.nextid.get()

    def create_lxc(
        self,
        hostname: str,
        cores: int = 4,
        memory: int = 4096,
        start: bool = True,
        password: Optional[str] = None,
        ostemplate: Optional[str] = None,
        vmid: Optional[int] = None,
        storage: Optional[str] = None,
        **kwargs,
    ) -> Optional[ProxmoxContainer]:
        if not vmid:
            vmid = self.__get_next_free_vmid()
        if not password:
            password = settings.CT_PASSWORD
        if not ostemplate:
            ostemplate = settings.CT_OS_TEMPLATE
        if not storage:
            storage = settings.CT_STORAGE
        net_config = (
            f"name={settings.CT_NET_NAME},"
            f"bridge={settings.CT_NET_BRIDGE},"
            f"ip={settings.CT_IP}/{settings.CT_CIDR},"
            f"gw={settings.CT_GW}"
        )
        try:
            pprint.info(
                "Creating CT: \n"
                f"   vmid={vmid}, \n"
                f"   ostemplate={ostemplate}, \n"
                f"   cores={cores}, \n"
                f"   memory={memory}, \n"
                f"   hostname={hostname}, \n"
                f"   password={password}, \n"
                f"   storage={storage}, \n"
                f"   net0={net_config}"
            )
            self.node.lxc.post(
                vmid=vmid,
                ostemplate=ostemplate,
                cores=cores,
                memory=memory,
                hostname=hostname,
                password=password,
                storage=storage,
                start=int(start),
                net0=net_config,
            )
            pprint.success(f"Successfully created CT: {vmid} {hostname}")
            return ProxmoxContainer(self.node, hostname, vmid)
        except Exception as e:
            pprint.error(f"Failed to create CT: {vmid}")
            pprint.info("Tracebak:")
            pprint.normal(e)
            sys.exit(1)

    def get_lxc(
        self, name: str, create: bool = False
    ) -> Optional[ProxmoxContainer]:
        filtered_ct = [ct for ct in self.lxc if ct.name == name]
        if len(filtered_ct) > 0:
            pprint.info(f"Container: {name} already exist")
            return filtered_ct[0]
        elif len(filtered_ct) < 1:
            pprint.info(f"Container: {name} does not exist")
            if create:
                return self.create_lxc(name)
        return None
