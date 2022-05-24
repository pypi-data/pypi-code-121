from __future__ import annotations

import json
from logging import Logger

from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


def get_cluster_usage(
    resource_conf: VCenterResourceConfig,
    datastore_name: str,
    logger: Logger,
):
    si = SiHandler.from_config(resource_conf, logger)
    dc = DcHandler.get_dc(resource_conf.default_datacenter, si)
    compute_entity = dc.get_compute_entity(resource_conf.vm_cluster)
    datastore = dc.get_datastore(datastore_name)
    logger.info(f"Found {compute_entity}")
    return json.dumps(
        {
            "datastore": datastore.usage_info.to_dict(),
            "cpu": compute_entity.cpu_usage.to_dict(),
            "ram": compute_entity.ram_usage.to_dict(),
        }
    )
