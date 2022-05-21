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

__all__ = ['DatasetAzureBlobArgs', 'DatasetAzureBlob']

@pulumi.input_type
class DatasetAzureBlobArgs:
    def __init__(__self__, *,
                 data_factory_id: pulumi.Input[str],
                 linked_service_name: pulumi.Input[str],
                 additional_properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 annotations: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 dynamic_filename_enabled: Optional[pulumi.Input[bool]] = None,
                 dynamic_path_enabled: Optional[pulumi.Input[bool]] = None,
                 filename: Optional[pulumi.Input[str]] = None,
                 folder: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 schema_columns: Optional[pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]]] = None):
        """
        The set of arguments for constructing a DatasetAzureBlob resource.
        :param pulumi.Input[str] data_factory_id: The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        :param pulumi.Input[str] linked_service_name: The Data Factory Linked Service name in which to associate the Dataset with.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] additional_properties: A map of additional properties to associate with the Data Factory Dataset.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] annotations: List of tags that can be used for describing the Data Factory Dataset.
        :param pulumi.Input[str] description: The description for the Data Factory Dataset.
        :param pulumi.Input[bool] dynamic_filename_enabled: Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[bool] dynamic_path_enabled: Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[str] filename: The filename of the Azure Blob.
        :param pulumi.Input[str] folder: The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        :param pulumi.Input[str] name: Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of parameters to associate with the Data Factory Dataset.
        :param pulumi.Input[str] path: The path of the Azure Blob.
        :param pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]] schema_columns: A `schema_column` block as defined below.
        """
        pulumi.set(__self__, "data_factory_id", data_factory_id)
        pulumi.set(__self__, "linked_service_name", linked_service_name)
        if additional_properties is not None:
            pulumi.set(__self__, "additional_properties", additional_properties)
        if annotations is not None:
            pulumi.set(__self__, "annotations", annotations)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if dynamic_filename_enabled is not None:
            pulumi.set(__self__, "dynamic_filename_enabled", dynamic_filename_enabled)
        if dynamic_path_enabled is not None:
            pulumi.set(__self__, "dynamic_path_enabled", dynamic_path_enabled)
        if filename is not None:
            pulumi.set(__self__, "filename", filename)
        if folder is not None:
            pulumi.set(__self__, "folder", folder)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parameters is not None:
            pulumi.set(__self__, "parameters", parameters)
        if path is not None:
            pulumi.set(__self__, "path", path)
        if schema_columns is not None:
            pulumi.set(__self__, "schema_columns", schema_columns)

    @property
    @pulumi.getter(name="dataFactoryId")
    def data_factory_id(self) -> pulumi.Input[str]:
        """
        The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        """
        return pulumi.get(self, "data_factory_id")

    @data_factory_id.setter
    def data_factory_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "data_factory_id", value)

    @property
    @pulumi.getter(name="linkedServiceName")
    def linked_service_name(self) -> pulumi.Input[str]:
        """
        The Data Factory Linked Service name in which to associate the Dataset with.
        """
        return pulumi.get(self, "linked_service_name")

    @linked_service_name.setter
    def linked_service_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "linked_service_name", value)

    @property
    @pulumi.getter(name="additionalProperties")
    def additional_properties(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of additional properties to associate with the Data Factory Dataset.
        """
        return pulumi.get(self, "additional_properties")

    @additional_properties.setter
    def additional_properties(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "additional_properties", value)

    @property
    @pulumi.getter
    def annotations(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of tags that can be used for describing the Data Factory Dataset.
        """
        return pulumi.get(self, "annotations")

    @annotations.setter
    def annotations(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "annotations", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description for the Data Factory Dataset.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="dynamicFilenameEnabled")
    def dynamic_filename_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        """
        return pulumi.get(self, "dynamic_filename_enabled")

    @dynamic_filename_enabled.setter
    def dynamic_filename_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "dynamic_filename_enabled", value)

    @property
    @pulumi.getter(name="dynamicPathEnabled")
    def dynamic_path_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        """
        return pulumi.get(self, "dynamic_path_enabled")

    @dynamic_path_enabled.setter
    def dynamic_path_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "dynamic_path_enabled", value)

    @property
    @pulumi.getter
    def filename(self) -> Optional[pulumi.Input[str]]:
        """
        The filename of the Azure Blob.
        """
        return pulumi.get(self, "filename")

    @filename.setter
    def filename(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "filename", value)

    @property
    @pulumi.getter
    def folder(self) -> Optional[pulumi.Input[str]]:
        """
        The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        """
        return pulumi.get(self, "folder")

    @folder.setter
    def folder(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "folder", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def parameters(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of parameters to associate with the Data Factory Dataset.
        """
        return pulumi.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameters", value)

    @property
    @pulumi.getter
    def path(self) -> Optional[pulumi.Input[str]]:
        """
        The path of the Azure Blob.
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "path", value)

    @property
    @pulumi.getter(name="schemaColumns")
    def schema_columns(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]]]:
        """
        A `schema_column` block as defined below.
        """
        return pulumi.get(self, "schema_columns")

    @schema_columns.setter
    def schema_columns(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]]]):
        pulumi.set(self, "schema_columns", value)


