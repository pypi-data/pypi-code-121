"""
hub.exec.boto3.client.route53.list_resource_record_sets
hub.exec.boto3.client.route53.change_resource_record_sets
"""
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    hosted_zone_id: str,
    record_type: str,
    resource_records: List = None,
    alias_target: Dict = None,
    resource_id: str = None,
    ttl: int = None,
) -> Dict[str, Any]:
    r"""
    Creates or changes a resource record set, which contains authoritative DNS information for a specified domain name
    or subdomain name.

    Args:
        name(Text): The name of the record. A '.' will be appended if not already present.
        hosted_zone_id(Text): The ID of the hosted zone that contains the resource record sets
        record_type(Text): The DNS record type. For information about different record types and how data is encoded for
            them, see `Supported DNS Resource Record Types https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html`__
            in the Amazon Route 53 Developer Guide.
        resource_records(List, optional): Information about the resource records to act upon.
        alias_target(Dict, optional): Alias resource record sets only: Information about the Amazon Web Services resource,
            such as a CloudFront distribution or an Amazon S3 bucket, that you want to route traffic to.
        resource_id(Text, optional): Composite ID for a resource record in a hosted zone. String formatted as
            <hosted_zone_id>_<record_name>_<record_type>
        ttl(int, optional): The resource record cache time to live (TTL), in seconds.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

        KL1PX9DBMUY9WHB_www.example.com_AAAA:
          aws.route53.resource_record.present:
          - hosted_zone_id: /hostedzone/KL1PX9DBMUY9WHB
            name: www.example.com.
            record_type: AAAA
            resource_records:
            - 2001:0db8:85a3:0:0:8a2e:0370:7335
            - 2001:0db8:85a3:0:0:8a2e:0370:7334
            ttl: 300

        ZY51FUS5VYB_www.example.net_A:
          aws.route53.resource_record.present:
          - alias_target:
              dns_name: lb1.us-east-1.elb.amazonaws.com.
              evaluate_target_health: false
              hosted_zone_id: Z35SXDOTRQ7X7Z
            hosted_zone_id: /hostedzone/ZY51FUS5VYB
            name: www.example.net.
            record_type: A
            resource_id: ZY51FUS5VYB_www.example.net_A
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    # name is supposed to end with '.'.
    # Because name is used when we look up the resource record we should store the canonical form in the state
    formatted_name = name if name.endswith(".") else f"{name}."
    if resource_id:
        if (
            hub.tool.aws.route53.resource_record_utils.compose_resource_id(
                hosted_zone_id, name, record_type
            )
            != resource_id
        ):
            result["comment"] = (
                f"aws.route53.resource_record resource_id {resource_id} is not composed of {hosted_zone_id}, {name} and {record_type}",
            )
            result["result"] = False
            return result

    before_response = (
        await hub.tool.aws.route53.resource_record_utils.find_resource_record(
            ctx, hosted_zone_id, formatted_name, record_type
        )
    )
    if not before_response["result"]:
        result["comment"] = before_response["comment"]
        result["result"] = False
        return result
    before = before_response.get("aws_state")

    pending_state = None
    if before:
        result[
            "old_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_resource_record_to_present(
            hosted_zone_id=hosted_zone_id, raw_resource=before
        )
        pending_state = hub.tool.aws.route53.resource_record_utils.patch_state(
            before, hosted_zone_id, ttl, resource_records, alias_target
        )
    else:
        pending_state = {
            "name": formatted_name,
            "hosted_zone_id": hosted_zone_id,
            "resource_id": resource_id
            if resource_id
            else hub.tool.aws.route53.resource_record_utils.compose_resource_id(
                hosted_zone_id, formatted_name, record_type
            ),
            "record_type": record_type,
        }
        if ttl:
            pending_state["ttl"] = ttl
        if resource_records:
            pending_state["resource_records"] = resource_records
        if alias_target:
            pending_state["alias_target"] = alias_target
    # action can be 'CREATE'|'DELETE'|'UPSERT' - see boto documentation for change_resource_record_sets
    action = None
    if before:
        if not hub.tool.aws.route53.resource_record_utils.same_states(
            pending_state, result["old_state"]
        ):
            result["comment"] = hub.tool.aws.comment_utils.would_update_comment(
                resource_type="aws.route53.resource_record", name=formatted_name
            )
            action = "UPSERT"
        else:
            result["comment"] = (
                f"No changes would be made for aws.route53.resource_record {formatted_name}",
            )
        result["result"] = True
    else:
        result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
            resource_type="aws.route53.resource_record", name=formatted_name
        )
        action = "CREATE"
        result["result"] = True

    if ctx.get("test", False):
        result["new_state"] = pending_state
        return result

    # do the actual update
    if action:
        change_batch = (
            hub.tool.aws.route53.resource_record_utils.create_change_batch_for_update(
                action, pending_state
            )
        )
        response = await hub.exec.boto3.client.route53.change_resource_record_sets(
            ctx, HostedZoneId=hosted_zone_id, ChangeBatch=change_batch
        )
        if not response["result"]:
            result["comment"] = (
                f'Error on {action} for aws.route53.resource_record {formatted_name}: {response["comment"]}',
            )
            result["result"] = False
            return result
        result["new_state"] = pending_state
        if action == "CREATE":
            result["comment"] = hub.tool.aws.comment_utils.create_comment(
                resource_type="aws.route53.resource_record", name=formatted_name
            )
        else:
            result["comment"] = hub.tool.aws.comment_utils.update_comment(
                resource_type="aws.route53.resource_record", name=formatted_name
            )

    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    r"""
    Deletes the specified resource record

    Args:
        name(Text): Name of the resource record. Needed because of the Idem contract but not used
        resource_id(Text, optional): Composite ID for a resource record in a hosted zone. String formatted as
            <hosted_zone_id>_<record_name>_<record_type>

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            MX_record_is_absent:
              aws.route53.resource_record.absent:
                - name: www.example.com.
                - resource_id: HSHMRK8IGWBU3PU_www.example.com_MX
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.route53.resource_record", name=name
        )
        return result

    try:
        decomposed_id = (
            hub.tool.aws.route53.resource_record_utils.decompose_resource_id(
                resource_id
            )
        )
    except Exception as e:
        result["comment"] = (f"{e.__class__.__name__}: {e}",)
        result["result"] = False
        return result
    hosted_zone_id = decomposed_id["hosted_zone_id"]
    formatted_name = f"{decomposed_id['name']}."
    record_type = decomposed_id["record_type"]

    before_response = (
        await hub.tool.aws.route53.resource_record_utils.find_resource_record(
            ctx,
            hosted_zone_id,
            formatted_name,
            record_type,
        )
    )
    if not before_response["result"]:
        result["comment"] = before_response["comment"]
        result["result"] = False
        return result

    before = before_response.get("aws_state")
    if not before:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.route53.resource_record", name=formatted_name
        )
    else:
        result[
            "old_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_resource_record_to_present(
            hosted_zone_id=hosted_zone_id, raw_resource=before
        )
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.route53.resource_record", name=formatted_name
        )
        if ctx.get("test", False):
            return result
        # delete the resource record
        change_batch = (
            hub.tool.aws.route53.resource_record_utils.create_change_batch_for_update(
                "DELETE", result["old_state"]
            )
        )
        response = await hub.exec.boto3.client.route53.change_resource_record_sets(
            ctx,
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch,
        )
        if not response["result"]:
            result["comment"] = (
                f"Error deleting aws.route53.resource_record '{formatted_name}': {response['comment']}",
            )
            result["result"] = False
            return result
        result["comment"] = hub.tool.aws.comment_utils.delete_comment(
            resource_type="aws.route53.resource_record", name=formatted_name
        )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    result = {}

    hosted_zones = await hub.exec.boto3.client.route53.list_hosted_zones(ctx)
    if not hosted_zones["result"]:
        hub.log.debug(
            f"Could not describe aws.route53.resource_record. {hosted_zones['comment']}"
        )
        return result

    for hosted_zone in hosted_zones["ret"]["HostedZones"]:
        hosted_zone_id = hosted_zone.get("Id")
        ret = await hub.exec.boto3.client.route53.list_resource_record_sets(
            ctx, HostedZoneId=hosted_zone_id
        )
        if not ret["result"]:
            hub.log.debug(
                f"Could not describe aws.route53.hosted_zone {ret['comment']}"
            )
            continue

        for resource_record_set in ret["ret"]["ResourceRecordSets"]:
            resource_translated = hub.tool.aws.route53.conversion_utils.convert_raw_resource_record_to_present(
                hosted_zone_id=hosted_zone_id, raw_resource=resource_record_set
            )
            result[resource_translated["resource_id"]] = {
                "aws.route53.resource_record.present": [resource_translated]
            }

    return result
