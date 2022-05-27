"""
hub.exec.boto3.client.rds.copy_db_cluster_parameter_group
hub.exec.boto3.client.rds.create_db_cluster_parameter_group
hub.exec.boto3.client.rds.delete_db_cluster_parameter_group
hub.exec.boto3.client.rds.describe_db_cluster_parameter_groups
hub.exec.boto3.client.rds.modify_db_cluster_parameter_group
hub.exec.boto3.client.rds.reset_db_cluster_parameter_group
"""
import copy
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    db_parameter_group_family: str,
    description: str,
    resource_id: str = None,
    tags: List = None,
) -> Dict[str, Any]:
    r"""
    Creates a new DB cluster parameter group.

    Parameters in a DB cluster parameter group apply to all of the instances in a DB cluster.

    A DB cluster parameter group is initially created with the default parameters for the database engine used by
    instances in the DB cluster. To provide custom values for any of the parameters, you must modify the group after
    creating it using ModifyDBClusterParameterGroup . Once you've created a DB cluster parameter group, you need to
    associate it with your DB cluster using ModifyDBCluster .

    When you associate a new DB cluster parameter group with a running Aurora DB cluster, reboot the DB instances in the
    DB cluster without failover for the new DB cluster parameter group and associated settings to take effect.

    Args:
        name(Text): An Idem name of the resource.
        resource_id(Text, optional): AWS DB Cluster Parameter Group name.

        db_parameter_group_family(Text): The DB cluster parameter group family name. A DB cluster
        parameter group can be associated with one and only one DB cluster parameter group family, and can be applied
        only to a DB cluster running a database engine and engine version compatible with that DB cluster parameter
        group family.
        Example: aurora5.6, aurora-postgresql9.6, mysql8.0 etc.

        description(Text): The description for the DB cluster parameter group.
        tags(List, optional): Tags to assign to the DB cluster parameter group. Defaults to None.

    Request Syntax:
        [db-cluster-parameter-group-name]:
          aws.rds.db_cluster_parameter_group.present:
            - name: 'string'
            - resource_id: 'string'
            - db_parameter_group_family: 'string'
            - description: 'string'
            - tags:
                - Key: 'string'
                  Value: 'string'
    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_present:
              aws.rds.db_cluster_parameter_group.present:
                - name: db-cluster-parameter-group-1
                - resource_id: db-cluster-parameter-group-1
                - db_parameter_group_family: aurora-5.6
                - description: Test description
                - tags:
                    - Key: Name
                      Value: db-cluster-parameter-group-1
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False
    plan_state = None
    if resource_id:
        response = await hub.exec.boto3.client.rds.describe_db_cluster_parameter_groups(
            ctx, DBClusterParameterGroupName=resource_id
        )
        if not response["result"] and not response["ret"]:
            result["comment"] = response["comment"]
            result["result"] = response["result"]
            return result
        before = response["ret"]["DBClusterParameterGroups"][0]

    if before:
        db_cluster_parameter_group_arn = before.get("DBClusterParameterGroupArn")
        ret_tag = await hub.exec.boto3.client.rds.list_tags_for_resource(
            ctx, ResourceName=db_cluster_parameter_group_arn
        )

        if ret_tag["result"]:
            result[
                "old_state"
            ] = hub.tool.aws.rds.conversion_utils.convert_raw_db_cluster_parameter_group_to_present(
                raw_resource=before, tags=ret_tag.get("ret").get("TagList")
            )
            old_tag_list = result["old_state"]["tags"]
        else:
            result["comment"] = ret_tag["comment"]
            result["result"] = False
            return result
        plan_state = copy.deepcopy(result["old_state"])

        # Update tags
        update_tags_ret = await hub.exec.aws.rds.tag.update_rds_tags(
            ctx=ctx,
            resource_arn=db_cluster_parameter_group_arn,
            old_tags=old_tag_list,
            new_tags=tags,
        )
        resource_updated = bool(update_tags_ret["ret"])
        if ctx.get("test", False):
            if db_parameter_group_family:
                plan_state["db_parameter_group_family"] = db_parameter_group_family
            if description:
                plan_state["description"] = description
            if resource_updated:
                plan_state["tags"] = update_tags_ret["ret"].get("tags")
        else:
            if not update_tags_ret["result"]:
                result["comment"] = result["comment"] + update_tags_ret["comment"]
                result["result"] = False
                return result
            if resource_updated:
                result["comment"] = hub.tool.aws.comment_utils.update_comment(
                    resource_type="aws.rds.db_cluster_parameter_group", name=name
                )
            else:
                result["comment"] = (
                    f"aws.rds.db_cluster_parameter_group '{name}' already exists",
                )
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_id": resource_id,
                    "db_parameter_group_family": db_parameter_group_family,
                    "description": description,
                    "tags": tags,
                },
            )
            result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
                resource_type="aws.rds.db_cluster_parameter_group", name=name
            )
            return result

        ret = await hub.exec.boto3.client.rds.create_db_cluster_parameter_group(
            ctx,
            **{
                "DBClusterParameterGroupName": name,
                "DBParameterGroupFamily": db_parameter_group_family,
                "Description": description,
                "Tags": tags,
            },
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + ret["comment"]
            return result

        result["comment"] = hub.tool.aws.comment_utils.create_comment(
            resource_type="aws.rds.db_cluster_parameter_group", name=name
        )

    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif (not before) or resource_updated:
            after = (
                await hub.exec.boto3.client.rds.describe_db_cluster_parameter_groups(
                    ctx, DBClusterParameterGroupName=name
                )
            )
            resource_arn = after["ret"]["DBClusterParameterGroups"][0].get(
                "DBClusterParameterGroupArn"
            )
            ret_tag = await hub.exec.boto3.client.rds.list_tags_for_resource(
                ctx, ResourceName=resource_arn
            )
            result[
                "new_state"
            ] = hub.tool.aws.rds.conversion_utils.convert_raw_db_cluster_parameter_group_to_present(
                raw_resource=after["ret"]["DBClusterParameterGroups"][0],
                tags=ret_tag.get("ret").get("TagList")
                if ret_tag.get("result")
                else None,
            )
        else:
            result["new_state"] = copy.deepcopy(result["old_state"])
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
    return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
) -> Dict[str, Any]:
    r"""
    Deletes a specified DB cluster parameter group. The DB cluster parameter group to be deleted can't be associated
    with any DB clusters. For more information on Amazon Aurora, see  What is Amazon Aurora? in the Amazon Aurora
    User Guide.  For more information on Multi-AZ DB clusters, see  Multi-AZ deployments with two readable standby
    DB instances in the Amazon RDS User Guide.

    Args:
        name(Text): An Idem name of the resource
        resource_id(Text, Optional): AWS DB Cluster Parameter Group name. Constraints: Must be the name of an existing
        DB cluster parameter group. You can't delete a default DB cluster parameter group. Can't be associated with
        any DB clusters.

    Request Syntax:
        [resource-id]:
          aws.rds.db_cluster_parameter_group.absent:
            - name: 'string'
            - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.rds.db_cluster_parameter_group.absent:
                - name: db-cluster-parameter-group-test-name
                - resource_id: db-cluster-parameter-group-test-name
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.rds.db_cluster_parameter_group", name=name
        )
        return result
    before = await hub.exec.boto3.client.rds.describe_db_cluster_parameter_groups(
        ctx, DBClusterParameterGroupName=resource_id
    )
    if not before["result"] or not before["ret"].get("DBClusterParameterGroups"):
        if "DBParameterGroupNotFound" in str(before["comment"]):
            result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
                resource_type="aws.rds.db_cluster_parameter_group", name=name
            )
        else:
            result["comment"] = before["comment"]
            result["result"] = False
        return result

    elif ctx.get("test", False):
        result[
            "old_state"
        ] = hub.tool.aws.rds.conversion_utils.convert_raw_db_cluster_parameter_group_to_present(
            raw_resource=before["ret"]["DBClusterParameterGroups"][0]
        )
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.rds.db_cluster_parameter_group", name=name
        )
    else:
        result[
            "old_state"
        ] = hub.tool.aws.rds.conversion_utils.convert_raw_db_cluster_parameter_group_to_present(
            raw_resource=before["ret"]["DBClusterParameterGroups"][0]
        )
        ret = await hub.exec.boto3.client.rds.delete_db_cluster_parameter_group(
            ctx, DBClusterParameterGroupName=resource_id
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result
        result["comment"] = hub.tool.aws.comment_utils.delete_comment(
            resource_type="aws.rds.db_cluster_parameter_group", name=name
        )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Returns a list of DBClusterParameterGroup descriptions. If a DBClusterParameterGroupName parameter is
    specified, the list will contain only the description of the specified DB cluster parameter group.  For more
    information on Amazon Aurora, see  What is Amazon Aurora? in the Amazon Aurora User Guide.  For more information
    on Multi-AZ DB clusters, see  Multi-AZ deployments with two readable standby DB instances in the Amazon RDS User
    Guide.

    Returns:
        Dict[str, Dict[str, Any]]

    Examples:

        .. code-block:: bash

            $ idem describe aws.rds.db_cluster_parameter_group
    """

    result = {}
    ret = await hub.exec.boto3.client.rds.describe_db_cluster_parameter_groups(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe db_cluster_parameter_group {ret['comment']}")
        return {}

    for resource in ret["ret"]["DBClusterParameterGroups"]:
        resource_id = resource.get("DBClusterParameterGroupName")
        resource_arn = resource.get("DBClusterParameterGroupArn")
        ret_tag = await hub.exec.boto3.client.rds.list_tags_for_resource(
            ctx, ResourceName=resource_arn
        )
        resource_translated = hub.tool.aws.rds.conversion_utils.convert_raw_db_cluster_parameter_group_to_present(
            raw_resource=resource,
            tags=ret_tag.get("ret").get("TagList") if ret_tag.get("result") else None,
        )
        result[resource_id] = {
            "aws.rds.db_cluster_parameter_group.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }
    return result
