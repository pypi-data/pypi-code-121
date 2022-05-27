import copy
import re
from typing import Any
from typing import Dict
from typing import List


def decompose_resource_id(hub, resource_id: str) -> Dict[str, str]:
    """
    Route53 records ID is composed of zone identifier, record name, and record type, separated by underscores (_)

    Args:
        hub: The redistributed pop central hub.
        resource_id: String formatted as <hosted_zone_id>_<record_name>_<record_type>

    Returns:
        Dict containing the different parts of the ID.
    """
    m = re.match(r"(?P<zone_id>[A-Z0-9]+)_(?P<name>\S+)_(?P<type>[A-Z]+)", resource_id)
    if not m:
        raise Exception(f"{resource_id} does not match resource_id pattern")
    (hosted_zone_id, record_name, record_type) = (
        m.group("zone_id"),
        m.group("name"),
        m.group("type"),
    )
    return {
        "hosted_zone_id": f"/hostedzone/{hosted_zone_id}",
        "name": record_name,
        "record_type": record_type,
    }


def compose_resource_id(
    hub,
    hosted_zone_id: str,
    name: str,
    record_type: str,
) -> str:
    """
    Compose ID for a resource record in a hosted zone.

    Args:
        hub: The redistributed pop central hub.
        hosted_zone_id: The ID if the hosted zone containing this record.
        name: The name of the record.
        record_type: The record type.

    Returns:
        ID of this record.
    """
    prefix = "/hostedzone/"
    suffix = "."
    zone_id = hosted_zone_id
    l_name = name
    if hosted_zone_id.startswith(prefix):
        zone_id = hosted_zone_id[len(prefix) :]
    if name.endswith(suffix):
        l_name = name[: len(name) - 1]
    return f"""{zone_id}_{l_name}_{record_type}"""


def patch_state(
    hub,
    before: Dict[str, Any],
    hosted_zone_id: str,
    ttl: int,
    resource_records: List,
    alias_target: Dict,
) -> Dict[str, Any]:
    """
    Patches the current state of the resource to match the desired state.
    hosted_zone_id, name and record_type are not considered because are used as ID for this resource.

    Args:
        hub: The redistributed pop central hub.
        before (Dict): raw state of the resource record.
        hosted_zone_id (str): ID of the hosted zone of this resource record.
        ttl (int): TTL property of resource record. See boto3 or aws documentation for details.
        resource_records (List): Resource record set. See boto3 or aws documentation for details.
        alias_target (Dict): Alias target for alias resource record set. See boto3 or aws documentation for details.

    Returns:
        Patched resource record. Hosted zone id, name and record type are part of the ID of this resource, so they are
        immutable.
    """

    ret = hub.tool.aws.route53.conversion_utils.convert_raw_resource_record_to_present(
        hosted_zone_id, before
    )
    if ttl:
        ret["ttl"] = ttl
    if resource_records:
        ret["resource_records"] = resource_records
    if alias_target:
        ret["alias_target"] = alias_target

    return ret


def create_change_batch_for_update(hub, action, resource_record) -> Any:
    """
    Create an object that will be passed to ChangeBatch argument of
    `change_resource_record_sets https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets`__

    Args:
        hub: The redistributed pop central hub.
        action(Text): 'CREATE'|'DELETE'|'UPSERT' literal.
        resource_record(Any): Idem resource record instance.

    Returns:
        Object to pass to ChangeBatch populated with the supported resource record properties
    """

    change_batch = {
        "Comment": f"{action} by idem-aws",
        "Changes": [
            {
                "Action": action,
                "ResourceRecordSet": {
                    "Name": resource_record["name"],
                    "Type": resource_record["record_type"],
                },
            },
        ],
    }
    if "ttl" in resource_record:
        change_batch["Changes"][0]["ResourceRecordSet"]["TTL"] = resource_record["ttl"]
    if "resource_records" in resource_record:
        change_batch["Changes"][0]["ResourceRecordSet"]["ResourceRecords"] = [
            {"Value": v} for v in resource_record["resource_records"]
        ]
    if "alias_target" in resource_record:
        change_batch["Changes"][0]["ResourceRecordSet"]["AliasTarget"] = {
            "HostedZoneId": resource_record["alias_target"]["hosted_zone_id"],
            "DNSName": resource_record["alias_target"]["dns_name"],
            "EvaluateTargetHealth": resource_record["alias_target"][
                "evaluate_target_health"
            ],
        }
    return change_batch


async def find_resource_record(
    hub, ctx, hosted_zone_id: str, name: str, record_type: str
) -> Dict[str, Any]:
    """
    Find a resource record in a hosted zone matching it by name and record type

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run.
        hosted_zone_id: ID of the hosted zone holding the resource record.
        name: name of the resource record.
        record_type: type of the resource record.

    Returns:
        Resource record matching the hosted_zone_id, name and record_type or None if resource record is not found.
    """

    record_sets = await hub.exec.boto3.client.route53.list_resource_record_sets(
        ctx,
        HostedZoneId=hosted_zone_id,
        StartRecordName=name,
        StartRecordType=record_type,
        MaxItems="1",
    )

    # present works on single resource record while `list_resource_record_sets` returns a list
    # expectation is if the resource record exists to be the first in the list
    if (
        record_sets["result"]
        and record_sets["ret"]["ResourceRecordSets"]
        and record_sets["ret"]["ResourceRecordSets"][0]["Name"] == name
        and record_sets["ret"]["ResourceRecordSets"][0]["Type"] == record_type
    ):
        return dict(
            result=record_sets["result"],
            comment=record_sets["comment"],
            aws_state=record_sets["ret"]["ResourceRecordSets"][0],
        )
    else:
        return dict(result=record_sets["result"], comment=record_sets["comment"])


def same_states(hub, state1: Dict[str, Any], state2: Dict[str, Any]) -> bool:
    """
    Compare Idem states for aws.route53.resource_record
    Args:
        state1(Dict[str,Any]): First state to compare
        state2(Dict[str,Any]): Second state to compare

    Returns:
        True if both states are equal, False otherwise
    """
    if state1 is None or state2 is None:
        return state1 == state2

    state1_copy = copy.deepcopy(state1)
    state2_copy = copy.deepcopy(state2)

    if "resource_records" in state1_copy and "resource_records" in state2_copy:
        state1_copy["resource_records"].sort()
        state2_copy["resource_records"].sort()
    # hosted_zone_id can come in 2 formats - /hostedzone/<id> and <id>. Convert to common format before comparison
    if not state1_copy["hosted_zone_id"].startswith("/hostedzone/"):
        state1_copy["hosted_zone_id"] = f"/hostedzone/{state1_copy['hosted_zone_id']}"
    if not state2_copy["hosted_zone_id"].startswith("/hostedzone/"):
        state2_copy["hosted_zone_id"] = f"/hostedzone/{state2_copy['hosted_zone_id']}"
    return state1_copy == state2_copy
