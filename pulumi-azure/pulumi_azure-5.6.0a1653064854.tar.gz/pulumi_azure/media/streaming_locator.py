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

__all__ = ['StreamingLocatorArgs', 'StreamingLocator']

@pulumi.input_type
class StreamingLocatorArgs:
    def __init__(__self__, *,
                 asset_name: pulumi.Input[str],
                 media_services_account_name: pulumi.Input[str],
                 resource_group_name: pulumi.Input[str],
                 streaming_policy_name: pulumi.Input[str],
                 alternative_media_id: Optional[pulumi.Input[str]] = None,
                 content_keys: Optional[pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]]] = None,
                 default_content_key_policy_name: Optional[pulumi.Input[str]] = None,
                 end_time: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 start_time: Optional[pulumi.Input[str]] = None,
                 streaming_locator_id: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a StreamingLocator resource.
        :param pulumi.Input[str] asset_name: Asset Name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] media_services_account_name: The Media Services account name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_policy_name: Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] alternative_media_id: Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]] content_keys: One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] default_content_key_policy_name: Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] end_time: The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] name: The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] start_time: The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_locator_id: The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        pulumi.set(__self__, "asset_name", asset_name)
        pulumi.set(__self__, "media_services_account_name", media_services_account_name)
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "streaming_policy_name", streaming_policy_name)
        if alternative_media_id is not None:
            pulumi.set(__self__, "alternative_media_id", alternative_media_id)
        if content_keys is not None:
            pulumi.set(__self__, "content_keys", content_keys)
        if default_content_key_policy_name is not None:
            pulumi.set(__self__, "default_content_key_policy_name", default_content_key_policy_name)
        if end_time is not None:
            pulumi.set(__self__, "end_time", end_time)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if start_time is not None:
            pulumi.set(__self__, "start_time", start_time)
        if streaming_locator_id is not None:
            pulumi.set(__self__, "streaming_locator_id", streaming_locator_id)

    @property
    @pulumi.getter(name="assetName")
    def asset_name(self) -> pulumi.Input[str]:
        """
        Asset Name. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "asset_name")

    @asset_name.setter
    def asset_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "asset_name", value)

    @property
    @pulumi.getter(name="mediaServicesAccountName")
    def media_services_account_name(self) -> pulumi.Input[str]:
        """
        The Media Services account name. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "media_services_account_name")

    @media_services_account_name.setter
    def media_services_account_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "media_services_account_name", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="streamingPolicyName")
    def streaming_policy_name(self) -> pulumi.Input[str]:
        """
        Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "streaming_policy_name")

    @streaming_policy_name.setter
    def streaming_policy_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "streaming_policy_name", value)

    @property
    @pulumi.getter(name="alternativeMediaId")
    def alternative_media_id(self) -> Optional[pulumi.Input[str]]:
        """
        Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "alternative_media_id")

    @alternative_media_id.setter
    def alternative_media_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "alternative_media_id", value)

    @property
    @pulumi.getter(name="contentKeys")
    def content_keys(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]]]:
        """
        One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "content_keys")

    @content_keys.setter
    def content_keys(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]]]):
        pulumi.set(self, "content_keys", value)

    @property
    @pulumi.getter(name="defaultContentKeyPolicyName")
    def default_content_key_policy_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "default_content_key_policy_name")

    @default_content_key_policy_name.setter
    def default_content_key_policy_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "default_content_key_policy_name", value)

    @property
    @pulumi.getter(name="endTime")
    def end_time(self) -> Optional[pulumi.Input[str]]:
        """
        The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "end_time")

    @end_time.setter
    def end_time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "end_time", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="startTime")
    def start_time(self) -> Optional[pulumi.Input[str]]:
        """
        The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "start_time")

    @start_time.setter
    def start_time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "start_time", value)

    @property
    @pulumi.getter(name="streamingLocatorId")
    def streaming_locator_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "streaming_locator_id")

    @streaming_locator_id.setter
    def streaming_locator_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "streaming_locator_id", value)


@pulumi.input_type
class _StreamingLocatorState:
    def __init__(__self__, *,
                 alternative_media_id: Optional[pulumi.Input[str]] = None,
                 asset_name: Optional[pulumi.Input[str]] = None,
                 content_keys: Optional[pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]]] = None,
                 default_content_key_policy_name: Optional[pulumi.Input[str]] = None,
                 end_time: Optional[pulumi.Input[str]] = None,
                 media_services_account_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 start_time: Optional[pulumi.Input[str]] = None,
                 streaming_locator_id: Optional[pulumi.Input[str]] = None,
                 streaming_policy_name: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering StreamingLocator resources.
        :param pulumi.Input[str] alternative_media_id: Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] asset_name: Asset Name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]] content_keys: One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] default_content_key_policy_name: Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] end_time: The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] media_services_account_name: The Media Services account name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] name: The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] start_time: The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_locator_id: The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_policy_name: Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        """
        if alternative_media_id is not None:
            pulumi.set(__self__, "alternative_media_id", alternative_media_id)
        if asset_name is not None:
            pulumi.set(__self__, "asset_name", asset_name)
        if content_keys is not None:
            pulumi.set(__self__, "content_keys", content_keys)
        if default_content_key_policy_name is not None:
            pulumi.set(__self__, "default_content_key_policy_name", default_content_key_policy_name)
        if end_time is not None:
            pulumi.set(__self__, "end_time", end_time)
        if media_services_account_name is not None:
            pulumi.set(__self__, "media_services_account_name", media_services_account_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if start_time is not None:
            pulumi.set(__self__, "start_time", start_time)
        if streaming_locator_id is not None:
            pulumi.set(__self__, "streaming_locator_id", streaming_locator_id)
        if streaming_policy_name is not None:
            pulumi.set(__self__, "streaming_policy_name", streaming_policy_name)

    @property
    @pulumi.getter(name="alternativeMediaId")
    def alternative_media_id(self) -> Optional[pulumi.Input[str]]:
        """
        Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "alternative_media_id")

    @alternative_media_id.setter
    def alternative_media_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "alternative_media_id", value)

    @property
    @pulumi.getter(name="assetName")
    def asset_name(self) -> Optional[pulumi.Input[str]]:
        """
        Asset Name. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "asset_name")

    @asset_name.setter
    def asset_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "asset_name", value)

    @property
    @pulumi.getter(name="contentKeys")
    def content_keys(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]]]:
        """
        One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "content_keys")

    @content_keys.setter
    def content_keys(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['StreamingLocatorContentKeyArgs']]]]):
        pulumi.set(self, "content_keys", value)

    @property
    @pulumi.getter(name="defaultContentKeyPolicyName")
    def default_content_key_policy_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "default_content_key_policy_name")

    @default_content_key_policy_name.setter
    def default_content_key_policy_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "default_content_key_policy_name", value)

    @property
    @pulumi.getter(name="endTime")
    def end_time(self) -> Optional[pulumi.Input[str]]:
        """
        The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "end_time")

    @end_time.setter
    def end_time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "end_time", value)

    @property
    @pulumi.getter(name="mediaServicesAccountName")
    def media_services_account_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Media Services account name. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "media_services_account_name")

    @media_services_account_name.setter
    def media_services_account_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "media_services_account_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="startTime")
    def start_time(self) -> Optional[pulumi.Input[str]]:
        """
        The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "start_time")

    @start_time.setter
    def start_time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "start_time", value)

    @property
    @pulumi.getter(name="streamingLocatorId")
    def streaming_locator_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "streaming_locator_id")

    @streaming_locator_id.setter
    def streaming_locator_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "streaming_locator_id", value)

    @property
    @pulumi.getter(name="streamingPolicyName")
    def streaming_policy_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "streaming_policy_name")

    @streaming_policy_name.setter
    def streaming_policy_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "streaming_policy_name", value)


class StreamingLocator(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 alternative_media_id: Optional[pulumi.Input[str]] = None,
                 asset_name: Optional[pulumi.Input[str]] = None,
                 content_keys: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['StreamingLocatorContentKeyArgs']]]]] = None,
                 default_content_key_policy_name: Optional[pulumi.Input[str]] = None,
                 end_time: Optional[pulumi.Input[str]] = None,
                 media_services_account_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 start_time: Optional[pulumi.Input[str]] = None,
                 streaming_locator_id: Optional[pulumi.Input[str]] = None,
                 streaming_policy_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Media Streaming Locator.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_tier="Standard",
            account_replication_type="GRS")
        example_service_account = azure.media.ServiceAccount("exampleServiceAccount",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            storage_accounts=[azure.media.ServiceAccountStorageAccountArgs(
                id=example_account.id,
                is_primary=True,
            )])
        example_asset = azure.media.Asset("exampleAsset",
            resource_group_name=example_resource_group.name,
            media_services_account_name=example_service_account.name,
            description="Asset description")
        example_streaming_locator = azure.media.StreamingLocator("exampleStreamingLocator",
            resource_group_name=example_resource_group.name,
            media_services_account_name=example_service_account.name,
            asset_name=example_asset.name,
            streaming_policy_name="Predefined_ClearStreamingOnly")
        ```

        ## Import

        Streaming Locators can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:media/streamingLocator:StreamingLocator example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/Microsoft.Media/mediaservices/account1/streaminglocators/locator1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] alternative_media_id: Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] asset_name: Asset Name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['StreamingLocatorContentKeyArgs']]]] content_keys: One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] default_content_key_policy_name: Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] end_time: The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] media_services_account_name: The Media Services account name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] name: The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] start_time: The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_locator_id: The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_policy_name: Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: StreamingLocatorArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Media Streaming Locator.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_tier="Standard",
            account_replication_type="GRS")
        example_service_account = azure.media.ServiceAccount("exampleServiceAccount",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            storage_accounts=[azure.media.ServiceAccountStorageAccountArgs(
                id=example_account.id,
                is_primary=True,
            )])
        example_asset = azure.media.Asset("exampleAsset",
            resource_group_name=example_resource_group.name,
            media_services_account_name=example_service_account.name,
            description="Asset description")
        example_streaming_locator = azure.media.StreamingLocator("exampleStreamingLocator",
            resource_group_name=example_resource_group.name,
            media_services_account_name=example_service_account.name,
            asset_name=example_asset.name,
            streaming_policy_name="Predefined_ClearStreamingOnly")
        ```

        ## Import

        Streaming Locators can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:media/streamingLocator:StreamingLocator example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/Microsoft.Media/mediaservices/account1/streaminglocators/locator1
        ```

        :param str resource_name: The name of the resource.
        :param StreamingLocatorArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(StreamingLocatorArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 alternative_media_id: Optional[pulumi.Input[str]] = None,
                 asset_name: Optional[pulumi.Input[str]] = None,
                 content_keys: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['StreamingLocatorContentKeyArgs']]]]] = None,
                 default_content_key_policy_name: Optional[pulumi.Input[str]] = None,
                 end_time: Optional[pulumi.Input[str]] = None,
                 media_services_account_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 start_time: Optional[pulumi.Input[str]] = None,
                 streaming_locator_id: Optional[pulumi.Input[str]] = None,
                 streaming_policy_name: Optional[pulumi.Input[str]] = None,
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
            __props__ = StreamingLocatorArgs.__new__(StreamingLocatorArgs)

            __props__.__dict__["alternative_media_id"] = alternative_media_id
            if asset_name is None and not opts.urn:
                raise TypeError("Missing required property 'asset_name'")
            __props__.__dict__["asset_name"] = asset_name
            __props__.__dict__["content_keys"] = content_keys
            __props__.__dict__["default_content_key_policy_name"] = default_content_key_policy_name
            __props__.__dict__["end_time"] = end_time
            if media_services_account_name is None and not opts.urn:
                raise TypeError("Missing required property 'media_services_account_name'")
            __props__.__dict__["media_services_account_name"] = media_services_account_name
            __props__.__dict__["name"] = name
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            __props__.__dict__["start_time"] = start_time
            __props__.__dict__["streaming_locator_id"] = streaming_locator_id
            if streaming_policy_name is None and not opts.urn:
                raise TypeError("Missing required property 'streaming_policy_name'")
            __props__.__dict__["streaming_policy_name"] = streaming_policy_name
        super(StreamingLocator, __self__).__init__(
            'azure:media/streamingLocator:StreamingLocator',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            alternative_media_id: Optional[pulumi.Input[str]] = None,
            asset_name: Optional[pulumi.Input[str]] = None,
            content_keys: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['StreamingLocatorContentKeyArgs']]]]] = None,
            default_content_key_policy_name: Optional[pulumi.Input[str]] = None,
            end_time: Optional[pulumi.Input[str]] = None,
            media_services_account_name: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            start_time: Optional[pulumi.Input[str]] = None,
            streaming_locator_id: Optional[pulumi.Input[str]] = None,
            streaming_policy_name: Optional[pulumi.Input[str]] = None) -> 'StreamingLocator':
        """
        Get an existing StreamingLocator resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] alternative_media_id: Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] asset_name: Asset Name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['StreamingLocatorContentKeyArgs']]]] content_keys: One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] default_content_key_policy_name: Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] end_time: The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] media_services_account_name: The Media Services account name. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] name: The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] start_time: The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_locator_id: The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        :param pulumi.Input[str] streaming_policy_name: Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _StreamingLocatorState.__new__(_StreamingLocatorState)

        __props__.__dict__["alternative_media_id"] = alternative_media_id
        __props__.__dict__["asset_name"] = asset_name
        __props__.__dict__["content_keys"] = content_keys
        __props__.__dict__["default_content_key_policy_name"] = default_content_key_policy_name
        __props__.__dict__["end_time"] = end_time
        __props__.__dict__["media_services_account_name"] = media_services_account_name
        __props__.__dict__["name"] = name
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["start_time"] = start_time
        __props__.__dict__["streaming_locator_id"] = streaming_locator_id
        __props__.__dict__["streaming_policy_name"] = streaming_policy_name
        return StreamingLocator(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="alternativeMediaId")
    def alternative_media_id(self) -> pulumi.Output[Optional[str]]:
        """
        Alternative Media ID of this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "alternative_media_id")

    @property
    @pulumi.getter(name="assetName")
    def asset_name(self) -> pulumi.Output[str]:
        """
        Asset Name. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "asset_name")

    @property
    @pulumi.getter(name="contentKeys")
    def content_keys(self) -> pulumi.Output[Optional[Sequence['outputs.StreamingLocatorContentKey']]]:
        """
        One or more `content_key` blocks as defined below. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "content_keys")

    @property
    @pulumi.getter(name="defaultContentKeyPolicyName")
    def default_content_key_policy_name(self) -> pulumi.Output[Optional[str]]:
        """
        Name of the default Content Key Policy used by this Streaming Locator.Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "default_content_key_policy_name")

    @property
    @pulumi.getter(name="endTime")
    def end_time(self) -> pulumi.Output[str]:
        """
        The end time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "end_time")

    @property
    @pulumi.getter(name="mediaServicesAccountName")
    def media_services_account_name(self) -> pulumi.Output[str]:
        """
        The Media Services account name. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "media_services_account_name")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name which should be used for this Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the Resource Group where the Streaming Locator should exist. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="startTime")
    def start_time(self) -> pulumi.Output[Optional[str]]:
        """
        The start time of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "start_time")

    @property
    @pulumi.getter(name="streamingLocatorId")
    def streaming_locator_id(self) -> pulumi.Output[str]:
        """
        The ID of the Streaming Locator. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "streaming_locator_id")

    @property
    @pulumi.getter(name="streamingPolicyName")
    def streaming_policy_name(self) -> pulumi.Output[str]:
        """
        Name of the Streaming Policy used by this Streaming Locator. Either specify the name of Streaming Policy you created or use one of the predefined Streaming Policies. The predefined Streaming Policies available are: `Predefined_DownloadOnly`, `Predefined_ClearStreamingOnly`, `Predefined_DownloadAndClearStreaming`, `Predefined_ClearKey`, `Predefined_MultiDrmCencStreaming` and `Predefined_MultiDrmStreaming`. Changing this forces a new Streaming Locator to be created.
        """
        return pulumi.get(self, "streaming_policy_name")

