import copy
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    hosted_zone_name: str,
    caller_reference: str,
    resource_id: str = None,
    config: Dict = None,
    vpcs: Dict = None,
    delegation_set_id: str = None,
    tags: List = None,
) -> Dict[str, Any]:
    r"""
        Creates a new public or private hosted zone. You create records in a public hosted zone to define how you want
        to route traffic on the internet for a domain, such as example.com, and its subdomains (apex.example.com,
        acme.example.com). You create records in a private hosted zone to define how you want to route traffic for a
        domain and its subdomains within one or more Amazon Virtual Private Clouds (Amazon VPCs).   You can't convert a
        public hosted zone to a private hosted zone or vice versa. Instead, you must create a new hosted zone with the
        same name and create new resource record sets.  For more information about charges for hosted zones, see Amazon
        Route 53 Pricing. Note the following:   You can't create a hosted zone for a top-level domain (TLD) such as
        .com.   For public hosted zones, Route 53 automatically creates a default SOA record and four NS records for the
        zone. For more information about SOA and NS records, see NS and SOA Records that Route 53 Creates for a Hosted
        Zone in the Amazon Route 53 Developer Guide. If you want to use the same name servers for multiple public hosted
        zones, you can optionally associate a reusable delegation set with the hosted zone. See the DelegationSetId
        element.   If your domain is registered with a registrar other than Route 53, you must update the name servers
        with your registrar to make Route 53 the DNS service for the domain. For more information, see Migrating DNS
        Service for an Existing Domain to Amazon Route 53 in the Amazon Route 53 Developer Guide.    When you submit a
        CreateHostedZone request, the initial status of the hosted zone is PENDING. For public hosted zones, this means
        that the NS and SOA records are not yet available on all Route 53 DNS servers. When the NS and SOA records are
        available, the status of the zone changes to INSYNC. The CreateHostedZone request requires the caller to have an
        ec2:DescribeVpcs permission.

        Args:
            name(Text): An Idem name of the hosted zone resource.
            hosted_zone_name(Text): A unique string that identifies a hosted zone.
            caller_reference(Text): A unique string that identifies the request and that allows failed CreateHostedZone
                                      requests to be retried without the risk of executing the operation twice.
                                      You must use a unique CallerReference string every time you submit a CreateHostedZone request.
                                      CallerReference can be any unique string, for example, a date/time stamp.,
            resource_id(Text, optional): AWS route53 hosted zone ID.
            config(dictionary, optional):A complex type that contains the following optional values: Defaults to None
                * Comment(Text) -- Any comments that you want to include about the hosted zone.
                * PrivateZone(boolean) -- A value that indicates whether this is a private hosted zone.
            vpcs(dictionary, optional): A complex type that contains information about the Amazon VPC that you're associating with
                                 this hosted zone. Defaults to None
                * VPCId(Text) -- (Private hosted zones only) The region that an Amazon VPC was created in.
                * VPCRegion(Text) -- (Private hosted zones only) The ID of an Amazon VPC.
            delegation_set_id(string, optional): Id of a reusable delegation set,
            tags(List, optional): The tags to assign to the VPC. Defaults to None.
                * Key (Text) -- The key of the tag. Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws: .
                * Value (Text) -- The value of the tag. Tag values are case-sensitive and accept a maximum of 255 Unicode characters.


            Request Syntax:
            [hosted_zone_id]:
              aws.route53.hosted_zone.present:
              - name: 'string'
              - hosted_zone_name: 'string'
              - resource_id: 'string'
              - caller_reference: 'string'
              - config:
                  PrivateZone: 'string'
                  Comment: 'string'
              - vpcs:
                  VPCId: 'string'
                  VPCRegion: 'string'
              - delegation_set_id: 'string'
    -         - tags:
                - Key: 'string'
                  Value: 'string'

        Returns:
            Dict[str, Any]

        Examples:

            .. code-block:: sls

                resource_is_present:
                  aws.route53.hosted_zone.present:
                    - name: value
                    - hosted_zone_name: value
                    - resource_id: value
                    - caller_reference: value
                    - config:
                        PrivateZone: True
                        Comment: 'description of hosted zone config'
                    - vpcs:
                        VPCId: 'vpc id'
                        VPCRegion: 'us-east1'
                    - delegation_set_id: 'string'
    -               - tags:
                        - Key: 'tag key'
                          Value: 'tag value'
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False

    if resource_id:
        before = await hub.exec.boto3.client.route53.get_hosted_zone(
            ctx, Id=resource_id
        )

    if before:
        result["comment"] = (f"aws.route53.hostedzone '{name}' already exists.",)
        old_tags = None
        tags_ret = await hub.exec.boto3.client.route53.list_tags_for_resource(
            ctx, ResourceType="hostedzone", ResourceId=resource_id
        )
        if tags_ret["result"]:
            old_tags = tags_ret["ret"].get("ResourceTagSet").get("Tags", [])
        else:
            result["result"] = False
            result["comment"] = tags_ret["comment"]
            return result

        result[
            "old_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_hosted_zone_to_present(
            raw_resource=before,
            idem_resource_name=name,
            tags=old_tags,
        )
        plan_state = copy.deepcopy(result["old_state"])
        # Check if comments needs to be updated.
        if (
            config is not None
            and config.get("Comment")
            and config.get("Comment") != plan_state["config"].get("Comment")
        ):
            if ctx.get("test", False):
                result["comment"] = result["comment"] + (
                    f"Would update aws.route53.hostedzone '{name}'",
                )
                resource_updated = True
                plan_state["config"] = config
            else:
                update_ret_comment = (
                    await hub.exec.boto3.client.route53.update_hosted_zone_comment(
                        ctx,
                        Id=resource_id,
                        Comment=config.get("Comment"),
                    )
                )
                if update_ret_comment["result"]:
                    resource_updated = True
                    comment = config.get("Comment")
                    result["comment"] = result["comment"] + (
                        f"Updated comment to '{comment}'",
                    )
                else:
                    result["comment"] = update_ret_comment["comment"]
                    result["result"] = False

        # Check if tags needs to be updated
        if tags is not None:
            update_ret_tags = await hub.exec.aws.route53.tag.update_tags(
                ctx,
                resource_type="hostedzone",
                resource_id=resource_id,
                old_tags=old_tags,
                new_tags=tags,
            )
            result["comment"] = result["comment"] + update_ret_tags["comment"]
            if not update_ret_tags["result"]:
                result["result"] = False
                return result
            resource_updated = resource_updated or bool(update_ret_tags["ret"])
            if ctx.get("test", False) and update_ret_tags["ret"]:
                plan_state["tags"] = update_ret_tags["ret"].get("tags")
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "hosted_zone_name": hosted_zone_name,
                    "caller_reference": caller_reference,
                    "config": config,
                    "vpcs": vpcs,
                    "delegation_set_id": delegation_set_id,
                    "tags": tags,
                },
            )
            result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
                resource_type="aws.route53.hosted_zone", name=name
            )
            return result

        ret = await hub.exec.boto3.client.route53.create_hosted_zone(
            ctx,
            Name=hosted_zone_name,
            VPC=vpcs,
            CallerReference=caller_reference,
            HostedZoneConfig=config,
            DelegationSetId=delegation_set_id,
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result

        result["comment"] = hub.tool.aws.comment_utils.create_comment(
            resource_type="aws.route53.hosted_zone", name=name
        )
        resource_id = ret["ret"]["HostedZone"]["Id"].split("/")[-1]
        if tags is not None:
            # add tag
            add_tags = await hub.exec.aws.route53.tag.update_tags(
                ctx,
                resource_type="hostedzone",
                resource_id=resource_id,
                old_tags=None,
                new_tags=tags,
            )
            if not add_tags["result"]:
                error = add_tags["comment"]
                result["result"] = False
                hub.log.debug(f"Tag addition failed for {name} with error {error}")
                result["comment"] = result["comment"] + add_tags["comment"]

    if ctx.get("test", False):
        result["new_state"] = plan_state
    elif (not before) or resource_updated:
        after = await hub.exec.boto3.client.route53.get_hosted_zone(ctx, Id=resource_id)
        if after["result"]:
            tags_ret = await hub.exec.boto3.client.route53.list_tags_for_resource(
                ctx,
                ResourceType="hostedzone",
                ResourceId=resource_id,
            )
            if tags_ret["result"]:
                tags = tags_ret["ret"]["ResourceTagSet"].get("Tags")
            result[
                "new_state"
            ] = hub.tool.aws.route53.conversion_utils.convert_raw_hosted_zone_to_present(
                raw_resource=after,
                idem_resource_name=name,
                tags=tags,
            )
    else:
        result["new_state"] = copy.deepcopy(result["old_state"])
    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    r"""
    **Autogenerated function**

    Deletes a hosted zone. If the hosted zone was created by another service, such as Cloud Map, see Deleting Public
    Hosted Zones That Were Created by Another Service in the Amazon Route 53 Developer Guide for information about
    how to delete it. (The process is the same for public and private hosted zones that were created by another
    service.) If you want to keep your domain registration but you want to stop routing internet traffic to your
    website or web application, we recommend that you delete resource record sets in the hosted zone instead of
    deleting the hosted zone.  If you delete a hosted zone, you can't undelete it. You must create a new hosted zone
    and update the name servers for your domain registration, which can require up to 48 hours to take effect. (If
    you delegated responsibility for a subdomain to a hosted zone and you delete the child hosted zone, you must
    update the name servers in the parent hosted zone.) In addition, if you delete a hosted zone, someone could
    hijack the domain and route traffic to their own resources using your domain name.  If you want to avoid the
    monthly charge for the hosted zone, you can transfer DNS service for the domain to a free DNS service. When you
    transfer DNS service, you have to update the name servers for the domain registration. If the domain is
    registered with Route 53, see UpdateDomainNameservers for information about how to replace Route 53 name servers
    with name servers for the new DNS service. If the domain is registered with another registrar, use the method
    provided by the registrar to update name servers for the domain registration. For more information, perform an
    internet search on "free DNS service." You can delete a hosted zone only if it contains only the default SOA
    record and NS resource record sets. If the hosted zone contains other resource record sets, you must delete them
    before you can delete the hosted zone. If you try to delete a hosted zone that contains other resource record
    sets, the request fails, and Route 53 returns a HostedZoneNotEmpty error. For information about deleting records
    from your hosted zone, see ChangeResourceRecordSets. To verify that the hosted zone has been deleted, do one of
    the following:   Use the GetHostedZone action to request information about the hosted zone.   Use the
    ListHostedZones action to get a list of the hosted zones associated with the current Amazon Web Services
    account.

    Args:
        name(Text): An Idem name of the hosted zone resource.
        resource_id(Text, optional): AWS route53 hosted zone ID. Idem automatically considers this resource being absent
         if this field is not specified.

    Request Syntax:
        [hosted-zone-name]:
          aws.route53.hosted_zone.present:
          - name: 'string'
          - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.route53.hosted_zone.absent:
                - name: value
                - resource_id: value
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.route53.hosted_zone", name=name
        )
        return result
    before = await hub.exec.boto3.client.route53.get_hosted_zone(ctx, Id=resource_id)

    if not before["result"]:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.route53.hosted_zone", name=name
        )
    else:
        tags = None
        tags_ret = await hub.exec.boto3.client.route53.list_tags_for_resource(
            ctx, ResourceType="hostedzone", ResourceId=resource_id
        )
        if tags_ret["result"]:
            tags = tags_ret["ret"]["ResourceTagSet"].get("Tags")
        result[
            "old_state"
        ] = hub.tool.aws.route53.conversion_utils.convert_raw_hosted_zone_to_present(
            raw_resource=before,
            idem_resource_name=name,
            tags=tags,
        )
        if ctx.get("test", False):
            result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
                resource_type="aws.route53.hosted_zone", name=name
            )
            return result
        ret = await hub.exec.boto3.client.route53.delete_hosted_zone(
            ctx, Id=resource_id
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result
        result["comment"] = hub.tool.aws.comment_utils.delete_comment(
            resource_type="aws.route53.hosted_zone", name=name
        )

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    **Autogenerated function**

    Describe the resource in a way that can be recreated/managed with the corresponding "present" function


    Retrieves a list of the public and private hosted zones that are associated with the current Amazon Web Services
    account.


    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.route53.hosted_zone
    """

    result = {}

    ret = await hub.exec.boto3.client.route53.list_hosted_zones(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe hosted_zone {ret['comment']}")
        return result

    for hosted_zone in ret["ret"]["HostedZones"]:
        tags = None
        resource_id = hosted_zone.get("Id")
        resource_id = resource_id.split("/")[-1]
        individual_hosted_zone = await hub.exec.boto3.client.route53.get_hosted_zone(
            ctx, Id=resource_id
        )

        tags_ret = await hub.exec.boto3.client.route53.list_tags_for_resource(
            ctx, ResourceType="hostedzone", ResourceId=resource_id
        )
        if tags_ret["result"]:
            tags = tags_ret["ret"]["ResourceTagSet"].get("Tags")

        resource_translated = (
            hub.tool.aws.route53.conversion_utils.convert_raw_hosted_zone_to_present(
                raw_resource=individual_hosted_zone,
                idem_resource_name=resource_id,
                tags=tags,
            )
        )
        result[resource_id] = {
            "aws.route53.hosted_zone.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }

    return result


async def search(
    hub,
    ctx,
    name: str,
    hosted_zone_name: str = None,
    resource_id: str = None,
    private_zone: bool = None,
    vpc_id: str = None,
    tags: List = None,
):
    """
    Use an un-managed hosted_zone as a data-source. Supply one or more of the inputs as the filter.

    Args:
        name(string): The name of the Idem state.
        hosted_zone_name(string, optional): The domain name of hosted_zone
        resource_id(string, optional): AWS hosted_zone id to filter the resource.If resource_id is mentioned then we
                                       directly return the resource without checking other filters
        private_zone(bool, optional): Bool argument to specify a private hosted_zone. One of the filter option for hosted_zone
        vpc_id(string, optional):The vpc_id associated with the hosted_zone.One of the filter option for hosted_zone
        tags(List, optional): Tags of the hosted_zone. One of the filter option for hosted_zone


    Request Syntax:
        [Idem-state-name]:
          aws.route53.hosted_zone.search:
          - hosted_zone_name: 'string'
          - resource_id: 'string'
          - private_zone: 'bool'
          - vpc_id: 'string'
          - tags: 'List'

    Returns:
        {"comment": A message tuple, "old_state": Dict, "new_state": Dict, "name": string, "result": bool}

        Examples:

            my-unmanaged-hosted_zone:
              aws.route53.hosted_zone.search:
                - hosted_zone_name: idem-test-example-86a1d12e-4d68-4979-96ff-8608c33e4b9f.com.
                - resource_id: Z02905093MT09M4X5AHR5
                - private_zone: false
                - vpc_id: vpc-0e87ce8f2c3317d53
                - tags:
                  - Key: Name
                    Value: idem-test-hosted_zone

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if resource_id:
        # If resource_id is mentioned directly returning the hosted_zone
        ret = await hub.exec.boto3.client.route53.get_hosted_zone(ctx, Id=resource_id)
        if not ret["result"]:
            result["result"] = ret["result"]
            result["comment"] = (
                f"Could not find hosted_zone with given {resource_id} resource_id {ret['comment']}",
            )
            return result
        result["comment"] = (
            f"Found hosted_zone with given resource_id {resource_id}, other filters will not be considered",
        )
        hosted_zone = ret
        tags_ret = await hub.exec.boto3.client.route53.list_tags_for_resource(
            ctx, ResourceType="hostedzone", ResourceId=resource_id
        )
        if not tags_ret["result"]:
            result["comment"] = tags_ret["comment"]
            result["result"] = False
            return result
        tags = tags_ret["ret"]["ResourceTagSet"].get("Tags")
    else:
        # Get all the hosted_zones to apply the filters
        describe_ret = await hub.exec.aws.route53.hosted_zone.get_all_hosted_zones(ctx)
        if not describe_ret["result"]:
            result["result"] = False
            result["comment"] = (
                f"Could not describe all the aws.route53.hosted_zone resources to apply the filters, {describe_ret['comment']}",
            )
            return result

        ret = hub.tool.aws.route53.hosted_zone_utils.get_hosted_zone_with_filters(
            raw_hosted_zones=describe_ret["ret"],
            hosted_zone_name=hosted_zone_name,
            private_zone=private_zone,
            vpc_id=vpc_id,
            tags=tags,
        )
        result["comment"] = result["comment"] + ret["comment"]
        if not ret["ret"]:
            result["result"] = ret["result"]
            return result

        hosted_zone = ret["ret"]
        tags = hosted_zone.get("tags")

    result[
        "old_state"
    ] = hub.tool.aws.route53.conversion_utils.convert_raw_hosted_zone_to_present(
        raw_resource=hosted_zone,
        idem_resource_name=name,
        tags=tags,
    )
    # Populate both "old_state" and "new_state" with the same data
    result["new_state"] = copy.deepcopy(result["old_state"])

    return result
