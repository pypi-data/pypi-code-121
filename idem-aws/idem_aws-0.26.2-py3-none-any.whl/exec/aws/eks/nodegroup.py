from typing import Dict
from typing import List

from dict_tools import differ


async def update_nodegroup(
    hub,
    ctx,
    name: str,
    before: Dict,
    version: str,
    release_version: str,
    launch_template: Dict,
    labels: Dict,
    taints: List,
    scaling_config: Dict,
    update_config: Dict,
    client_request_token: Dict,
    timeout: Dict,
):
    """
    Updates an Amazon EKS node group

    Args:
       hub:
       ctx:
       name: An Idem name of the resource
       before(Dict): AWS cluster
       release_version(Text): The AMI version of the Amazon EKS optimized AMI to use with your node group.
                              By default, the latest available AMI version for the node group's current Kubernetes version is used. For
                              more information, see Amazon EKS optimized Amazon Linux 2 AMI versions in the Amazon EKS User Guide . If you
                              specify launchTemplate , and your launch template uses a custom AMI, then don't specify releaseVersion ,
                              or the node group deployment will fail. For more information about using launch templates with Amazon EKS,
                              see Launch template support in the Amazon EKS User Guide.

       version(Text): The desired Kubernetes version for your cluster
       launch_template(Dict): An object representing a node group's launch template specification. If
                              specified, then do not specify instanceTypes , diskSize , or remoteAccess and make sure that the launch
                              template meets the requirements in launchTemplateSpecification.
       update_config(Dict): The node group update configuration
       scaling_config(Dict): The scaling configuration details for the Auto Scaling group that is created
                                       for your node group
       taints(List): The Kubernetes taints to be applied to the nodes in the node group.
       labels(Dict): The Kubernetes labels to be applied to the nodes in the node group when they are created.
       client_request_token(Text):Unique, case-sensitive identifier that you provide to ensure the idempotency of the request.
                                  This field is autopopulated if not provided.
       timeout(Dict, optional): Timeout configuration for creating or updating nodegroup.
            * create (Dict) -- Timeout configuration for creating nodegroup
                * delay(int, default=30) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=80) -- Customized timeout configuration containing delay and max attempts.
            * update (string) -- Timeout configuration for updating nodegroup
                * delay(int, default=30) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=80) -- Customized timeout configuration containing delay and max attempts.

    Returns:
       {"result": True|False, "comment": A message Tuple, "ret": Dict}
    """
    result = dict(comment=(), result=True, ret={})

    # change depends on version, releaseVersion,
    update_version_payload = {}
    waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
        default_delay=30,
        default_max_attempts=80,
        timeout_config=timeout.get("update") if timeout else None,
    )
    if version and before.get("version") != version:
        update_version_payload["version"] = version
    if release_version and before.get("release_version") != release_version:
        update_version_payload["releaseVersion"] = release_version
    if update_version_payload:
        if not ctx.get("test", False):
            ret = await hub.exec.boto3.client.eks.update_nodegroup_version(
                ctx,
                nodegroupName=before["resource_id"],
                clusterName=before["cluster_name"],
                launchTemplate=launch_template,
                clientRequestToken=client_request_token,
                **update_version_payload,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
            else:
                hub.log.debug(f"Waiting on updating aws.eks.nodegroup '{name}'")
                try:
                    await hub.tool.boto3.client.wait(
                        ctx,
                        "eks",
                        "nodegroup_active",
                        nodegroupName=before.get("resource_id"),
                        clusterName=before.get("cluster_name"),
                        WaiterConfig=waiter_config,
                    )
                except Exception as e:
                    result["comment"] = result["comment"] + (str(e),)
                    result["result"] = False
                    return result
        if "version" in update_version_payload:
            result["ret"]["version"] = version
            result["comment"] = result["comment"] + (
                f"Update cluster nodegroup version: {version} on nodegroup {before.get('resource_id')}",
            )
        if "releaseVersion" in update_version_payload:
            result["ret"]["release_version"] = version
            result["comment"] = result["comment"] + (
                f"Update cluster nodegroup release_version: {release_version} on nodegroup {before.get('resource_id')}",
            )

    # change depends on labels, scaling_group, taint, update_config
    node_config_change = hub.tool.aws.eks.eks_utils.get_updated_node_group_config(
        before,
        labels,
        taints,
        scaling_config,
        update_config,
    )
    if node_config_change:
        if not ctx.get("test", False):
            ret = await hub.exec.boto3.client.eks.update_nodegroup_config(
                ctx,
                nodegroupName=before["resource_id"],
                clusterName=before["cluster_name"],
                labels=node_config_change.get("labels"),
                taints=node_config_change.get("taints"),
                scalingConfig=node_config_change.get("scaling_config"),
                updateConfig=node_config_change.get("update_config"),
                clientRequestToken=client_request_token,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + ret["comment"]
                result["result"] = False
                return result
            else:
                hub.log.debug(f"Waiting on updating aws.eks.nodegroup '{name}'")
                try:
                    await hub.tool.boto3.client.wait(
                        ctx,
                        "eks",
                        "nodegroup_active",
                        nodegroupName=before.get("resource_id"),
                        clusterName=before.get("cluster_name"),
                        WaiterConfig=waiter_config,
                    )
                except Exception as e:
                    result["comment"] = result["comment"] + (str(e),)
                    result["result"] = False
                    return result
        for node_config_change_param in node_config_change:
            result["ret"][node_config_change_param] = node_config_change[
                node_config_change_param
            ]
            result["comment"] = result["comment"] + (
                f"Update cluster nodegroup {node_config_change_param}: {str(node_config_change[node_config_change_param])} on nodegroup {before.get('resource_id')}",
            )
    return result
