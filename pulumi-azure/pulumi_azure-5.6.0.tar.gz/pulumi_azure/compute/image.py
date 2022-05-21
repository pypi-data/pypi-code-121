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

__all__ = ['ImageArgs', 'Image']

@pulumi.input_type
class ImageArgs:
    def __init__(__self__, *,
                 resource_group_name: pulumi.Input[str],
                 data_disks: Optional[pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]]] = None,
                 hyper_v_generation: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 os_disk: Optional[pulumi.Input['ImageOsDiskArgs']] = None,
                 source_virtual_machine_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_resilient: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a Image resource.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create
               the image. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]] data_disks: One or more `data_disk` elements as defined below.
        :param pulumi.Input[str] hyper_v_generation: The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        :param pulumi.Input[str] location: Specified the supported Azure location where the resource exists.
               Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the image. Changing this forces a
               new resource to be created.
        :param pulumi.Input['ImageOsDiskArgs'] os_disk: One or more `os_disk` elements as defined below.
        :param pulumi.Input[str] source_virtual_machine_id: The Virtual Machine ID from which to create the image.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_resilient: Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if data_disks is not None:
            pulumi.set(__self__, "data_disks", data_disks)
        if hyper_v_generation is not None:
            pulumi.set(__self__, "hyper_v_generation", hyper_v_generation)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if os_disk is not None:
            pulumi.set(__self__, "os_disk", os_disk)
        if source_virtual_machine_id is not None:
            pulumi.set(__self__, "source_virtual_machine_id", source_virtual_machine_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if zone_resilient is not None:
            pulumi.set(__self__, "zone_resilient", zone_resilient)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group in which to create
        the image. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="dataDisks")
    def data_disks(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]]]:
        """
        One or more `data_disk` elements as defined below.
        """
        return pulumi.get(self, "data_disks")

    @data_disks.setter
    def data_disks(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]]]):
        pulumi.set(self, "data_disks", value)

    @property
    @pulumi.getter(name="hyperVGeneration")
    def hyper_v_generation(self) -> Optional[pulumi.Input[str]]:
        """
        The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        """
        return pulumi.get(self, "hyper_v_generation")

    @hyper_v_generation.setter
    def hyper_v_generation(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "hyper_v_generation", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specified the supported Azure location where the resource exists.
        Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the image. Changing this forces a
        new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="osDisk")
    def os_disk(self) -> Optional[pulumi.Input['ImageOsDiskArgs']]:
        """
        One or more `os_disk` elements as defined below.
        """
        return pulumi.get(self, "os_disk")

    @os_disk.setter
    def os_disk(self, value: Optional[pulumi.Input['ImageOsDiskArgs']]):
        pulumi.set(self, "os_disk", value)

    @property
    @pulumi.getter(name="sourceVirtualMachineId")
    def source_virtual_machine_id(self) -> Optional[pulumi.Input[str]]:
        """
        The Virtual Machine ID from which to create the image.
        """
        return pulumi.get(self, "source_virtual_machine_id")

    @source_virtual_machine_id.setter
    def source_virtual_machine_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "source_virtual_machine_id", value)

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
    @pulumi.getter(name="zoneResilient")
    def zone_resilient(self) -> Optional[pulumi.Input[bool]]:
        """
        Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "zone_resilient")

    @zone_resilient.setter
    def zone_resilient(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "zone_resilient", value)


@pulumi.input_type
class _ImageState:
    def __init__(__self__, *,
                 data_disks: Optional[pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]]] = None,
                 hyper_v_generation: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 os_disk: Optional[pulumi.Input['ImageOsDiskArgs']] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 source_virtual_machine_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_resilient: Optional[pulumi.Input[bool]] = None):
        """
        Input properties used for looking up and filtering Image resources.
        :param pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]] data_disks: One or more `data_disk` elements as defined below.
        :param pulumi.Input[str] hyper_v_generation: The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        :param pulumi.Input[str] location: Specified the supported Azure location where the resource exists.
               Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the image. Changing this forces a
               new resource to be created.
        :param pulumi.Input['ImageOsDiskArgs'] os_disk: One or more `os_disk` elements as defined below.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create
               the image. Changing this forces a new resource to be created.
        :param pulumi.Input[str] source_virtual_machine_id: The Virtual Machine ID from which to create the image.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_resilient: Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        if data_disks is not None:
            pulumi.set(__self__, "data_disks", data_disks)
        if hyper_v_generation is not None:
            pulumi.set(__self__, "hyper_v_generation", hyper_v_generation)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if os_disk is not None:
            pulumi.set(__self__, "os_disk", os_disk)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if source_virtual_machine_id is not None:
            pulumi.set(__self__, "source_virtual_machine_id", source_virtual_machine_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if zone_resilient is not None:
            pulumi.set(__self__, "zone_resilient", zone_resilient)

    @property
    @pulumi.getter(name="dataDisks")
    def data_disks(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]]]:
        """
        One or more `data_disk` elements as defined below.
        """
        return pulumi.get(self, "data_disks")

    @data_disks.setter
    def data_disks(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ImageDataDiskArgs']]]]):
        pulumi.set(self, "data_disks", value)

    @property
    @pulumi.getter(name="hyperVGeneration")
    def hyper_v_generation(self) -> Optional[pulumi.Input[str]]:
        """
        The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        """
        return pulumi.get(self, "hyper_v_generation")

    @hyper_v_generation.setter
    def hyper_v_generation(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "hyper_v_generation", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specified the supported Azure location where the resource exists.
        Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the image. Changing this forces a
        new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="osDisk")
    def os_disk(self) -> Optional[pulumi.Input['ImageOsDiskArgs']]:
        """
        One or more `os_disk` elements as defined below.
        """
        return pulumi.get(self, "os_disk")

    @os_disk.setter
    def os_disk(self, value: Optional[pulumi.Input['ImageOsDiskArgs']]):
        pulumi.set(self, "os_disk", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group in which to create
        the image. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="sourceVirtualMachineId")
    def source_virtual_machine_id(self) -> Optional[pulumi.Input[str]]:
        """
        The Virtual Machine ID from which to create the image.
        """
        return pulumi.get(self, "source_virtual_machine_id")

    @source_virtual_machine_id.setter
    def source_virtual_machine_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "source_virtual_machine_id", value)

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
    @pulumi.getter(name="zoneResilient")
    def zone_resilient(self) -> Optional[pulumi.Input[bool]]:
        """
        Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "zone_resilient")

    @zone_resilient.setter
    def zone_resilient(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "zone_resilient", value)


class Image(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 data_disks: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ImageDataDiskArgs']]]]] = None,
                 hyper_v_generation: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 os_disk: Optional[pulumi.Input[pulumi.InputType['ImageOsDiskArgs']]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 source_virtual_machine_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_resilient: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        Manages a custom virtual machine image that can be used to create virtual machines.

        ## Example Usage
        ### Creating From VHD

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_image = azure.compute.Image("exampleImage",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            os_disk=azure.compute.ImageOsDiskArgs(
                os_type="Linux",
                os_state="Generalized",
                blob_uri="{blob_uri}",
                size_gb=30,
            ))
        ```
        ### Creating From Virtual Machine (VM Must Be Generalized Beforehand)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_image = azure.compute.Image("exampleImage",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            source_virtual_machine_id="{vm_id}")
        ```

        ## Import

        Images can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:compute/image:Image example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/microsoft.compute/images/image1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ImageDataDiskArgs']]]] data_disks: One or more `data_disk` elements as defined below.
        :param pulumi.Input[str] hyper_v_generation: The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        :param pulumi.Input[str] location: Specified the supported Azure location where the resource exists.
               Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the image. Changing this forces a
               new resource to be created.
        :param pulumi.Input[pulumi.InputType['ImageOsDiskArgs']] os_disk: One or more `os_disk` elements as defined below.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create
               the image. Changing this forces a new resource to be created.
        :param pulumi.Input[str] source_virtual_machine_id: The Virtual Machine ID from which to create the image.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_resilient: Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ImageArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a custom virtual machine image that can be used to create virtual machines.

        ## Example Usage
        ### Creating From VHD

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_image = azure.compute.Image("exampleImage",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            os_disk=azure.compute.ImageOsDiskArgs(
                os_type="Linux",
                os_state="Generalized",
                blob_uri="{blob_uri}",
                size_gb=30,
            ))
        ```
        ### Creating From Virtual Machine (VM Must Be Generalized Beforehand)

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_image = azure.compute.Image("exampleImage",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name,
            source_virtual_machine_id="{vm_id}")
        ```

        ## Import

        Images can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:compute/image:Image example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/microsoft.compute/images/image1
        ```

        :param str resource_name: The name of the resource.
        :param ImageArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ImageArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 data_disks: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ImageDataDiskArgs']]]]] = None,
                 hyper_v_generation: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 os_disk: Optional[pulumi.Input[pulumi.InputType['ImageOsDiskArgs']]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 source_virtual_machine_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 zone_resilient: Optional[pulumi.Input[bool]] = None,
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
            __props__ = ImageArgs.__new__(ImageArgs)

            __props__.__dict__["data_disks"] = data_disks
            __props__.__dict__["hyper_v_generation"] = hyper_v_generation
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            __props__.__dict__["os_disk"] = os_disk
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            __props__.__dict__["source_virtual_machine_id"] = source_virtual_machine_id
            __props__.__dict__["tags"] = tags
            __props__.__dict__["zone_resilient"] = zone_resilient
        super(Image, __self__).__init__(
            'azure:compute/image:Image',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            data_disks: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ImageDataDiskArgs']]]]] = None,
            hyper_v_generation: Optional[pulumi.Input[str]] = None,
            location: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            os_disk: Optional[pulumi.Input[pulumi.InputType['ImageOsDiskArgs']]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            source_virtual_machine_id: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            zone_resilient: Optional[pulumi.Input[bool]] = None) -> 'Image':
        """
        Get an existing Image resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ImageDataDiskArgs']]]] data_disks: One or more `data_disk` elements as defined below.
        :param pulumi.Input[str] hyper_v_generation: The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        :param pulumi.Input[str] location: Specified the supported Azure location where the resource exists.
               Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the image. Changing this forces a
               new resource to be created.
        :param pulumi.Input[pulumi.InputType['ImageOsDiskArgs']] os_disk: One or more `os_disk` elements as defined below.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create
               the image. Changing this forces a new resource to be created.
        :param pulumi.Input[str] source_virtual_machine_id: The Virtual Machine ID from which to create the image.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[bool] zone_resilient: Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ImageState.__new__(_ImageState)

        __props__.__dict__["data_disks"] = data_disks
        __props__.__dict__["hyper_v_generation"] = hyper_v_generation
        __props__.__dict__["location"] = location
        __props__.__dict__["name"] = name
        __props__.__dict__["os_disk"] = os_disk
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["source_virtual_machine_id"] = source_virtual_machine_id
        __props__.__dict__["tags"] = tags
        __props__.__dict__["zone_resilient"] = zone_resilient
        return Image(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="dataDisks")
    def data_disks(self) -> pulumi.Output[Optional[Sequence['outputs.ImageDataDisk']]]:
        """
        One or more `data_disk` elements as defined below.
        """
        return pulumi.get(self, "data_disks")

    @property
    @pulumi.getter(name="hyperVGeneration")
    def hyper_v_generation(self) -> pulumi.Output[Optional[str]]:
        """
        The HyperVGenerationType of the VirtualMachine created from the image as `V1`, `V2`. The default is `V1`.
        """
        return pulumi.get(self, "hyper_v_generation")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        Specified the supported Azure location where the resource exists.
        Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the image. Changing this forces a
        new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="osDisk")
    def os_disk(self) -> pulumi.Output[Optional['outputs.ImageOsDisk']]:
        """
        One or more `os_disk` elements as defined below.
        """
        return pulumi.get(self, "os_disk")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group in which to create
        the image. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="sourceVirtualMachineId")
    def source_virtual_machine_id(self) -> pulumi.Output[Optional[str]]:
        """
        The Virtual Machine ID from which to create the image.
        """
        return pulumi.get(self, "source_virtual_machine_id")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="zoneResilient")
    def zone_resilient(self) -> pulumi.Output[Optional[bool]]:
        """
        Is zone resiliency enabled?  Defaults to `false`.  Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "zone_resilient")

