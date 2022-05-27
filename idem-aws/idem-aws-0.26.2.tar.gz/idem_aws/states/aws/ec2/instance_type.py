from typing import List


async def search(hub, ctx, name: str, filters: List = None, resource_id: str = None):
    """
    Use an un-managed Instance-type as a data-source. Supply one of the inputs as the filter.

    Args:
        hub:
        ctx:
        name(Text): The name of the Idem state.
        resource_id(Text, optional): AWS Ec2 Instance type to identify the resource.
        filters(list, optional): One or more filters: for example, tag :<key>, tag-key.
        A complete list of filters can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instance_types

    Request Syntax:
        [Idem-state-name]:
          aws.ec2.instance_type.search:
          - resource_id: 'Text'
          - filters:
            - name: 'string'
              values: 'list'
            - name: 'string'
              values: 'list'

        Examples:

            my-unmanaged-instance-type:
              aws.ec2.instance_type.search:
                - filters:
                  - name: instance-type
                    values:
                      - '*.nano'
                  - name: hypervisor
                    values:
                      - xen
                  - name: processor-info.supported-architecture
                    values:
                      - x86_64

            my_instance:
              aws.ec2.instance.present:
                - instance_type: ${aws.ec2.instance_type:my-unmanaged-instance-type:resource_id}
    """
    result = dict(
        comment=[], old_state=ctx.old_state, new_state=None, name=name, result=True
    )

    # Get the resource_id from ESM if this resource used to be managed by "present"
    if not resource_id:
        resource_id = (ctx.old_state or {}).get("resource_id")

    # Perform validation on the parameters
    syntax_validation = hub.tool.aws.search_utils.search_filter_syntax_validation(
        filters=filters
    )
    result["result"] &= syntax_validation["result"]
    if not result["result"]:
        result["comment"].append(syntax_validation["comment"])
        return result

    boto3_filter = hub.tool.aws.search_utils.convert_search_filter_to_boto3(
        filters=filters
    )

    # Get all instances that match the given filters
    ret = await hub.exec.boto3.client.ec2.describe_instance_types(
        ctx,
        Filters=boto3_filter,
        InstanceTypes=[resource_id] if resource_id else None,
    )
    result["result"] &= ret.result
    if not ret:
        result["comment"].append(ret.comment)
        return result

    # Get all the instance types that matched the filter
    instance_types = {i["InstanceType"] for i in ret.ret["InstanceTypes"]}

    # Check for null results
    if not instance_types:
        result["result"] = False
        result["comment"] += [
            f"Unable to find an aws.ec2.instance_type for '{name}' that matched the given filters"
        ]
        return result

    # Get the first instance from the results
    instance_type = next(iter(instance_types))

    # Add a comment if there were multiple results
    if len(instance_types) > 1:
        result["comment"] += [
            f"More than one aws.ec2.instance resource was found. Use resource '{instance_type}'"
        ]

    # Return both old_state and new_state together
    result["new_state"] = {"resource_id": instance_type}

    return result