@pulumi.input_type
class _DatasetAzureBlobState:
    def __init__(__self__, *,
                 additional_properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 annotations: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 data_factory_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 dynamic_filename_enabled: Optional[pulumi.Input[bool]] = None,
                 dynamic_path_enabled: Optional[pulumi.Input[bool]] = None,
                 filename: Optional[pulumi.Input[str]] = None,
                 folder: Optional[pulumi.Input[str]] = None,
                 linked_service_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 schema_columns: Optional[pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]]] = None):
        """
        Input properties used for looking up and filtering DatasetAzureBlob resources.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] additional_properties: A map of additional properties to associate with the Data Factory Dataset.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] annotations: List of tags that can be used for describing the Data Factory Dataset.
        :param pulumi.Input[str] data_factory_id: The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        :param pulumi.Input[str] description: The description for the Data Factory Dataset.
        :param pulumi.Input[bool] dynamic_filename_enabled: Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[bool] dynamic_path_enabled: Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[str] filename: The filename of the Azure Blob.
        :param pulumi.Input[str] folder: The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        :param pulumi.Input[str] linked_service_name: The Data Factory Linked Service name in which to associate the Dataset with.
        :param pulumi.Input[str] name: Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of parameters to associate with the Data Factory Dataset.
        :param pulumi.Input[str] path: The path of the Azure Blob.
        :param pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]] schema_columns: A `schema_column` block as defined below.
        """
        if additional_properties is not None:
            pulumi.set(__self__, "additional_properties", additional_properties)
        if annotations is not None:
            pulumi.set(__self__, "annotations", annotations)
        if data_factory_id is not None:
            pulumi.set(__self__, "data_factory_id", data_factory_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if dynamic_filename_enabled is not None:
            pulumi.set(__self__, "dynamic_filename_enabled", dynamic_filename_enabled)
        if dynamic_path_enabled is not None:
            pulumi.set(__self__, "dynamic_path_enabled", dynamic_path_enabled)
        if filename is not None:
            pulumi.set(__self__, "filename", filename)
        if folder is not None:
            pulumi.set(__self__, "folder", folder)
        if linked_service_name is not None:
            pulumi.set(__self__, "linked_service_name", linked_service_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parameters is not None:
            pulumi.set(__self__, "parameters", parameters)
        if path is not None:
            pulumi.set(__self__, "path", path)
        if schema_columns is not None:
            pulumi.set(__self__, "schema_columns", schema_columns)

    @property
    @pulumi.getter(name="additionalProperties")
    def additional_properties(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of additional properties to associate with the Data Factory Dataset.
        """
        return pulumi.get(self, "additional_properties")

    @additional_properties.setter
    def additional_properties(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "additional_properties", value)

    @property
    @pulumi.getter
    def annotations(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of tags that can be used for describing the Data Factory Dataset.
        """
        return pulumi.get(self, "annotations")

    @annotations.setter
    def annotations(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "annotations", value)

    @property
    @pulumi.getter(name="dataFactoryId")
    def data_factory_id(self) -> Optional[pulumi.Input[str]]:
        """
        The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        """
        return pulumi.get(self, "data_factory_id")

    @data_factory_id.setter
    def data_factory_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "data_factory_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description for the Data Factory Dataset.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="dynamicFilenameEnabled")
    def dynamic_filename_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        """
        return pulumi.get(self, "dynamic_filename_enabled")

    @dynamic_filename_enabled.setter
    def dynamic_filename_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "dynamic_filename_enabled", value)

    @property
    @pulumi.getter(name="dynamicPathEnabled")
    def dynamic_path_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        """
        return pulumi.get(self, "dynamic_path_enabled")

    @dynamic_path_enabled.setter
    def dynamic_path_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "dynamic_path_enabled", value)

    @property
    @pulumi.getter
    def filename(self) -> Optional[pulumi.Input[str]]:
        """
        The filename of the Azure Blob.
        """
        return pulumi.get(self, "filename")

    @filename.setter
    def filename(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "filename", value)

    @property
    @pulumi.getter
    def folder(self) -> Optional[pulumi.Input[str]]:
        """
        The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        """
        return pulumi.get(self, "folder")

    @folder.setter
    def folder(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "folder", value)

    @property
    @pulumi.getter(name="linkedServiceName")
    def linked_service_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Data Factory Linked Service name in which to associate the Dataset with.
        """
        return pulumi.get(self, "linked_service_name")

    @linked_service_name.setter
    def linked_service_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "linked_service_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def parameters(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of parameters to associate with the Data Factory Dataset.
        """
        return pulumi.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameters", value)

    @property
    @pulumi.getter
    def path(self) -> Optional[pulumi.Input[str]]:
        """
        The path of the Azure Blob.
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "path", value)

    @property
    @pulumi.getter(name="schemaColumns")
    def schema_columns(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]]]:
        """
        A `schema_column` block as defined below.
        """
        return pulumi.get(self, "schema_columns")

    @schema_columns.setter
    def schema_columns(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['DatasetAzureBlobSchemaColumnArgs']]]]):
        pulumi.set(self, "schema_columns", value)


class DatasetAzureBlob(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 additional_properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 annotations: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 data_factory_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 dynamic_filename_enabled: Optional[pulumi.Input[bool]] = None,
                 dynamic_path_enabled: Optional[pulumi.Input[bool]] = None,
                 filename: Optional[pulumi.Input[str]] = None,
                 folder: Optional[pulumi.Input[str]] = None,
                 linked_service_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 schema_columns: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatasetAzureBlobSchemaColumnArgs']]]]] = None,
                 __props__=None):
        """
        Manages an Azure Blob Dataset inside an Azure Data Factory.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_account = azure.storage.get_account_output(name="storageaccountname",
            resource_group_name=example_resource_group.name)
        example_factory = azure.datafactory.Factory("exampleFactory",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name)
        example_linked_service_azure_blob_storage = azure.datafactory.LinkedServiceAzureBlobStorage("exampleLinkedServiceAzureBlobStorage",
            data_factory_id=example_factory.id,
            connection_string=example_account.primary_connection_string)
        example_dataset_azure_blob = azure.datafactory.DatasetAzureBlob("exampleDatasetAzureBlob",
            data_factory_id=example_factory.id,
            linked_service_name=example_linked_service_azure_blob_storage.name,
            path="foo",
            filename="bar.png")
        ```

        ## Import

        Data Factory Datasets can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:datafactory/datasetAzureBlob:DatasetAzureBlob example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.DataFactory/factories/example/datasets/example
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] additional_properties: A map of additional properties to associate with the Data Factory Dataset.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] annotations: List of tags that can be used for describing the Data Factory Dataset.
        :param pulumi.Input[str] data_factory_id: The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        :param pulumi.Input[str] description: The description for the Data Factory Dataset.
        :param pulumi.Input[bool] dynamic_filename_enabled: Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[bool] dynamic_path_enabled: Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[str] filename: The filename of the Azure Blob.
        :param pulumi.Input[str] folder: The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        :param pulumi.Input[str] linked_service_name: The Data Factory Linked Service name in which to associate the Dataset with.
        :param pulumi.Input[str] name: Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of parameters to associate with the Data Factory Dataset.
        :param pulumi.Input[str] path: The path of the Azure Blob.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatasetAzureBlobSchemaColumnArgs']]]] schema_columns: A `schema_column` block as defined below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: DatasetAzureBlobArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an Azure Blob Dataset inside an Azure Data Factory.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_account = azure.storage.get_account_output(name="storageaccountname",
            resource_group_name=example_resource_group.name)
        example_factory = azure.datafactory.Factory("exampleFactory",
            location=example_resource_group.location,
            resource_group_name=example_resource_group.name)
        example_linked_service_azure_blob_storage = azure.datafactory.LinkedServiceAzureBlobStorage("exampleLinkedServiceAzureBlobStorage",
            data_factory_id=example_factory.id,
            connection_string=example_account.primary_connection_string)
        example_dataset_azure_blob = azure.datafactory.DatasetAzureBlob("exampleDatasetAzureBlob",
            data_factory_id=example_factory.id,
            linked_service_name=example_linked_service_azure_blob_storage.name,
            path="foo",
            filename="bar.png")
        ```

        ## Import

        Data Factory Datasets can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:datafactory/datasetAzureBlob:DatasetAzureBlob example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example/providers/Microsoft.DataFactory/factories/example/datasets/example
        ```

        :param str resource_name: The name of the resource.
        :param DatasetAzureBlobArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(DatasetAzureBlobArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 additional_properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 annotations: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 data_factory_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 dynamic_filename_enabled: Optional[pulumi.Input[bool]] = None,
                 dynamic_path_enabled: Optional[pulumi.Input[bool]] = None,
                 filename: Optional[pulumi.Input[str]] = None,
                 folder: Optional[pulumi.Input[str]] = None,
                 linked_service_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 schema_columns: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatasetAzureBlobSchemaColumnArgs']]]]] = None,
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
            __props__ = DatasetAzureBlobArgs.__new__(DatasetAzureBlobArgs)

            __props__.__dict__["additional_properties"] = additional_properties
            __props__.__dict__["annotations"] = annotations
            if data_factory_id is None and not opts.urn:
                raise TypeError("Missing required property 'data_factory_id'")
            __props__.__dict__["data_factory_id"] = data_factory_id
            __props__.__dict__["description"] = description
            __props__.__dict__["dynamic_filename_enabled"] = dynamic_filename_enabled
            __props__.__dict__["dynamic_path_enabled"] = dynamic_path_enabled
            __props__.__dict__["filename"] = filename
            __props__.__dict__["folder"] = folder
            if linked_service_name is None and not opts.urn:
                raise TypeError("Missing required property 'linked_service_name'")
            __props__.__dict__["linked_service_name"] = linked_service_name
            __props__.__dict__["name"] = name
            __props__.__dict__["parameters"] = parameters
            __props__.__dict__["path"] = path
            __props__.__dict__["schema_columns"] = schema_columns
        super(DatasetAzureBlob, __self__).__init__(
            'azure:datafactory/datasetAzureBlob:DatasetAzureBlob',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            additional_properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            annotations: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            data_factory_id: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            dynamic_filename_enabled: Optional[pulumi.Input[bool]] = None,
            dynamic_path_enabled: Optional[pulumi.Input[bool]] = None,
            filename: Optional[pulumi.Input[str]] = None,
            folder: Optional[pulumi.Input[str]] = None,
            linked_service_name: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            path: Optional[pulumi.Input[str]] = None,
            schema_columns: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatasetAzureBlobSchemaColumnArgs']]]]] = None) -> 'DatasetAzureBlob':
        """
        Get an existing DatasetAzureBlob resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] additional_properties: A map of additional properties to associate with the Data Factory Dataset.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] annotations: List of tags that can be used for describing the Data Factory Dataset.
        :param pulumi.Input[str] data_factory_id: The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        :param pulumi.Input[str] description: The description for the Data Factory Dataset.
        :param pulumi.Input[bool] dynamic_filename_enabled: Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[bool] dynamic_path_enabled: Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        :param pulumi.Input[str] filename: The filename of the Azure Blob.
        :param pulumi.Input[str] folder: The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        :param pulumi.Input[str] linked_service_name: The Data Factory Linked Service name in which to associate the Dataset with.
        :param pulumi.Input[str] name: Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of parameters to associate with the Data Factory Dataset.
        :param pulumi.Input[str] path: The path of the Azure Blob.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatasetAzureBlobSchemaColumnArgs']]]] schema_columns: A `schema_column` block as defined below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _DatasetAzureBlobState.__new__(_DatasetAzureBlobState)

        __props__.__dict__["additional_properties"] = additional_properties
        __props__.__dict__["annotations"] = annotations
        __props__.__dict__["data_factory_id"] = data_factory_id
        __props__.__dict__["description"] = description
        __props__.__dict__["dynamic_filename_enabled"] = dynamic_filename_enabled
        __props__.__dict__["dynamic_path_enabled"] = dynamic_path_enabled
        __props__.__dict__["filename"] = filename
        __props__.__dict__["folder"] = folder
        __props__.__dict__["linked_service_name"] = linked_service_name
        __props__.__dict__["name"] = name
        __props__.__dict__["parameters"] = parameters
        __props__.__dict__["path"] = path
        __props__.__dict__["schema_columns"] = schema_columns
        return DatasetAzureBlob(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="additionalProperties")
    def additional_properties(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of additional properties to associate with the Data Factory Dataset.
        """
        return pulumi.get(self, "additional_properties")

    @property
    @pulumi.getter
    def annotations(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        List of tags that can be used for describing the Data Factory Dataset.
        """
        return pulumi.get(self, "annotations")

    @property
    @pulumi.getter(name="dataFactoryId")
    def data_factory_id(self) -> pulumi.Output[str]:
        """
        The Data Factory ID in which to associate the Linked Service with. Changing this forces a new resource.
        """
        return pulumi.get(self, "data_factory_id")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        The description for the Data Factory Dataset.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="dynamicFilenameEnabled")
    def dynamic_filename_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Is the `filename` using dynamic expression, function or system variables? Defaults to `false`.
        """
        return pulumi.get(self, "dynamic_filename_enabled")

    @property
    @pulumi.getter(name="dynamicPathEnabled")
    def dynamic_path_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Is the `path` using dynamic expression, function or system variables? Defaults to `false`.
        """
        return pulumi.get(self, "dynamic_path_enabled")

    @property
    @pulumi.getter
    def filename(self) -> pulumi.Output[Optional[str]]:
        """
        The filename of the Azure Blob.
        """
        return pulumi.get(self, "filename")

    @property
    @pulumi.getter
    def folder(self) -> pulumi.Output[Optional[str]]:
        """
        The folder that this Dataset is in. If not specified, the Dataset will appear at the root level.
        """
        return pulumi.get(self, "folder")

    @property
    @pulumi.getter(name="linkedServiceName")
    def linked_service_name(self) -> pulumi.Output[str]:
        """
        The Data Factory Linked Service name in which to associate the Dataset with.
        """
        return pulumi.get(self, "linked_service_name")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the Data Factory Dataset. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def parameters(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of parameters to associate with the Data Factory Dataset.
        """
        return pulumi.get(self, "parameters")

    @property
    @pulumi.getter
    def path(self) -> pulumi.Output[Optional[str]]:
        """
        The path of the Azure Blob.
        """
        return pulumi.get(self, "path")

    @property
    @pulumi.getter(name="schemaColumns")
    def schema_columns(self) -> pulumi.Output[Optional[Sequence['outputs.DatasetAzureBlobSchemaColumn']]]:
        """
        A `schema_column` block as defined below.
        """
        return pulumi.get(self, "schema_columns")

