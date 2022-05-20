# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'AccountIdentity',
    'AccountNetworkAcls',
    'AccountNetworkAclsVirtualNetworkRule',
    'AccountStorage',
]

@pulumi.output_type
class AccountIdentity(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "identityIds":
            suggest = "identity_ids"
        elif key == "principalId":
            suggest = "principal_id"
        elif key == "tenantId":
            suggest = "tenant_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AccountIdentity. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AccountIdentity.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AccountIdentity.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 type: str,
                 identity_ids: Optional[Sequence[str]] = None,
                 principal_id: Optional[str] = None,
                 tenant_id: Optional[str] = None):
        """
        :param str type: Specifies the type of Managed Service Identity that should be configured on this Cognitive Account. Possible values are `SystemAssigned`, `UserAssigned`, `SystemAssigned, UserAssigned` (to enable both).
        :param Sequence[str] identity_ids: Specifies a list of User Assigned Managed Identity IDs to be assigned to this Cognitive Account.
        :param str principal_id: The Principal ID associated with this Managed Service Identity.
        :param str tenant_id: The Tenant ID associated with this Managed Service Identity.
        """
        pulumi.set(__self__, "type", type)
        if identity_ids is not None:
            pulumi.set(__self__, "identity_ids", identity_ids)
        if principal_id is not None:
            pulumi.set(__self__, "principal_id", principal_id)
        if tenant_id is not None:
            pulumi.set(__self__, "tenant_id", tenant_id)

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        Specifies the type of Managed Service Identity that should be configured on this Cognitive Account. Possible values are `SystemAssigned`, `UserAssigned`, `SystemAssigned, UserAssigned` (to enable both).
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter(name="identityIds")
    def identity_ids(self) -> Optional[Sequence[str]]:
        """
        Specifies a list of User Assigned Managed Identity IDs to be assigned to this Cognitive Account.
        """
        return pulumi.get(self, "identity_ids")

    @property
    @pulumi.getter(name="principalId")
    def principal_id(self) -> Optional[str]:
        """
        The Principal ID associated with this Managed Service Identity.
        """
        return pulumi.get(self, "principal_id")

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> Optional[str]:
        """
        The Tenant ID associated with this Managed Service Identity.
        """
        return pulumi.get(self, "tenant_id")


@pulumi.output_type
class AccountNetworkAcls(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "defaultAction":
            suggest = "default_action"
        elif key == "ipRules":
            suggest = "ip_rules"
        elif key == "virtualNetworkRules":
            suggest = "virtual_network_rules"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AccountNetworkAcls. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AccountNetworkAcls.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AccountNetworkAcls.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 default_action: str,
                 ip_rules: Optional[Sequence[str]] = None,
                 virtual_network_rules: Optional[Sequence['outputs.AccountNetworkAclsVirtualNetworkRule']] = None):
        """
        :param str default_action: The Default Action to use when no rules match from `ip_rules` / `virtual_network_rules`. Possible values are `Allow` and `Deny`.
        :param Sequence[str] ip_rules: One or more IP Addresses, or CIDR Blocks which should be able to access the Cognitive Account.
        :param Sequence['AccountNetworkAclsVirtualNetworkRuleArgs'] virtual_network_rules: A `virtual_network_rules` block as defined below.
        """
        pulumi.set(__self__, "default_action", default_action)
        if ip_rules is not None:
            pulumi.set(__self__, "ip_rules", ip_rules)
        if virtual_network_rules is not None:
            pulumi.set(__self__, "virtual_network_rules", virtual_network_rules)

    @property
    @pulumi.getter(name="defaultAction")
    def default_action(self) -> str:
        """
        The Default Action to use when no rules match from `ip_rules` / `virtual_network_rules`. Possible values are `Allow` and `Deny`.
        """
        return pulumi.get(self, "default_action")

    @property
    @pulumi.getter(name="ipRules")
    def ip_rules(self) -> Optional[Sequence[str]]:
        """
        One or more IP Addresses, or CIDR Blocks which should be able to access the Cognitive Account.
        """
        return pulumi.get(self, "ip_rules")

    @property
    @pulumi.getter(name="virtualNetworkRules")
    def virtual_network_rules(self) -> Optional[Sequence['outputs.AccountNetworkAclsVirtualNetworkRule']]:
        """
        A `virtual_network_rules` block as defined below.
        """
        return pulumi.get(self, "virtual_network_rules")


@pulumi.output_type
class AccountNetworkAclsVirtualNetworkRule(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "subnetId":
            suggest = "subnet_id"
        elif key == "ignoreMissingVnetServiceEndpoint":
            suggest = "ignore_missing_vnet_service_endpoint"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AccountNetworkAclsVirtualNetworkRule. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AccountNetworkAclsVirtualNetworkRule.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AccountNetworkAclsVirtualNetworkRule.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 subnet_id: str,
                 ignore_missing_vnet_service_endpoint: Optional[bool] = None):
        """
        :param str subnet_id: The ID of the subnet which should be able to access this Cognitive Account.
        :param bool ignore_missing_vnet_service_endpoint: Whether ignore missing vnet service endpoint or not. Default to `false`.
        """
        pulumi.set(__self__, "subnet_id", subnet_id)
        if ignore_missing_vnet_service_endpoint is not None:
            pulumi.set(__self__, "ignore_missing_vnet_service_endpoint", ignore_missing_vnet_service_endpoint)

    @property
    @pulumi.getter(name="subnetId")
    def subnet_id(self) -> str:
        """
        The ID of the subnet which should be able to access this Cognitive Account.
        """
        return pulumi.get(self, "subnet_id")

    @property
    @pulumi.getter(name="ignoreMissingVnetServiceEndpoint")
    def ignore_missing_vnet_service_endpoint(self) -> Optional[bool]:
        """
        Whether ignore missing vnet service endpoint or not. Default to `false`.
        """
        return pulumi.get(self, "ignore_missing_vnet_service_endpoint")


@pulumi.output_type
class AccountStorage(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "storageAccountId":
            suggest = "storage_account_id"
        elif key == "identityClientId":
            suggest = "identity_client_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AccountStorage. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AccountStorage.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AccountStorage.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 storage_account_id: str,
                 identity_client_id: Optional[str] = None):
        """
        :param str storage_account_id: Full resource id of a Microsoft.Storage resource.
        :param str identity_client_id: The client ID of the managed identity associated with the storage resource.
        """
        pulumi.set(__self__, "storage_account_id", storage_account_id)
        if identity_client_id is not None:
            pulumi.set(__self__, "identity_client_id", identity_client_id)

    @property
    @pulumi.getter(name="storageAccountId")
    def storage_account_id(self) -> str:
        """
        Full resource id of a Microsoft.Storage resource.
        """
        return pulumi.get(self, "storage_account_id")

    @property
    @pulumi.getter(name="identityClientId")
    def identity_client_id(self) -> Optional[str]:
        """
        The client ID of the managed identity associated with the storage resource.
        """
        return pulumi.get(self, "identity_client_id")


