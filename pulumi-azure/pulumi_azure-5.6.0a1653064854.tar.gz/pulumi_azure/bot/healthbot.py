# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['HealthbotArgs', 'Healthbot']

@pulumi.input_type
class HealthbotArgs:
    def __init__(__self__, *,
                 resource_group_name: pulumi.Input[str],
                 sku_name: pulumi.Input[str],
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a Healthbot resource.
        :param pulumi.Input[str] resource_group_name: Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
               forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        :param pulumi.Input[str] location: Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        :param pulumi.Input[str] name: Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the service.
        """
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "sku_name", sku_name)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
        forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="skuName")
    def sku_name(self) -> pulumi.Input[str]:
        """
        The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        """
        return pulumi.get(self, "sku_name")

    @sku_name.setter
    def sku_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "sku_name", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the service.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _HealthbotState:
    def __init__(__self__, *,
                 bot_management_portal_url: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering Healthbot resources.
        :param pulumi.Input[str] bot_management_portal_url: The management portal url.
        :param pulumi.Input[str] location: Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        :param pulumi.Input[str] name: Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
               forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the service.
        """
        if bot_management_portal_url is not None:
            pulumi.set(__self__, "bot_management_portal_url", bot_management_portal_url)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if sku_name is not None:
            pulumi.set(__self__, "sku_name", sku_name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="botManagementPortalUrl")
    def bot_management_portal_url(self) -> Optional[pulumi.Input[str]]:
        """
        The management portal url.
        """
        return pulumi.get(self, "bot_management_portal_url")

    @bot_management_portal_url.setter
    def bot_management_portal_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "bot_management_portal_url", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
        forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="skuName")
    def sku_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        """
        return pulumi.get(self, "sku_name")

    @sku_name.setter
    def sku_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "sku_name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the service.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


class Healthbot(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Manages a Healthbot Service.

        ## Import

        Healthbot Service can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:bot/healthbot:Healthbot example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/Microsoft.HealthBot/healthBots/bot1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] location: Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        :param pulumi.Input[str] name: Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
               forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the service.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: HealthbotArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Healthbot Service.

        ## Import

        Healthbot Service can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:bot/healthbot:Healthbot example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/Microsoft.HealthBot/healthBots/bot1
        ```

        :param str resource_name: The name of the resource.
        :param HealthbotArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(HealthbotArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku_name: Optional[pulumi.Input[str]] = None,
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
            __props__ = HealthbotArgs.__new__(HealthbotArgs)

            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            if sku_name is None and not opts.urn:
                raise TypeError("Missing required property 'sku_name'")
            __props__.__dict__["sku_name"] = sku_name
            __props__.__dict__["tags"] = tags
            __props__.__dict__["bot_management_portal_url"] = None
        super(Healthbot, __self__).__init__(
            'azure:bot/healthbot:Healthbot',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            bot_management_portal_url: Optional[pulumi.Input[str]] = None,
            location: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            sku_name: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'Healthbot':
        """
        Get an existing Healthbot resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bot_management_portal_url: The management portal url.
        :param pulumi.Input[str] location: Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        :param pulumi.Input[str] name: Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
               forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the service.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _HealthbotState.__new__(_HealthbotState)

        __props__.__dict__["bot_management_portal_url"] = bot_management_portal_url
        __props__.__dict__["location"] = location
        __props__.__dict__["name"] = name
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["sku_name"] = sku_name
        __props__.__dict__["tags"] = tags
        return Healthbot(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="botManagementPortalUrl")
    def bot_management_portal_url(self) -> pulumi.Output[str]:
        """
        The management portal url.
        """
        return pulumi.get(self, "bot_management_portal_url")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        Specifies The Azure Region where the resource exists. CHanging this force a new resource to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies The name of the Healthbot Service resource. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        Specifies The name of the Resource Group in which to create the Healthbot Service. changing this
        forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="skuName")
    def sku_name(self) -> pulumi.Output[str]:
        """
        The name which should be used for the SKU of the service. Possible values are "F0" and "S1".
        """
        return pulumi.get(self, "sku_name")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags which should be assigned to the service.
        """
        return pulumi.get(self, "tags")

