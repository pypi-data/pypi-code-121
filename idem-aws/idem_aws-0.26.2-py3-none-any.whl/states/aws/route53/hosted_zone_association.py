import copy
import re
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    zone_id: str,
    vpc_id: str,
    vpc_region: str = None,
    resource_id: str = None,
    comment: str = None,
    timeout: Dict = None,
) -> Dict[str, Any]:
    """
    Associates the specified vpc to the specified hosted zone.

    Args:
        hub:
        ctx:
        name(Text): An Idem name of the AWS hosted zone vpc association.
        zone_id(Text): The id of hosted zone to associate to a vpc
        vpc_id(Text): The id of the vpc to associate to a hosted zone.
        vpc_region(Text, optional): The AWS region where the vpc belongs to.
                                    If the vpc_region is not specified, AWS region from credentials file will be used.
        resource_id(Text, optional): The identifier for this object, combination of hosted_zone id, vpc id and vpc region separated by a separator ':'
        comment(Text, optional): A comment about the association request.
        timeout(Dict, optional): Timeout configuration for hosted zone and vpc association.
            * create (Dict) -- Timeout configuration for creating nat gateway
                    * delay (int) -- The amount of time in seconds to wait between attempts. Defaults to 15.
                    * max_attempts(int) -- Customized timeout configuration containing delay and max attempts. Defaults to 40.

    Request Syntax:
        [zone_id:vpc_id:vpc_region]:
          aws.route53.hosted_zone_association.present:
          - resource_id: 'string'
          - zone_id: 'string'
          - vpc_id: 'string'
          - vpc_region: 'string'
          - comment: 'string'
          - timeout:
              create
                delay: 'integer'
                max_attempts: 'integer'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            Z09756241DYDBTZK8J11E:vpc-9aacf0f2:eu-central-1:
              aws.route53.hosted_zone_association.present:
                - zone_id: Z09756241DYDBTZK8J11E
                - vpc_id: vpc-9aacf0f2
                - vpc_region: eu-central-1
                - resource_id: Z09756241DYDBTZK8J11E:vpc-9aacf0f2:eu-central-1
                - timeout:
                    create:
                        delay: 15
                        max_attempts: 40

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    if resource_id:
        if (
            not re.findall(":", resource_id)
            or not len(re.findall(":", resource_id)) == 2
        ):
            result[
                "comment"
            ] = f"Incorrect aws.route53.hosted_zone_association resource_id: {resource_id}. Expected id <zoneId>:<vpcId>:<vpc region>"
            result["result"] = False
            return result
        resource = resource_id.split(":")
        vpc_region = resource[2]

    if vpc_region is None:
        vpc_region = ctx["acct"].get("region_name")
    if not (vpc_id == "resource_id_known_after_present"):
        before = await hub.exec.aws.route53.hosted_zone_association.is_hosted_zone_associated_to_vpc(
            ctx, zone_id=zone_id, vpc_id=vpc_id, vpc_region=vpc_region
        )
        if not before["result"]:
            result["result"] = False
            result["comment"] = before["comment"]
            return result
    if before and before["ret"]:
        result[
            "old_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_zone_association_to_present(
            hosted_zone_id=zone_id,
            vpc_id=vpc_id,
            vpc_region=vpc_region,
            idem_resource_name=name,
        )
        result["new_state"] = copy.deepcopy(result["old_state"])
        result["comment"] = (
            f"aws.route53.hosted_zone_association '{name}' association already exists",
        )
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "zone_id": zone_id,
                    "vpc_id": vpc_id,
                    "vpc_region": vpc_region,
                    "comment": comment,
                },
            )
            result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
                resource_type="aws.route53.hosted_zone_association", name=name
            )
            return result
        associate_ret = (
            await hub.exec.boto3.client.route53.associate_vpc_with_hosted_zone(
                ctx,
                HostedZoneId=zone_id,
                VPC={"VPCId": vpc_id, "VPCRegion": vpc_region},
                Comment=comment,
            )
        )
        result["result"] = associate_ret["result"]
        if not result["result"]:
            result["comment"] = associate_ret["comment"]
            return result

        waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
            default_delay=15,
            default_max_attempts=40,
            timeout_config=timeout.get("create") if timeout else None,
        )
        try:
            await hub.tool.boto3.client.wait(
                ctx,
                "route53",
                "resource_record_sets_changed",
                Id=associate_ret["ret"]["ChangeInfo"]["Id"],
                WaiterConfig=waiter_config,
            )
        except Exception as e:
            result["comment"] = result["comment"] + (str(e),)
            result["result"] = False

        resource_id = f"{zone_id}:{vpc_id}:{vpc_region}"
        result["comment"] = hub.tool.aws.comment_utils.create_comment(
            resource_type="aws.route53.hosted_zone_association", name=name
        )

        result[
            "new_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_zone_association_to_present(
            hosted_zone_id=zone_id,
            vpc_id=vpc_id,
            vpc_region=vpc_region,
            idem_resource_name=resource_id,
            comment=associate_ret["ret"]["ChangeInfo"].get("Comment"),
        )

    return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    comment: str = None,
    timeout: Dict = None,
) -> Dict[str, Any]:
    """

    Removes the specified managed policy from the specified role.

    Args:
        name(Text): An Idem name of the AWS hosted zone vpc association.
        resource_id(Text, optional): The id of the hosted zone and vpc association. Idem automatically considers this resource being absent
         if this field is not specified.
        comment(Text, optional): A comment about the disassociation request.
        timeout(Dict, optional): Timeout configuration for hosted zone and vpc association.
            * delete (Dict) -- Timeout configuration for creating nat gateway
                    * delay (int) -- The amount of time in seconds to wait between attempts. Defaults to 15.
                    * max_attempts(int) -- Customized timeout configuration containing delay and max attempts. Defaults to 40.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            Z09756241DYDBTZK8J11E:vpc-9aacf0f2:eu-central-1:
              aws.route53.hosted_zone_association.absent:
                - name: Z09756241DYDBTZK8J11E:vpc-9aacf0f2:eu-central-1
                - resource_id: Z09756241DYDBTZK8J11E:vpc-9aacf0f2:eu-central-1
                - timeout:
                    delete:
                        delay: 15
                        max_attempts: 40
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.route53.hosted_zone_association", name=name
        )
        return result
    if not re.findall(":", resource_id) or not len(re.findall(":", resource_id)) == 2:
        result[
            "comment"
        ] = f"Incorrect aws.route53.hosted_zone_association resource_id: {resource_id}. Expected id <zoneId>:<vpcId>:<vpc region>"
        result["result"] = False
        return result
    resource = resource_id.split(":")
    zone_id = resource[0]
    vpc_id = resource[1]
    vpc_region = resource[2]

    if not vpc_region:
        vpc_region = ctx["acct"].get("region_name")

    before_ret = await hub.exec.aws.route53.hosted_zone_association.is_hosted_zone_associated_to_vpc(
        ctx, zone_id=zone_id, vpc_id=vpc_id, vpc_region=vpc_region
    )

    if not before_ret["result"]:
        if "InvalidInput" in before_ret["comment"][0]:
            result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
                resource_type="aws.route53.hosted_zone_association", name=name
            )
        else:
            result["comment"] = before_ret["comment"]
            result["result"] = False
        return result
    if not before_ret["ret"]:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.route53.hosted_zone_association", name=name
        )
        return result
    else:
        result[
            "old_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_zone_association_to_present(
            hosted_zone_id=zone_id,
            vpc_id=vpc_id,
            vpc_region=vpc_region,
            idem_resource_name=name,
        )
        if ctx.get("test", False):
            result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
                resource_type="aws.route53.hosted_zone_association", name=name
            )
            return result
        disassociate_ret = (
            await hub.exec.boto3.client.route53.disassociate_vpc_from_hosted_zone(
                ctx,
                HostedZoneId=zone_id,
                VPC={"VPCRegion": vpc_region, "VPCId": vpc_id},
                Comment=comment,
            )
        )
        result["result"] = disassociate_ret["result"]
        if not result["result"]:
            result["comment"] = disassociate_ret["comment"]
            return result

        waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
            default_delay=15,
            default_max_attempts=40,
            timeout_config=timeout.get("delete") if timeout else None,
        )
        try:
            await hub.tool.boto3.client.wait(
                ctx,
                "route53",
                "resource_record_sets_changed",
                Id=disassociate_ret["ret"]["ChangeInfo"]["Id"],
                WaiterConfig=waiter_config,
            )
        except Exception as e:
            result["comment"] = result["comment"] + (str(e),)
            result["result"] = False
        result["comment"] = hub.tool.aws.comment_utils.delete_comment(
            resource_type="aws.route53.hosted_zone_association", name=name
        )

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    """

    Describe the resource in a way that can be recreated/managed with the corresponding "present" function


    Lists the associated vpc's with respective hosted zones. If there are no vpc associated with the specified hosted
    zone, the operation returns an empty dict.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.route53.hosted_zone_association

    """

    result = {}
    ret = await hub.exec.boto3.client.route53.list_hosted_zones(ctx)

    if not ret["result"]:
        hub.log.debug(f"Could not describe aws.route53.hosted_zone, {ret['comment']}")
        return {}

    for hosted_zone in ret["ret"]["HostedZones"]:

        hosted_zone_id = hosted_zone.get("Id")

        hosted_zone_details = await hub.exec.boto3.client.route53.get_hosted_zone(
            ctx, Id=hosted_zone_id
        )
        if hosted_zone_details and hosted_zone_details["ret"].get("VPCs"):
            associated_vpcs = hosted_zone_details["ret"].get("VPCs")

            for vpc in associated_vpcs:
                vpc_id = vpc.get("VPCId")
                vpc_region = vpc.get("VPCRegion")
                hosted_zone_id = hosted_zone_id.split("/")[-1]

                resource_id = f"{hosted_zone_id}:{vpc_id}:{vpc_region}"
                translated_resource = hub.tool.aws.route53.conversion_utils.convert_raw_zone_association_to_present(
                    hosted_zone_id=hosted_zone_id,
                    vpc_id=vpc_id,
                    vpc_region=vpc_region,
                    idem_resource_name=resource_id,
                )

                result[resource_id] = {
                    "aws.route53.hosted_zone_association.present": [
                        {parameter_key: parameter_value}
                        for parameter_key, parameter_value in translated_resource.items()
                    ]
                }
    return result
