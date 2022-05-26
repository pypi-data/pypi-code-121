"""Cloud function used to associate created server with a dns name."""

import os
import time

from flask import Request  # type: ignore
from google.cloud.dns import Client  # type: ignore
from googleapiclient.discovery import Resource, build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore


def __create_instance(
    compute: Resource,
    disk_id: str,
    machine_type: str,
    project: str,
    server_name: str,
    zone: str,
) -> dict:
    machine_type = f"zones/{zone}/machineTypes/{machine_type}"
    startup = open("startup.sh", "r").read()

    config = {
        "name": server_name,
        "machineType": machine_type,
        "disks": [{"autoDelete": False, "boot": True, "source": disk_id}],
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ],
        "serviceAccounts": [
            {
                "email": "default",
                "scopes": [
                    "https://www.googleapis.com/auth/devstorage.read_only",
                    "https://www.googleapis.com/auth/logging.write",
                    "https://www.googleapis.com/auth/monitoring.write",
                    "https://www.googleapis.com/auth/servicecontrol",
                    "https://www.googleapis.com/auth/service.management.readonly",
                    "https://www.googleapis.com/auth/trace.append",
                ],
            }
        ],
        "metadata": {
            "items": [
                {
                    "key": "startup-script",
                    "value": startup,
                },
            ]
        },
        "scheduling": {
            "preemptible": True,
        },
        "shieldedInstanceConfig": {
            "enableIntegrityMonitoring": True,
            "enableSecureBoot": True,
            "enableVtpm": True,
        },
    }

    return compute.instances().insert(project=project, zone=zone, body=config).execute()


def __delete_instance(compute: Resource, project: str, server_name: str, zone: str) -> dict:
    return compute.instances().delete(project=project, zone=zone, instance=server_name).execute()


def __get_instance(compute: Resource, project: str, server_name: str, zone: str) -> dict:
    return compute.instances().get(project=project, zone=zone, instance=server_name).execute()


def __wait_for_operation(compute: Resource, project: str, operation: dict, zone: str) -> dict:
    while True:
        result = (
            compute.zoneOperations().get(project=project, zone=zone, operation=operation).execute()
        )

        if result["status"] == "DONE":
            if "error" in result:
                raise ValueError(result["error"])

            return result

        time.sleep(1)


def __create_record(dns_name: str, dns_zone: str, project: str, ip: str) -> None:
    dns_client = Client(project=project)
    zone = dns_client.zone(name=dns_zone)
    changes = zone.changes()
    rrs = zone.resource_record_set(dns_name, record_type="A", ttl=300, rrdatas=[ip])

    for record in zone.list_resource_record_sets():
        if record.name == dns_name:
            changes.delete_record_set(record)

    changes.add_record_set(rrs)
    changes.create()


def http(_: Request) -> tuple:
    """Associate PufferPanel server public ip with given dns name."""
    compute = build("compute", "v1")
    disk_id = os.environ["DISK_ID"]
    dns_name = os.environ["DNS_NAME"]
    dns_zone = os.environ["DNS_ZONE"]
    machine_type = os.environ["MACHINE_TYPE"]
    server_name = os.environ["SERVER_NAME"]
    project = os.environ["GCP_PROJECT"]
    zone = os.environ["ZONE"]

    response_message = "Successfully "
    response_status_code = 200

    operation = None

    try:
        instance = __get_instance(compute, project, server_name, zone)
        operation = __delete_instance(compute, project, instance["name"], zone)
    except HttpError:
        operation = __create_instance(compute, disk_id, machine_type, project, server_name, zone)

    if operation:
        __wait_for_operation(compute, project, operation["name"], zone)
        response_message += f"{operation['operationType']}d {server_name}"

        if "insert" in response_message:
            response_message = response_message.replace("insert", "create")
            instance = __get_instance(compute, project, server_name, zone)
            ip = (
                instance.pop("networkInterfaces", [{}])
                .pop(0)
                .pop("accessConfigs", [{}])
                .pop(0)
                .pop("natIP", None)
            )
            __create_record(dns_name, dns_zone, project, ip)

    return (response_message, response_status_code)
