from typing import Dict

from dict_tools import data


async def update_cluster(
    hub,
    ctx,
    name: str,
    before: Dict,
    version: str,
    encryption_config: Dict,
    resources_vpc_config: Dict,
    logging: Dict,
    client_request_token: str,
    timeout: Dict,
):
    """
    Updates an Amazon EKS cluster

    Args:
       hub:
       ctx:
       name(Text): An Idem name of the resource.
       before(Dict): AWS cluster
       logging(Dict): Enable or disable exporting the Kubernetes control plane logs for your cluster to
                                CloudWatch Logs. By default, cluster control plane logs aren't exported to CloudWatch Logs. For more
                                information, see Amazon EKS Cluster control plane logs in the * Amazon EKS User Guide *
       encryption_config(Dict): The encryption configuration for the cluster.
       resources_vpc_config(Dict): The VPC configuration that's used by the cluster control plane. Amazon
                                   EKS VPC resources have specific requirements to work properly with Kubernetes. For more information,
                                   see Cluster VPC Considerations and Cluster Security Group Considerations in the Amazon EKS User Guide . You
                                   must specify at least two subnets. You can specify up to five security groups. However, we recommend that you
                                   use a dedicated security group for your cluster control plane.
       version(Text): The desired Kubernetes version for your cluster
       client_request_token(Text):Unique, case-sensitive identifier that you provide to ensure the idempotency of the request.
                                  This field is autopopulated if not provided.
       timeout(Dict, optional): Timeout configuration for creating or updating cluster.
            * create (Dict) -- Timeout configuration for creating cluster
                * delay(int, default=60) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=40) -- Customized timeout configuration containing delay and max attempts.
            * update (string) -- Timeout configuration for updating cluster
                * delay(int, default=60) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=40) -- Customized timeout configuration containing delay and max attempts.

    Returns:
       {"result": True|False, "comment": A message Tuple, "ret": Dict}
    """
    result = dict(comment=(), result=True, ret={})
    # change depends on resourcesVpcConfig,  encryptionConfig, logging and version
    if version and before.get("version") != version:
        if not ctx.get("test", False):
            ret = await hub.exec.boto3.client.eks.update_cluster_version(
                ctx,
                name=before.get("resource_id"),
                version=version,
                clientRequestToken=client_request_token,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            else:
                waiter_ret = await hub.exec.aws.eks.cluster.cluster_waiter(
                    ctx, name, before.get("resource_id"), timeout, "update"
                )
                if not waiter_ret["result"]:
                    result["result"] = False
                    result["comment"] = result["comment"] + waiter_ret["comment"]
                    return result
        result["ret"]["version"] = version
        result["comment"] = result["comment"] + (
            f"Update cluster version: {version} on cluster {before.get('resource_id')}",
        )

    # we can associate encryption config only if its already not present.
    # If the cluster already has encryption config we cannot associate.
    if (
        encryption_config
        and not before.get("encryption_config")
        and before.get("encryption_config") != encryption_config
    ):
        if not ctx.get("test", False):
            ret = await hub.exec.boto3.client.eks.associate_encryption_config(
                ctx,
                clusterName=before.get("resource_id"),
                encryptionConfig=encryption_config,
                clientRequestToken=client_request_token,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            else:
                waiter_ret = await hub.exec.aws.eks.cluster.cluster_waiter(
                    ctx, name, before.get("resource_id"), timeout, "update"
                )
                if not waiter_ret["result"]:
                    result["result"] = False
                    result["comment"] = result["comment"] + waiter_ret["comment"]
                    return result
        result["ret"]["encryption_config"] = encryption_config
        result["comment"] = result["comment"] + (
            f"Update cluster encryption config: {encryption_config} on cluster {before.get('resource_id')}",
        )
    if logging and data.recursive_diff(
        before.get("logging"), logging, ignore_order=True
    ):
        if not ctx.get("test", False):
            ret = await hub.exec.boto3.client.eks.update_cluster_config(
                ctx,
                name=before.get("resource_id"),
                clientRequestToken=client_request_token,
                logging=logging,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            else:
                waiter_ret = await hub.exec.aws.eks.cluster.cluster_waiter(
                    ctx, name, before.get("resource_id"), timeout, "update"
                )
                if not waiter_ret["result"]:
                    result["result"] = False
                    result["comment"] = result["comment"] + waiter_ret["comment"]
                    return result
        result["ret"]["logging"] = logging
        result["comment"] = result["comment"] + (
            f"Update cluster logging: {logging} on cluster {before.get('resource_id')}",
        )
    if resources_vpc_config:
        vpc_config_changes = hub.tool.aws.eks.eks_utils.get_resource_vpc_config_changes(
            before.get("resources_vpc_config"),
            resources_vpc_config,
        )
        if vpc_config_changes:
            if not ctx.get("test", False):
                ret = await hub.exec.boto3.client.eks.update_cluster_config(
                    ctx,
                    name=before.get("resource_id"),
                    clientRequestToken=client_request_token,
                    resourcesVpcConfig=vpc_config_changes,
                )
                result["result"] = ret["result"]
                if not result["result"]:
                    result["comment"] = ret["comment"]
                    return result
                else:
                    waiter_ret = await hub.exec.aws.eks.cluster.cluster_waiter(
                        ctx, name, before.get("resource_id"), timeout, "update"
                    )
                    if not waiter_ret["result"]:
                        result["result"] = False
                        result["comment"] = result["comment"] + waiter_ret["comment"]
                        return result
            result["ret"]["resources_vpc_config"] = resources_vpc_config
            result["comment"] = result["comment"] + (
                f"Update cluster resources vpc config: {vpc_config_changes} on cluster {before.get('resource_id')}",
            )

    return result


async def cluster_waiter(
    hub, ctx, name: str, resource_id: str, timeout: Dict, operation_type: str
):
    """

    Waiter to wait for the cluster to become active.

        Args:
           hub:
           ctx:
           name(Text): An Idem name of the resource.
           resource_id(Text): Name of the cluster to Identify the resource
           timeout(Dict, optional): Timeout configuration for creating or updating cluster.
            * create (Dict) -- Timeout configuration for creating cluster
                * delay(int, default=60) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=40) -- Customized timeout configuration containing delay and max attempts.
            * update (string) -- Timeout configuration for updating cluster
                * delay(int, default=60) -- The amount of time in seconds to wait between attempts.
                * max_attempts(int, default=40) -- Customized timeout configuration containing delay and max attempts.
           operation_type(Text): create or update operation

        Returns:
            Dict[str, Any]
    """

    result = dict(comment=(), result=True, ret={})
    waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
        default_delay=60,
        default_max_attempts=40,
        timeout_config=timeout.get(operation_type) if timeout else None,
    )
    hub.log.debug(f"Waiting on {operation_type} aws.eks.cluster '{name}'")
    try:
        await hub.tool.boto3.client.wait(
            ctx,
            "eks",
            "cluster_active",
            name=resource_id,
            WaiterConfig=waiter_config,
        )
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
    return result
