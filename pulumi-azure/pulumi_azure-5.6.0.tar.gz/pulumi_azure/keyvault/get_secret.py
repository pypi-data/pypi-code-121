# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetSecretResult',
    'AwaitableGetSecretResult',
    'get_secret',
    'get_secret_output',
]

@pulumi.output_type
class GetSecretResult:
    """
    A collection of values returned by getSecret.
    """
    def __init__(__self__, content_type=None, id=None, key_vault_id=None, name=None, tags=None, value=None, version=None, versionless_id=None):
        if content_type and not isinstance(content_type, str):
            raise TypeError("Expected argument 'content_type' to be a str")
        pulumi.set(__self__, "content_type", content_type)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if key_vault_id and not isinstance(key_vault_id, str):
            raise TypeError("Expected argument 'key_vault_id' to be a str")
        pulumi.set(__self__, "key_vault_id", key_vault_id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if value and not isinstance(value, str):
            raise TypeError("Expected argument 'value' to be a str")
        pulumi.set(__self__, "value", value)
        if version and not isinstance(version, str):
            raise TypeError("Expected argument 'version' to be a str")
        pulumi.set(__self__, "version", version)
        if versionless_id and not isinstance(versionless_id, str):
            raise TypeError("Expected argument 'versionless_id' to be a str")
        pulumi.set(__self__, "versionless_id", versionless_id)

    @property
    @pulumi.getter(name="contentType")
    def content_type(self) -> str:
        """
        The content type for the Key Vault Secret.
        """
        return pulumi.get(self, "content_type")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="keyVaultId")
    def key_vault_id(self) -> str:
        return pulumi.get(self, "key_vault_id")

    @property
    @pulumi.getter
    def name(self) -> str:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        Any tags assigned to this resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter
    def value(self) -> str:
        """
        The value of the Key Vault Secret.
        """
        return pulumi.get(self, "value")

    @property
    @pulumi.getter
    def version(self) -> str:
        """
        The current version of the Key Vault Secret.
        """
        return pulumi.get(self, "version")

    @property
    @pulumi.getter(name="versionlessId")
    def versionless_id(self) -> str:
        return pulumi.get(self, "versionless_id")


class AwaitableGetSecretResult(GetSecretResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetSecretResult(
            content_type=self.content_type,
            id=self.id,
            key_vault_id=self.key_vault_id,
            name=self.name,
            tags=self.tags,
            value=self.value,
            version=self.version,
            versionless_id=self.versionless_id)


def get_secret(key_vault_id: Optional[str] = None,
               name: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetSecretResult:
    """
    Use this data source to access information about an existing Key Vault Secret.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.keyvault.get_secret(name="secret-sauce",
        key_vault_id=data["azurerm_key_vault"]["existing"]["id"])
    pulumi.export("secretValue", example.value)
    ```


    :param str key_vault_id: Specifies the ID of the Key Vault instance where the Secret resides, available on the `keyvault.KeyVault` Data Source / Resource.
    :param str name: Specifies the name of the Key Vault Secret.
    """
    __args__ = dict()
    __args__['keyVaultId'] = key_vault_id
    __args__['name'] = name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:keyvault/getSecret:getSecret', __args__, opts=opts, typ=GetSecretResult).value

    return AwaitableGetSecretResult(
        content_type=__ret__.content_type,
        id=__ret__.id,
        key_vault_id=__ret__.key_vault_id,
        name=__ret__.name,
        tags=__ret__.tags,
        value=__ret__.value,
        version=__ret__.version,
        versionless_id=__ret__.versionless_id)


@_utilities.lift_output_func(get_secret)
def get_secret_output(key_vault_id: Optional[pulumi.Input[str]] = None,
                      name: Optional[pulumi.Input[str]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetSecretResult]:
    """
    Use this data source to access information about an existing Key Vault Secret.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.keyvault.get_secret(name="secret-sauce",
        key_vault_id=data["azurerm_key_vault"]["existing"]["id"])
    pulumi.export("secretValue", example.value)
    ```


    :param str key_vault_id: Specifies the ID of the Key Vault instance where the Secret resides, available on the `keyvault.KeyVault` Data Source / Resource.
    :param str name: Specifies the name of the Key Vault Secret.
    """
    ...
