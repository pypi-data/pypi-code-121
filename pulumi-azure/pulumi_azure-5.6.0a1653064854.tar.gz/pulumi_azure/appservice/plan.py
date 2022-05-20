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

__all__ = ['PlanArgs', 'Plan']

@pulumi.input_type
class PlanArgs:
    def __init__(__self__, *,
                 resource_group_name: pulumi.Input[str],
                 sku: pulumi.Input['PlanSkuArgs'],
                 app_service_environment_id: Optional[pulumi.Input[str]] = None,
                 is_xenon: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 maximum_elastic_worker_count: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 per_site_scaling: Optional[pulumi.Input[bool]] = None,
                 reserved: Optional[pulumi.Input[bool]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_redundant: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a Plan resource.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the App Service Plan component.
        :param pulumi.Input['PlanSkuArgs'] sku: A `sku` block as documented below.
        :param pulumi.Input[str] app_service_environment_id: The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        :param pulumi.Input[str] kind: The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_elastic_worker_count: The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        :param pulumi.Input[str] name: Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] per_site_scaling: Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        :param pulumi.Input[bool] reserved: Is this App Service Plan `Reserved`. Defaults to `false`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_redundant: Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "sku", sku)
        if app_service_environment_id is not None:
            pulumi.set(__self__, "app_service_environment_id", app_service_environment_id)
        if is_xenon is not None:
            pulumi.set(__self__, "is_xenon", is_xenon)
        if kind is not None:
            pulumi.set(__self__, "kind", kind)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if maximum_elastic_worker_count is not None:
            pulumi.set(__self__, "maximum_elastic_worker_count", maximum_elastic_worker_count)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if per_site_scaling is not None:
            pulumi.set(__self__, "per_site_scaling", per_site_scaling)
        if reserved is not None:
            pulumi.set(__self__, "reserved", reserved)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if zone_redundant is not None:
            pulumi.set(__self__, "zone_redundant", zone_redundant)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group in which to create the App Service Plan component.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def sku(self) -> pulumi.Input['PlanSkuArgs']:
        """
        A `sku` block as documented below.
        """
        return pulumi.get(self, "sku")

    @sku.setter
    def sku(self, value: pulumi.Input['PlanSkuArgs']):
        pulumi.set(self, "sku", value)

    @property
    @pulumi.getter(name="appServiceEnvironmentId")
    def app_service_environment_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        """
        return pulumi.get(self, "app_service_environment_id")

    @app_service_environment_id.setter
    def app_service_environment_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "app_service_environment_id", value)

    @property
    @pulumi.getter(name="isXenon")
    def is_xenon(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "is_xenon")

    @is_xenon.setter
    def is_xenon(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "is_xenon", value)

    @property
    @pulumi.getter
    def kind(self) -> Optional[pulumi.Input[str]]:
        """
        The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "kind")

    @kind.setter
    def kind(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kind", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="maximumElasticWorkerCount")
    def maximum_elastic_worker_count(self) -> Optional[pulumi.Input[int]]:
        """
        The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        """
        return pulumi.get(self, "maximum_elastic_worker_count")

    @maximum_elastic_worker_count.setter
    def maximum_elastic_worker_count(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "maximum_elastic_worker_count", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="perSiteScaling")
    def per_site_scaling(self) -> Optional[pulumi.Input[bool]]:
        """
        Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        """
        return pulumi.get(self, "per_site_scaling")

    @per_site_scaling.setter
    def per_site_scaling(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "per_site_scaling", value)

    @property
    @pulumi.getter
    def reserved(self) -> Optional[pulumi.Input[bool]]:
        """
        Is this App Service Plan `Reserved`. Defaults to `false`.
        """
        return pulumi.get(self, "reserved")

    @reserved.setter
    def reserved(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "reserved", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="zoneRedundant")
    def zone_redundant(self) -> Optional[pulumi.Input[bool]]:
        """
        Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        return pulumi.get(self, "zone_redundant")

    @zone_redundant.setter
    def zone_redundant(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "zone_redundant", value)


@pulumi.input_type
class _PlanState:
    def __init__(__self__, *,
                 app_service_environment_id: Optional[pulumi.Input[str]] = None,
                 is_xenon: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 maximum_elastic_worker_count: Optional[pulumi.Input[int]] = None,
                 maximum_number_of_workers: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 per_site_scaling: Optional[pulumi.Input[bool]] = None,
                 reserved: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku: Optional[pulumi.Input['PlanSkuArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_redundant: Optional[pulumi.Input[bool]] = None):
        """
        Input properties used for looking up and filtering Plan resources.
        :param pulumi.Input[str] app_service_environment_id: The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        :param pulumi.Input[str] kind: The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_elastic_worker_count: The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        :param pulumi.Input[int] maximum_number_of_workers: The maximum number of workers supported with the App Service Plan's sku.
        :param pulumi.Input[str] name: Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] per_site_scaling: Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        :param pulumi.Input[bool] reserved: Is this App Service Plan `Reserved`. Defaults to `false`.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the App Service Plan component.
        :param pulumi.Input['PlanSkuArgs'] sku: A `sku` block as documented below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_redundant: Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        if app_service_environment_id is not None:
            pulumi.set(__self__, "app_service_environment_id", app_service_environment_id)
        if is_xenon is not None:
            pulumi.set(__self__, "is_xenon", is_xenon)
        if kind is not None:
            pulumi.set(__self__, "kind", kind)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if maximum_elastic_worker_count is not None:
            pulumi.set(__self__, "maximum_elastic_worker_count", maximum_elastic_worker_count)
        if maximum_number_of_workers is not None:
            pulumi.set(__self__, "maximum_number_of_workers", maximum_number_of_workers)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if per_site_scaling is not None:
            pulumi.set(__self__, "per_site_scaling", per_site_scaling)
        if reserved is not None:
            pulumi.set(__self__, "reserved", reserved)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if sku is not None:
            pulumi.set(__self__, "sku", sku)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if zone_redundant is not None:
            pulumi.set(__self__, "zone_redundant", zone_redundant)

    @property
    @pulumi.getter(name="appServiceEnvironmentId")
    def app_service_environment_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        """
        return pulumi.get(self, "app_service_environment_id")

    @app_service_environment_id.setter
    def app_service_environment_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "app_service_environment_id", value)

    @property
    @pulumi.getter(name="isXenon")
    def is_xenon(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "is_xenon")

    @is_xenon.setter
    def is_xenon(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "is_xenon", value)

    @property
    @pulumi.getter
    def kind(self) -> Optional[pulumi.Input[str]]:
        """
        The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "kind")

    @kind.setter
    def kind(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kind", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="maximumElasticWorkerCount")
    def maximum_elastic_worker_count(self) -> Optional[pulumi.Input[int]]:
        """
        The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        """
        return pulumi.get(self, "maximum_elastic_worker_count")

    @maximum_elastic_worker_count.setter
    def maximum_elastic_worker_count(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "maximum_elastic_worker_count", value)

    @property
    @pulumi.getter(name="maximumNumberOfWorkers")
    def maximum_number_of_workers(self) -> Optional[pulumi.Input[int]]:
        """
        The maximum number of workers supported with the App Service Plan's sku.
        """
        return pulumi.get(self, "maximum_number_of_workers")

    @maximum_number_of_workers.setter
    def maximum_number_of_workers(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "maximum_number_of_workers", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="perSiteScaling")
    def per_site_scaling(self) -> Optional[pulumi.Input[bool]]:
        """
        Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        """
        return pulumi.get(self, "per_site_scaling")

    @per_site_scaling.setter
    def per_site_scaling(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "per_site_scaling", value)

    @property
    @pulumi.getter
    def reserved(self) -> Optional[pulumi.Input[bool]]:
        """
        Is this App Service Plan `Reserved`. Defaults to `false`.
        """
        return pulumi.get(self, "reserved")

    @reserved.setter
    def reserved(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "reserved", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group in which to create the App Service Plan component.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def sku(self) -> Optional[pulumi.Input['PlanSkuArgs']]:
        """
        A `sku` block as documented below.
        """
        return pulumi.get(self, "sku")

    @sku.setter
    def sku(self, value: Optional[pulumi.Input['PlanSkuArgs']]):
        pulumi.set(self, "sku", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="zoneRedundant")
    def zone_redundant(self) -> Optional[pulumi.Input[bool]]:
        """
        Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        return pulumi.get(self, "zone_redundant")

    @zone_redundant.setter
    def zone_redundant(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "zone_redundant", value)


class Plan(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_service_environment_id: Optional[pulumi.Input[str]] = None,
                 is_xenon: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 maximum_elastic_worker_count: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 per_site_scaling: Optional[pulumi.Input[bool]] = None,
                 reserved: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku: Optional[pulumi.Input[pulumi.InputType['PlanSkuArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_redundant: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        ## Example Usage
        ### Dedicated)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            sku=azure.appservice.PlanSkuArgs(
                tier="Standard",
                size="S1",
            ))
        ```
        ### Shared / Consumption Plan)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            kind="FunctionApp",
            sku=azure.appservice.PlanSkuArgs(
                tier="Dynamic",
                size="Y1",
            ))
        ```
        ### Linux)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            kind="Linux",
            reserved=True,
            sku=azure.appservice.PlanSkuArgs(
                tier="Standard",
                size="S1",
            ))
        ```
        ### Windows Container)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            kind="xenon",
            is_xenon=True,
            sku=azure.appservice.PlanSkuArgs(
                tier="PremiumContainer",
                size="PC2",
            ))
        ```

        ## Import

        App Service Plan instances can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appservice/plan:Plan instance1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Web/serverfarms/instance1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] app_service_environment_id: The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        :param pulumi.Input[str] kind: The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_elastic_worker_count: The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        :param pulumi.Input[str] name: Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] per_site_scaling: Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        :param pulumi.Input[bool] reserved: Is this App Service Plan `Reserved`. Defaults to `false`.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the App Service Plan component.
        :param pulumi.Input[pulumi.InputType['PlanSkuArgs']] sku: A `sku` block as documented below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_redundant: Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: PlanArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Example Usage
        ### Dedicated)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            sku=azure.appservice.PlanSkuArgs(
                tier="Standard",
                size="S1",
            ))
        ```
        ### Shared / Consumption Plan)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            kind="FunctionApp",
            sku=azure.appservice.PlanSkuArgs(
                tier="Dynamic",
                size="Y1",
            ))
        ```
        ### Linux)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            kind="Linux",
            reserved=True,
            sku=azure.appservice.PlanSkuArgs(
                tier="Standard",
                size="S1",
            ))
        ```
        ### Windows Container)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_plan = azure.appservice.Plan("examplePlan",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            kind="xenon",
            is_xenon=True,
            sku=azure.appservice.PlanSkuArgs(
                tier="PremiumContainer",
                size="PC2",
            ))
        ```

        ## Import

        App Service Plan instances can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appservice/plan:Plan instance1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Web/serverfarms/instance1
        ```

        :param str resource_name: The name of the resource.
        :param PlanArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(PlanArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_service_environment_id: Optional[pulumi.Input[str]] = None,
                 is_xenon: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 maximum_elastic_worker_count: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 per_site_scaling: Optional[pulumi.Input[bool]] = None,
                 reserved: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku: Optional[pulumi.Input[pulumi.InputType['PlanSkuArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_redundant: Optional[pulumi.Input[bool]] = None,
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
            __props__ = PlanArgs.__new__(PlanArgs)

            __props__.__dict__["app_service_environment_id"] = app_service_environment_id
            __props__.__dict__["is_xenon"] = is_xenon
            __props__.__dict__["kind"] = kind
            __props__.__dict__["location"] = location
            __props__.__dict__["maximum_elastic_worker_count"] = maximum_elastic_worker_count
            __props__.__dict__["name"] = name
            __props__.__dict__["per_site_scaling"] = per_site_scaling
            __props__.__dict__["reserved"] = reserved
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            if sku is None and not opts.urn:
                raise TypeError("Missing required property 'sku'")
            __props__.__dict__["sku"] = sku
            __props__.__dict__["tags"] = tags
            __props__.__dict__["zone_redundant"] = zone_redundant
            __props__.__dict__["maximum_number_of_workers"] = None
        super(Plan, __self__).__init__(
            'azure:appservice/plan:Plan',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            app_service_environment_id: Optional[pulumi.Input[str]] = None,
            is_xenon: Optional[pulumi.Input[bool]] = None,
            kind: Optional[pulumi.Input[str]] = None,
            location: Optional[pulumi.Input[str]] = None,
            maximum_elastic_worker_count: Optional[pulumi.Input[int]] = None,
            maximum_number_of_workers: Optional[pulumi.Input[int]] = None,
            name: Optional[pulumi.Input[str]] = None,
            per_site_scaling: Optional[pulumi.Input[bool]] = None,
            reserved: Optional[pulumi.Input[bool]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            sku: Optional[pulumi.Input[pulumi.InputType['PlanSkuArgs']]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            zone_redundant: Optional[pulumi.Input[bool]] = None) -> 'Plan':
        """
        Get an existing Plan resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] app_service_environment_id: The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        :param pulumi.Input[str] kind: The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_elastic_worker_count: The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        :param pulumi.Input[int] maximum_number_of_workers: The maximum number of workers supported with the App Service Plan's sku.
        :param pulumi.Input[str] name: Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] per_site_scaling: Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        :param pulumi.Input[bool] reserved: Is this App Service Plan `Reserved`. Defaults to `false`.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the App Service Plan component.
        :param pulumi.Input[pulumi.InputType['PlanSkuArgs']] sku: A `sku` block as documented below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_redundant: Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _PlanState.__new__(_PlanState)

        __props__.__dict__["app_service_environment_id"] = app_service_environment_id
        __props__.__dict__["is_xenon"] = is_xenon
        __props__.__dict__["kind"] = kind
        __props__.__dict__["location"] = location
        __props__.__dict__["maximum_elastic_worker_count"] = maximum_elastic_worker_count
        __props__.__dict__["maximum_number_of_workers"] = maximum_number_of_workers
        __props__.__dict__["name"] = name
        __props__.__dict__["per_site_scaling"] = per_site_scaling
        __props__.__dict__["reserved"] = reserved
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["sku"] = sku
        __props__.__dict__["tags"] = tags
        __props__.__dict__["zone_redundant"] = zone_redundant
        return Plan(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="appServiceEnvironmentId")
    def app_service_environment_id(self) -> pulumi.Output[Optional[str]]:
        """
        The ID of the App Service Environment where the App Service Plan should be located. Changing forces a new resource to be created.
        """
        return pulumi.get(self, "app_service_environment_id")

    @property
    @pulumi.getter(name="isXenon")
    def is_xenon(self) -> pulumi.Output[Optional[bool]]:
        return pulumi.get(self, "is_xenon")

    @property
    @pulumi.getter
    def kind(self) -> pulumi.Output[Optional[str]]:
        """
        The kind of the App Service Plan to create. Possible values are `Windows` (also available as `App`), `Linux`, `elastic` (for Premium Consumption) and `FunctionApp` (for a Consumption Plan). Defaults to `Windows`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter(name="maximumElasticWorkerCount")
    def maximum_elastic_worker_count(self) -> pulumi.Output[int]:
        """
        The maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan.
        """
        return pulumi.get(self, "maximum_elastic_worker_count")

    @property
    @pulumi.getter(name="maximumNumberOfWorkers")
    def maximum_number_of_workers(self) -> pulumi.Output[int]:
        """
        The maximum number of workers supported with the App Service Plan's sku.
        """
        return pulumi.get(self, "maximum_number_of_workers")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the App Service Plan component. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="perSiteScaling")
    def per_site_scaling(self) -> pulumi.Output[Optional[bool]]:
        """
        Can Apps assigned to this App Service Plan be scaled independently? If set to `false` apps assigned to this plan will scale to all instances of the plan.  Defaults to `false`.
        """
        return pulumi.get(self, "per_site_scaling")

    @property
    @pulumi.getter
    def reserved(self) -> pulumi.Output[Optional[bool]]:
        """
        Is this App Service Plan `Reserved`. Defaults to `false`.
        """
        return pulumi.get(self, "reserved")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group in which to create the App Service Plan component.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter
    def sku(self) -> pulumi.Output['outputs.PlanSku']:
        """
        A `sku` block as documented below.
        """
        return pulumi.get(self, "sku")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="zoneRedundant")
    def zone_redundant(self) -> pulumi.Output[Optional[bool]]:
        """
        Specifies if the App Service Plan should be Zone Redundant. Changing this forces a new resource to be created. Defaults to `false`.
        """
        return pulumi.get(self, "zone_redundant")

