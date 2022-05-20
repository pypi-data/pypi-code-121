# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs
from ._inputs import *

__all__ = ['InferenceClusterArgs', 'InferenceCluster']

@pulumi.input_type
class InferenceClusterArgs:
    def __init__(__self__, *,
                 kubernetes_cluster_id: pulumi.Input[str],
                 machine_learning_workspace_id: pulumi.Input[str],
                 cluster_purpose: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 identity: Optional[pulumi.Input['InferenceClusterIdentityArgs']] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 ssl: Optional[pulumi.Input['InferenceClusterSslArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a InferenceCluster resource.
        :param pulumi.Input[str] kubernetes_cluster_id: The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] machine_learning_workspace_id: The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] cluster_purpose: The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] description: The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input['InferenceClusterIdentityArgs'] identity: An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] location: The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] name: The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input['InferenceClusterSslArgs'] ssl: A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        pulumi.set(__self__, "kubernetes_cluster_id", kubernetes_cluster_id)
        pulumi.set(__self__, "machine_learning_workspace_id", machine_learning_workspace_id)
        if cluster_purpose is not None:
            pulumi.set(__self__, "cluster_purpose", cluster_purpose)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if identity is not None:
            pulumi.set(__self__, "identity", identity)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if ssl is not None:
            pulumi.set(__self__, "ssl", ssl)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="kubernetesClusterId")
    def kubernetes_cluster_id(self) -> pulumi.Input[str]:
        """
        The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "kubernetes_cluster_id")

    @kubernetes_cluster_id.setter
    def kubernetes_cluster_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "kubernetes_cluster_id", value)

    @property
    @pulumi.getter(name="machineLearningWorkspaceId")
    def machine_learning_workspace_id(self) -> pulumi.Input[str]:
        """
        The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "machine_learning_workspace_id")

    @machine_learning_workspace_id.setter
    def machine_learning_workspace_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "machine_learning_workspace_id", value)

    @property
    @pulumi.getter(name="clusterPurpose")
    def cluster_purpose(self) -> Optional[pulumi.Input[str]]:
        """
        The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "cluster_purpose")

    @cluster_purpose.setter
    def cluster_purpose(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cluster_purpose", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def identity(self) -> Optional[pulumi.Input['InferenceClusterIdentityArgs']]:
        """
        An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "identity")

    @identity.setter
    def identity(self, value: Optional[pulumi.Input['InferenceClusterIdentityArgs']]):
        pulumi.set(self, "identity", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def ssl(self) -> Optional[pulumi.Input['InferenceClusterSslArgs']]:
        """
        A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "ssl")

    @ssl.setter
    def ssl(self, value: Optional[pulumi.Input['InferenceClusterSslArgs']]):
        pulumi.set(self, "ssl", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _InferenceClusterState:
    def __init__(__self__, *,
                 cluster_purpose: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 identity: Optional[pulumi.Input['InferenceClusterIdentityArgs']] = None,
                 kubernetes_cluster_id: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 machine_learning_workspace_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 ssl: Optional[pulumi.Input['InferenceClusterSslArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering InferenceCluster resources.
        :param pulumi.Input[str] cluster_purpose: The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] description: The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input['InferenceClusterIdentityArgs'] identity: An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] kubernetes_cluster_id: The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] location: The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] machine_learning_workspace_id: The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] name: The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input['InferenceClusterSslArgs'] ssl: A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        if cluster_purpose is not None:
            pulumi.set(__self__, "cluster_purpose", cluster_purpose)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if identity is not None:
            pulumi.set(__self__, "identity", identity)
        if kubernetes_cluster_id is not None:
            pulumi.set(__self__, "kubernetes_cluster_id", kubernetes_cluster_id)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if machine_learning_workspace_id is not None:
            pulumi.set(__self__, "machine_learning_workspace_id", machine_learning_workspace_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if ssl is not None:
            pulumi.set(__self__, "ssl", ssl)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="clusterPurpose")
    def cluster_purpose(self) -> Optional[pulumi.Input[str]]:
        """
        The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "cluster_purpose")

    @cluster_purpose.setter
    def cluster_purpose(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cluster_purpose", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def identity(self) -> Optional[pulumi.Input['InferenceClusterIdentityArgs']]:
        """
        An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "identity")

    @identity.setter
    def identity(self, value: Optional[pulumi.Input['InferenceClusterIdentityArgs']]):
        pulumi.set(self, "identity", value)

    @property
    @pulumi.getter(name="kubernetesClusterId")
    def kubernetes_cluster_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "kubernetes_cluster_id")

    @kubernetes_cluster_id.setter
    def kubernetes_cluster_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kubernetes_cluster_id", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="machineLearningWorkspaceId")
    def machine_learning_workspace_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "machine_learning_workspace_id")

    @machine_learning_workspace_id.setter
    def machine_learning_workspace_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "machine_learning_workspace_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def ssl(self) -> Optional[pulumi.Input['InferenceClusterSslArgs']]:
        """
        A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "ssl")

    @ssl.setter
    def ssl(self, value: Optional[pulumi.Input['InferenceClusterSslArgs']]):
        pulumi.set(self, "ssl", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


class InferenceCluster(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_purpose: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 identity: Optional[pulumi.Input[pulumi.InputType['InferenceClusterIdentityArgs']]] = None,
                 kubernetes_cluster_id: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 machine_learning_workspace_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 ssl: Optional[pulumi.Input[pulumi.InputType['InferenceClusterSslArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Manages a Machine Learning Inference Cluster.

        > **NOTE:** The Machine Learning Inference Cluster resource is used to attach an existing AKS cluster to the Machine Learning Workspace, it doesn't create the AKS cluster itself. Therefore it can only be created and deleted, not updated. Any change to the configuration will recreate the resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_client_config()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup",
            location="west europe",
            tags={
                "stage": "example",
            })
        example_insights = azure.appinsights.Insights("exampleInsights",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            application_type="web")
        example_key_vault = azure.keyvault.KeyVault("exampleKeyVault",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            tenant_id=current.tenant_id,
            sku_name="standard",
            purge_protection_enabled=True)
        example_account = azure.storage.Account("exampleAccount",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            account_tier="Standard",
            account_replication_type="LRS")
        example_workspace = azure.machinelearning.Workspace("exampleWorkspace",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            application_insights_id=example_insights.id,
            key_vault_id=example_key_vault.id,
            storage_account_id=example_account.id,
            identity=azure.machinelearning.WorkspaceIdentityArgs(
                type="SystemAssigned",
            ))
        example_virtual_network = azure.network.VirtualNetwork("exampleVirtualNetwork",
            address_spaces=["10.1.0.0/16"],
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name)
        example_subnet = azure.network.Subnet("exampleSubnet",
            resource_group_name=example_resource_group.name,
            virtual_network_name=example_virtual_network.name,
            address_prefixes=["10.1.0.0/24"])
        example_kubernetes_cluster = azure.containerservice.KubernetesCluster("exampleKubernetesCluster",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            default_node_pool=azure.containerservice.KubernetesClusterDefaultNodePoolArgs(
                name="default",
                node_count=3,
                vm_size="Standard_D3_v2",
                vnet_subnet_id=example_subnet.id,
            ),
            identity=azure.containerservice.KubernetesClusterIdentityArgs(
                type="SystemAssigned",
            ))
        example_inference_cluster = azure.machinelearning.InferenceCluster("exampleInferenceCluster",
            location=example_resource_group.location,
            cluster_purpose="FastProd",
            kubernetes_cluster_id=example_kubernetes_cluster.id,
            description="This is an example cluster used with Terraform",
            machine_learning_workspace_id=example_workspace.id,
            tags={
                "stage": "example",
            })
        ```

        ## Import

        Machine Learning Inference Clusters can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:machinelearning/inferenceCluster:InferenceCluster example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/resGroup1/providers/Microsoft.MachineLearningServices/workspaces/workspace1/computes/cluster1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cluster_purpose: The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] description: The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[pulumi.InputType['InferenceClusterIdentityArgs']] identity: An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] kubernetes_cluster_id: The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] location: The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] machine_learning_workspace_id: The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] name: The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[pulumi.InputType['InferenceClusterSslArgs']] ssl: A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: InferenceClusterArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Machine Learning Inference Cluster.

        > **NOTE:** The Machine Learning Inference Cluster resource is used to attach an existing AKS cluster to the Machine Learning Workspace, it doesn't create the AKS cluster itself. Therefore it can only be created and deleted, not updated. Any change to the configuration will recreate the resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_client_config()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup",
            location="west europe",
            tags={
                "stage": "example",
            })
        example_insights = azure.appinsights.Insights("exampleInsights",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            application_type="web")
        example_key_vault = azure.keyvault.KeyVault("exampleKeyVault",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            tenant_id=current.tenant_id,
            sku_name="standard",
            purge_protection_enabled=True)
        example_account = azure.storage.Account("exampleAccount",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            account_tier="Standard",
            account_replication_type="LRS")
        example_workspace = azure.machinelearning.Workspace("exampleWorkspace",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            application_insights_id=example_insights.id,
            key_vault_id=example_key_vault.id,
            storage_account_id=example_account.id,
            identity=azure.machinelearning.WorkspaceIdentityArgs(
                type="SystemAssigned",
            ))
        example_virtual_network = azure.network.VirtualNetwork("exampleVirtualNetwork",
            address_spaces=["10.1.0.0/16"],
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name)
        example_subnet = azure.network.Subnet("exampleSubnet",
            resource_group_name=example_resource_group.name,
            virtual_network_name=example_virtual_network.name,
            address_prefixes=["10.1.0.0/24"])
        example_kubernetes_cluster = azure.containerservice.KubernetesCluster("exampleKubernetesCluster",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            default_node_pool=azure.containerservice.KubernetesClusterDefaultNodePoolArgs(
                name="default",
                node_count=3,
                vm_size="Standard_D3_v2",
                vnet_subnet_id=example_subnet.id,
            ),
            identity=azure.containerservice.KubernetesClusterIdentityArgs(
                type="SystemAssigned",
            ))
        example_inference_cluster = azure.machinelearning.InferenceCluster("exampleInferenceCluster",
            location=example_resource_group.location,
            cluster_purpose="FastProd",
            kubernetes_cluster_id=example_kubernetes_cluster.id,
            description="This is an example cluster used with Terraform",
            machine_learning_workspace_id=example_workspace.id,
            tags={
                "stage": "example",
            })
        ```

        ## Import

        Machine Learning Inference Clusters can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:machinelearning/inferenceCluster:InferenceCluster example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/resGroup1/providers/Microsoft.MachineLearningServices/workspaces/workspace1/computes/cluster1
        ```

        :param str resource_name: The name of the resource.
        :param InferenceClusterArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(InferenceClusterArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_purpose: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 identity: Optional[pulumi.Input[pulumi.InputType['InferenceClusterIdentityArgs']]] = None,
                 kubernetes_cluster_id: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 machine_learning_workspace_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 ssl: Optional[pulumi.Input[pulumi.InputType['InferenceClusterSslArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = InferenceClusterArgs.__new__(InferenceClusterArgs)

            __props__.__dict__["cluster_purpose"] = cluster_purpose
            __props__.__dict__["description"] = description
            __props__.__dict__["identity"] = identity
            if kubernetes_cluster_id is None and not opts.urn:
                raise TypeError("Missing required property 'kubernetes_cluster_id'")
            __props__.__dict__["kubernetes_cluster_id"] = kubernetes_cluster_id
            __props__.__dict__["location"] = location
            if machine_learning_workspace_id is None and not opts.urn:
                raise TypeError("Missing required property 'machine_learning_workspace_id'")
            __props__.__dict__["machine_learning_workspace_id"] = machine_learning_workspace_id
            __props__.__dict__["name"] = name
            __props__.__dict__["ssl"] = ssl
            __props__.__dict__["tags"] = tags
        super(InferenceCluster, __self__).__init__(
            'azure:machinelearning/inferenceCluster:InferenceCluster',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            cluster_purpose: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            identity: Optional[pulumi.Input[pulumi.InputType['InferenceClusterIdentityArgs']]] = None,
            kubernetes_cluster_id: Optional[pulumi.Input[str]] = None,
            location: Optional[pulumi.Input[str]] = None,
            machine_learning_workspace_id: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            ssl: Optional[pulumi.Input[pulumi.InputType['InferenceClusterSslArgs']]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'InferenceCluster':
        """
        Get an existing InferenceCluster resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cluster_purpose: The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] description: The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[pulumi.InputType['InferenceClusterIdentityArgs']] identity: An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] kubernetes_cluster_id: The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] location: The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] machine_learning_workspace_id: The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[str] name: The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[pulumi.InputType['InferenceClusterSslArgs']] ssl: A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _InferenceClusterState.__new__(_InferenceClusterState)

        __props__.__dict__["cluster_purpose"] = cluster_purpose
        __props__.__dict__["description"] = description
        __props__.__dict__["identity"] = identity
        __props__.__dict__["kubernetes_cluster_id"] = kubernetes_cluster_id
        __props__.__dict__["location"] = location
        __props__.__dict__["machine_learning_workspace_id"] = machine_learning_workspace_id
        __props__.__dict__["name"] = name
        __props__.__dict__["ssl"] = ssl
        __props__.__dict__["tags"] = tags
        return InferenceCluster(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="clusterPurpose")
    def cluster_purpose(self) -> pulumi.Output[Optional[str]]:
        """
        The purpose of the Inference Cluster. Options are `DevTest`, `DenseProd` and `FastProd`. If used for Development or Testing, use `DevTest` here. Default purpose is `FastProd`, which is recommended for production workloads. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "cluster_purpose")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        The description of the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def identity(self) -> pulumi.Output[Optional['outputs.InferenceClusterIdentity']]:
        """
        An `identity` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "identity")

    @property
    @pulumi.getter(name="kubernetesClusterId")
    def kubernetes_cluster_id(self) -> pulumi.Output[str]:
        """
        The ID of the Kubernetes Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "kubernetes_cluster_id")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        The Azure Region where the Machine Learning Inference Cluster should exist. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter(name="machineLearningWorkspaceId")
    def machine_learning_workspace_id(self) -> pulumi.Output[str]:
        """
        The ID of the Machine Learning Workspace. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "machine_learning_workspace_id")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name which should be used for this Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def ssl(self) -> pulumi.Output[Optional['outputs.InferenceClusterSsl']]:
        """
        A `ssl` block as defined below. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "ssl")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags which should be assigned to the Machine Learning Inference Cluster. Changing this forces a new Machine Learning Inference Cluster to be created.
        """
        return pulumi.get(self, "tags")

