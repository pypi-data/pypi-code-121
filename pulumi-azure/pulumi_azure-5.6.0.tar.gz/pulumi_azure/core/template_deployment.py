# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['TemplateDeploymentArgs', 'TemplateDeployment']

@pulumi.input_type
class TemplateDeploymentArgs:
    def __init__(__self__, *,
                 deployment_mode: pulumi.Input[str],
                 resource_group_name: pulumi.Input[str],
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 parameters_body: Optional[pulumi.Input[str]] = None,
                 template_body: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a TemplateDeployment resource.
        :param pulumi.Input[str] deployment_mode: Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
               Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
               specified within the template, and this provider will not be aware of this.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to
               create the template deployment.
        :param pulumi.Input[str] name: Specifies the name of the template deployment. Changing this forces a
               new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: Specifies the name and value pairs that define the deployment parameters for the template.
        :param pulumi.Input[str] parameters_body: Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        :param pulumi.Input[str] template_body: Specifies the JSON definition for the template.
        """
        pulumi.set(__self__, "deployment_mode", deployment_mode)
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parameters is not None:
            pulumi.set(__self__, "parameters", parameters)
        if parameters_body is not None:
            pulumi.set(__self__, "parameters_body", parameters_body)
        if template_body is not None:
            pulumi.set(__self__, "template_body", template_body)

    @property
    @pulumi.getter(name="deploymentMode")
    def deployment_mode(self) -> pulumi.Input[str]:
        """
        Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
        Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
        specified within the template, and this provider will not be aware of this.
        """
        return pulumi.get(self, "deployment_mode")

    @deployment_mode.setter
    def deployment_mode(self, value: pulumi.Input[str]):
        pulumi.set(self, "deployment_mode", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group in which to
        create the template deployment.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the template deployment. Changing this forces a
        new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def parameters(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Specifies the name and value pairs that define the deployment parameters for the template.
        """
        return pulumi.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameters", value)

    @property
    @pulumi.getter(name="parametersBody")
    def parameters_body(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        """
        return pulumi.get(self, "parameters_body")

    @parameters_body.setter
    def parameters_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "parameters_body", value)

    @property
    @pulumi.getter(name="templateBody")
    def template_body(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the JSON definition for the template.
        """
        return pulumi.get(self, "template_body")

    @template_body.setter
    def template_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "template_body", value)


@pulumi.input_type
class _TemplateDeploymentState:
    def __init__(__self__, *,
                 deployment_mode: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 outputs: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 parameters_body: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 template_body: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering TemplateDeployment resources.
        :param pulumi.Input[str] deployment_mode: Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
               Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
               specified within the template, and this provider will not be aware of this.
        :param pulumi.Input[str] name: Specifies the name of the template deployment. Changing this forces a
               new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] outputs: A map of supported scalar output types returned from the deployment (currently, Azure Template Deployment outputs of type String, Int and Bool are supported, and are converted to strings - others will be ignored) and can be accessed using `.outputs["name"]`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: Specifies the name and value pairs that define the deployment parameters for the template.
        :param pulumi.Input[str] parameters_body: Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to
               create the template deployment.
        :param pulumi.Input[str] template_body: Specifies the JSON definition for the template.
        """
        if deployment_mode is not None:
            pulumi.set(__self__, "deployment_mode", deployment_mode)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if outputs is not None:
            pulumi.set(__self__, "outputs", outputs)
        if parameters is not None:
            pulumi.set(__self__, "parameters", parameters)
        if parameters_body is not None:
            pulumi.set(__self__, "parameters_body", parameters_body)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if template_body is not None:
            pulumi.set(__self__, "template_body", template_body)

    @property
    @pulumi.getter(name="deploymentMode")
    def deployment_mode(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
        Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
        specified within the template, and this provider will not be aware of this.
        """
        return pulumi.get(self, "deployment_mode")

    @deployment_mode.setter
    def deployment_mode(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "deployment_mode", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the template deployment. Changing this forces a
        new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def outputs(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of supported scalar output types returned from the deployment (currently, Azure Template Deployment outputs of type String, Int and Bool are supported, and are converted to strings - others will be ignored) and can be accessed using `.outputs["name"]`.
        """
        return pulumi.get(self, "outputs")

    @outputs.setter
    def outputs(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "outputs", value)

    @property
    @pulumi.getter
    def parameters(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Specifies the name and value pairs that define the deployment parameters for the template.
        """
        return pulumi.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameters", value)

    @property
    @pulumi.getter(name="parametersBody")
    def parameters_body(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        """
        return pulumi.get(self, "parameters_body")

    @parameters_body.setter
    def parameters_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "parameters_body", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group in which to
        create the template deployment.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="templateBody")
    def template_body(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the JSON definition for the template.
        """
        return pulumi.get(self, "template_body")

    @template_body.setter
    def template_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "template_body", value)


class TemplateDeployment(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 deployment_mode: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 parameters_body: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 template_body: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a template deployment of resources

        > **Note on ARM Template Deployments:** Due to the way the underlying Azure API is designed, this provider can only manage the deployment of the ARM Template - and not any resources which are created by it.
        This means that when deleting the `core.TemplateDeployment` resource, this provider will only remove the reference to the deployment, whilst leaving any resources created by that ARM Template Deployment.
        One workaround for this is to use a unique Resource Group for each ARM Template Deployment, which means deleting the Resource Group would contain any resources created within it - however this isn't ideal. [More information](https://docs.microsoft.com/en-us/rest/api/resources/deployments#Deployments_Delete).

        ## Example Usage

        > **Note:** This example uses Storage Accounts and Public IP's which are natively supported by this provider - we'd highly recommend using the Native Resources where possible instead rather than an ARM Template, for the reasons outlined above.

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_template_deployment = azure.core.TemplateDeployment("exampleTemplateDeployment",
            resource_group_name=example_resource_group.name,
            template_body=\"\"\"{
          "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
          "contentVersion": "1.0.0.0",
          "parameters": {
            "storageAccountType": {
              "type": "string",
              "defaultValue": "Standard_LRS",
              "allowedValues": [
                "Standard_LRS",
                "Standard_GRS",
                "Standard_ZRS"
              ],
              "metadata": {
                "description": "Storage Account type"
              }
            }
          },
          "variables": {
            "location": "[resourceGroup().location]",
            "storageAccountName": "[concat(uniquestring(resourceGroup().id), 'storage')]",
            "publicIPAddressName": "[concat('myPublicIp', uniquestring(resourceGroup().id))]",
            "publicIPAddressType": "Dynamic",
            "apiVersion": "2015-06-15",
            "dnsLabelPrefix": "example-acctest"
          },
          "resources": [
            {
              "type": "Microsoft.Storage/storageAccounts",
              "name": "[variables('storageAccountName')]",
              "apiVersion": "[variables('apiVersion')]",
              "location": "[variables('location')]",
              "properties": {
                "accountType": "[parameters('storageAccountType')]"
              }
            },
            {
              "type": "Microsoft.Network/publicIPAddresses",
              "apiVersion": "[variables('apiVersion')]",
              "name": "[variables('publicIPAddressName')]",
              "location": "[variables('location')]",
              "properties": {
                "publicIPAllocationMethod": "[variables('publicIPAddressType')]",
                "dnsSettings": {
                  "domainNameLabel": "[variables('dnsLabelPrefix')]"
                }
              }
            }
          ],
          "outputs": {
            "storageAccountName": {
              "type": "string",
              "value": "[variables('storageAccountName')]"
            }
          }
        }
        \"\"\",
            parameters={
                "storageAccountType": "Standard_GRS",
            },
            deployment_mode="Incremental")
        pulumi.export("storageAccountName", example_template_deployment.outputs["storageAccountName"])
        ```
        ## Note

        This provider does not know about the individual resources created by Azure using a deployment template and therefore cannot delete these resources during a destroy. Destroying a template deployment removes the associated deployment operations, but will not delete the Azure resources created by the deployment. In order to delete these resources, the containing resource group must also be destroyed. [More information](https://docs.microsoft.com/en-us/rest/api/resources/deployments#Deployments_Delete).

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] deployment_mode: Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
               Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
               specified within the template, and this provider will not be aware of this.
        :param pulumi.Input[str] name: Specifies the name of the template deployment. Changing this forces a
               new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: Specifies the name and value pairs that define the deployment parameters for the template.
        :param pulumi.Input[str] parameters_body: Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to
               create the template deployment.
        :param pulumi.Input[str] template_body: Specifies the JSON definition for the template.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: TemplateDeploymentArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a template deployment of resources

        > **Note on ARM Template Deployments:** Due to the way the underlying Azure API is designed, this provider can only manage the deployment of the ARM Template - and not any resources which are created by it.
        This means that when deleting the `core.TemplateDeployment` resource, this provider will only remove the reference to the deployment, whilst leaving any resources created by that ARM Template Deployment.
        One workaround for this is to use a unique Resource Group for each ARM Template Deployment, which means deleting the Resource Group would contain any resources created within it - however this isn't ideal. [More information](https://docs.microsoft.com/en-us/rest/api/resources/deployments#Deployments_Delete).

        ## Example Usage

        > **Note:** This example uses Storage Accounts and Public IP's which are natively supported by this provider - we'd highly recommend using the Native Resources where possible instead rather than an ARM Template, for the reasons outlined above.

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_template_deployment = azure.core.TemplateDeployment("exampleTemplateDeployment",
            resource_group_name=example_resource_group.name,
            template_body=\"\"\"{
          "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
          "contentVersion": "1.0.0.0",
          "parameters": {
            "storageAccountType": {
              "type": "string",
              "defaultValue": "Standard_LRS",
              "allowedValues": [
                "Standard_LRS",
                "Standard_GRS",
                "Standard_ZRS"
              ],
              "metadata": {
                "description": "Storage Account type"
              }
            }
          },
          "variables": {
            "location": "[resourceGroup().location]",
            "storageAccountName": "[concat(uniquestring(resourceGroup().id), 'storage')]",
            "publicIPAddressName": "[concat('myPublicIp', uniquestring(resourceGroup().id))]",
            "publicIPAddressType": "Dynamic",
            "apiVersion": "2015-06-15",
            "dnsLabelPrefix": "example-acctest"
          },
          "resources": [
            {
              "type": "Microsoft.Storage/storageAccounts",
              "name": "[variables('storageAccountName')]",
              "apiVersion": "[variables('apiVersion')]",
              "location": "[variables('location')]",
              "properties": {
                "accountType": "[parameters('storageAccountType')]"
              }
            },
            {
              "type": "Microsoft.Network/publicIPAddresses",
              "apiVersion": "[variables('apiVersion')]",
              "name": "[variables('publicIPAddressName')]",
              "location": "[variables('location')]",
              "properties": {
                "publicIPAllocationMethod": "[variables('publicIPAddressType')]",
                "dnsSettings": {
                  "domainNameLabel": "[variables('dnsLabelPrefix')]"
                }
              }
            }
          ],
          "outputs": {
            "storageAccountName": {
              "type": "string",
              "value": "[variables('storageAccountName')]"
            }
          }
        }
        \"\"\",
            parameters={
                "storageAccountType": "Standard_GRS",
            },
            deployment_mode="Incremental")
        pulumi.export("storageAccountName", example_template_deployment.outputs["storageAccountName"])
        ```
        ## Note

        This provider does not know about the individual resources created by Azure using a deployment template and therefore cannot delete these resources during a destroy. Destroying a template deployment removes the associated deployment operations, but will not delete the Azure resources created by the deployment. In order to delete these resources, the containing resource group must also be destroyed. [More information](https://docs.microsoft.com/en-us/rest/api/resources/deployments#Deployments_Delete).

        :param str resource_name: The name of the resource.
        :param TemplateDeploymentArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(TemplateDeploymentArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 deployment_mode: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 parameters_body: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 template_body: Optional[pulumi.Input[str]] = None,
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
            __props__ = TemplateDeploymentArgs.__new__(TemplateDeploymentArgs)

            if deployment_mode is None and not opts.urn:
                raise TypeError("Missing required property 'deployment_mode'")
            __props__.__dict__["deployment_mode"] = deployment_mode
            __props__.__dict__["name"] = name
            __props__.__dict__["parameters"] = parameters
            __props__.__dict__["parameters_body"] = parameters_body
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            __props__.__dict__["template_body"] = template_body
            __props__.__dict__["outputs"] = None
        super(TemplateDeployment, __self__).__init__(
            'azure:core/templateDeployment:TemplateDeployment',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            deployment_mode: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            outputs: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            parameters_body: Optional[pulumi.Input[str]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            template_body: Optional[pulumi.Input[str]] = None) -> 'TemplateDeployment':
        """
        Get an existing TemplateDeployment resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] deployment_mode: Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
               Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
               specified within the template, and this provider will not be aware of this.
        :param pulumi.Input[str] name: Specifies the name of the template deployment. Changing this forces a
               new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] outputs: A map of supported scalar output types returned from the deployment (currently, Azure Template Deployment outputs of type String, Int and Bool are supported, and are converted to strings - others will be ignored) and can be accessed using `.outputs["name"]`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: Specifies the name and value pairs that define the deployment parameters for the template.
        :param pulumi.Input[str] parameters_body: Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to
               create the template deployment.
        :param pulumi.Input[str] template_body: Specifies the JSON definition for the template.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _TemplateDeploymentState.__new__(_TemplateDeploymentState)

        __props__.__dict__["deployment_mode"] = deployment_mode
        __props__.__dict__["name"] = name
        __props__.__dict__["outputs"] = outputs
        __props__.__dict__["parameters"] = parameters
        __props__.__dict__["parameters_body"] = parameters_body
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["template_body"] = template_body
        return TemplateDeployment(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="deploymentMode")
    def deployment_mode(self) -> pulumi.Output[str]:
        """
        Specifies the mode that is used to deploy resources. This value could be either `Incremental` or `Complete`.
        Note that you will almost *always* want this to be set to `Incremental` otherwise the deployment will destroy all infrastructure not
        specified within the template, and this provider will not be aware of this.
        """
        return pulumi.get(self, "deployment_mode")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the template deployment. Changing this forces a
        new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def outputs(self) -> pulumi.Output[Mapping[str, str]]:
        """
        A map of supported scalar output types returned from the deployment (currently, Azure Template Deployment outputs of type String, Int and Bool are supported, and are converted to strings - others will be ignored) and can be accessed using `.outputs["name"]`.
        """
        return pulumi.get(self, "outputs")

    @property
    @pulumi.getter
    def parameters(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Specifies the name and value pairs that define the deployment parameters for the template.
        """
        return pulumi.get(self, "parameters")

    @property
    @pulumi.getter(name="parametersBody")
    def parameters_body(self) -> pulumi.Output[Optional[str]]:
        """
        Specifies a valid Azure JSON parameters file that define the deployment parameters. It can contain KeyVault references
        """
        return pulumi.get(self, "parameters_body")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group in which to
        create the template deployment.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="templateBody")
    def template_body(self) -> pulumi.Output[str]:
        """
        Specifies the JSON definition for the template.
        """
        return pulumi.get(self, "template_body")

