# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ServerSecurityAlertPolicyArgs', 'ServerSecurityAlertPolicy']

@pulumi.input_type
class ServerSecurityAlertPolicyArgs:
    def __init__(__self__, *,
                 resource_group_name: pulumi.Input[str],
                 server_name: pulumi.Input[str],
                 state: pulumi.Input[str],
                 disabled_alerts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 email_account_admins: Optional[pulumi.Input[bool]] = None,
                 email_addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 retention_days: Optional[pulumi.Input[int]] = None,
                 storage_account_access_key: Optional[pulumi.Input[str]] = None,
                 storage_endpoint: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ServerSecurityAlertPolicy resource.
        :param pulumi.Input[str] resource_group_name: The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[str] server_name: Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[str] state: Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] disabled_alerts: Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        :param pulumi.Input[bool] email_account_admins: Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] email_addresses: Specifies an array of email addresses to which the alert is sent.
        :param pulumi.Input[int] retention_days: Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        :param pulumi.Input[str] storage_account_access_key: Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        :param pulumi.Input[str] storage_endpoint: Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "server_name", server_name)
        pulumi.set(__self__, "state", state)
        if disabled_alerts is not None:
            pulumi.set(__self__, "disabled_alerts", disabled_alerts)
        if email_account_admins is not None:
            pulumi.set(__self__, "email_account_admins", email_account_admins)
        if email_addresses is not None:
            pulumi.set(__self__, "email_addresses", email_addresses)
        if retention_days is not None:
            pulumi.set(__self__, "retention_days", retention_days)
        if storage_account_access_key is not None:
            pulumi.set(__self__, "storage_account_access_key", storage_account_access_key)
        if storage_endpoint is not None:
            pulumi.set(__self__, "storage_endpoint", storage_endpoint)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="serverName")
    def server_name(self) -> pulumi.Input[str]:
        """
        Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "server_name")

    @server_name.setter
    def server_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "server_name", value)

    @property
    @pulumi.getter
    def state(self) -> pulumi.Input[str]:
        """
        Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: pulumi.Input[str]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="disabledAlerts")
    def disabled_alerts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        """
        return pulumi.get(self, "disabled_alerts")

    @disabled_alerts.setter
    def disabled_alerts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "disabled_alerts", value)

    @property
    @pulumi.getter(name="emailAccountAdmins")
    def email_account_admins(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        """
        return pulumi.get(self, "email_account_admins")

    @email_account_admins.setter
    def email_account_admins(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "email_account_admins", value)

    @property
    @pulumi.getter(name="emailAddresses")
    def email_addresses(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies an array of email addresses to which the alert is sent.
        """
        return pulumi.get(self, "email_addresses")

    @email_addresses.setter
    def email_addresses(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "email_addresses", value)

    @property
    @pulumi.getter(name="retentionDays")
    def retention_days(self) -> Optional[pulumi.Input[int]]:
        """
        Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        """
        return pulumi.get(self, "retention_days")

    @retention_days.setter
    def retention_days(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "retention_days", value)

    @property
    @pulumi.getter(name="storageAccountAccessKey")
    def storage_account_access_key(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        """
        return pulumi.get(self, "storage_account_access_key")

    @storage_account_access_key.setter
    def storage_account_access_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "storage_account_access_key", value)

    @property
    @pulumi.getter(name="storageEndpoint")
    def storage_endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        return pulumi.get(self, "storage_endpoint")

    @storage_endpoint.setter
    def storage_endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "storage_endpoint", value)


@pulumi.input_type
class _ServerSecurityAlertPolicyState:
    def __init__(__self__, *,
                 disabled_alerts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 email_account_admins: Optional[pulumi.Input[bool]] = None,
                 email_addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 retention_days: Optional[pulumi.Input[int]] = None,
                 server_name: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 storage_account_access_key: Optional[pulumi.Input[str]] = None,
                 storage_endpoint: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ServerSecurityAlertPolicy resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] disabled_alerts: Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        :param pulumi.Input[bool] email_account_admins: Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] email_addresses: Specifies an array of email addresses to which the alert is sent.
        :param pulumi.Input[str] resource_group_name: The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[int] retention_days: Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        :param pulumi.Input[str] server_name: Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[str] state: Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        :param pulumi.Input[str] storage_account_access_key: Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        :param pulumi.Input[str] storage_endpoint: Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        if disabled_alerts is not None:
            pulumi.set(__self__, "disabled_alerts", disabled_alerts)
        if email_account_admins is not None:
            pulumi.set(__self__, "email_account_admins", email_account_admins)
        if email_addresses is not None:
            pulumi.set(__self__, "email_addresses", email_addresses)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if retention_days is not None:
            pulumi.set(__self__, "retention_days", retention_days)
        if server_name is not None:
            pulumi.set(__self__, "server_name", server_name)
        if state is not None:
            pulumi.set(__self__, "state", state)
        if storage_account_access_key is not None:
            pulumi.set(__self__, "storage_account_access_key", storage_account_access_key)
        if storage_endpoint is not None:
            pulumi.set(__self__, "storage_endpoint", storage_endpoint)

    @property
    @pulumi.getter(name="disabledAlerts")
    def disabled_alerts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        """
        return pulumi.get(self, "disabled_alerts")

    @disabled_alerts.setter
    def disabled_alerts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "disabled_alerts", value)

    @property
    @pulumi.getter(name="emailAccountAdmins")
    def email_account_admins(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        """
        return pulumi.get(self, "email_account_admins")

    @email_account_admins.setter
    def email_account_admins(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "email_account_admins", value)

    @property
    @pulumi.getter(name="emailAddresses")
    def email_addresses(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies an array of email addresses to which the alert is sent.
        """
        return pulumi.get(self, "email_addresses")

    @email_addresses.setter
    def email_addresses(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "email_addresses", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="retentionDays")
    def retention_days(self) -> Optional[pulumi.Input[int]]:
        """
        Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        """
        return pulumi.get(self, "retention_days")

    @retention_days.setter
    def retention_days(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "retention_days", value)

    @property
    @pulumi.getter(name="serverName")
    def server_name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "server_name")

    @server_name.setter
    def server_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "server_name", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="storageAccountAccessKey")
    def storage_account_access_key(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        """
        return pulumi.get(self, "storage_account_access_key")

    @storage_account_access_key.setter
    def storage_account_access_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "storage_account_access_key", value)

    @property
    @pulumi.getter(name="storageEndpoint")
    def storage_endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        return pulumi.get(self, "storage_endpoint")

    @storage_endpoint.setter
    def storage_endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "storage_endpoint", value)


class ServerSecurityAlertPolicy(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 disabled_alerts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 email_account_admins: Optional[pulumi.Input[bool]] = None,
                 email_addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 retention_days: Optional[pulumi.Input[int]] = None,
                 server_name: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 storage_account_access_key: Optional[pulumi.Input[str]] = None,
                 storage_endpoint: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Security Alert Policy for a MSSQL Server.

        > **NOTE** Security Alert Policy is currently only available for MS SQL databases.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_sql_server = azure.sql.SqlServer("exampleSqlServer",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            version="12.0",
            administrator_login="4dm1n157r470r",
            administrator_login_password="4-v3ry-53cr37-p455w0rd")
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_tier="Standard",
            account_replication_type="GRS")
        example_server_security_alert_policy = azure.mssql.ServerSecurityAlertPolicy("exampleServerSecurityAlertPolicy",
            resource_group_name=example_resource_group.name,
            server_name=example_sql_server.name,
            state="Enabled",
            storage_endpoint=example_account.primary_blob_endpoint,
            storage_account_access_key=example_account.primary_access_key,
            disabled_alerts=[
                "Sql_Injection",
                "Data_Exfiltration",
            ],
            retention_days=20)
        ```

        ## Import

        MS SQL Server Security Alert Policy can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:mssql/serverSecurityAlertPolicy:ServerSecurityAlertPolicy example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/acceptanceTestResourceGroup1/providers/Microsoft.Sql/servers/mssqlserver/securityAlertPolicies/Default
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] disabled_alerts: Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        :param pulumi.Input[bool] email_account_admins: Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] email_addresses: Specifies an array of email addresses to which the alert is sent.
        :param pulumi.Input[str] resource_group_name: The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[int] retention_days: Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        :param pulumi.Input[str] server_name: Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[str] state: Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        :param pulumi.Input[str] storage_account_access_key: Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        :param pulumi.Input[str] storage_endpoint: Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ServerSecurityAlertPolicyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Security Alert Policy for a MSSQL Server.

        > **NOTE** Security Alert Policy is currently only available for MS SQL databases.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_sql_server = azure.sql.SqlServer("exampleSqlServer",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            version="12.0",
            administrator_login="4dm1n157r470r",
            administrator_login_password="4-v3ry-53cr37-p455w0rd")
        example_account = azure.storage.Account("exampleAccount",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            account_tier="Standard",
            account_replication_type="GRS")
        example_server_security_alert_policy = azure.mssql.ServerSecurityAlertPolicy("exampleServerSecurityAlertPolicy",
            resource_group_name=example_resource_group.name,
            server_name=example_sql_server.name,
            state="Enabled",
            storage_endpoint=example_account.primary_blob_endpoint,
            storage_account_access_key=example_account.primary_access_key,
            disabled_alerts=[
                "Sql_Injection",
                "Data_Exfiltration",
            ],
            retention_days=20)
        ```

        ## Import

        MS SQL Server Security Alert Policy can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:mssql/serverSecurityAlertPolicy:ServerSecurityAlertPolicy example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/acceptanceTestResourceGroup1/providers/Microsoft.Sql/servers/mssqlserver/securityAlertPolicies/Default
        ```

        :param str resource_name: The name of the resource.
        :param ServerSecurityAlertPolicyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ServerSecurityAlertPolicyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 disabled_alerts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 email_account_admins: Optional[pulumi.Input[bool]] = None,
                 email_addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 retention_days: Optional[pulumi.Input[int]] = None,
                 server_name: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 storage_account_access_key: Optional[pulumi.Input[str]] = None,
                 storage_endpoint: Optional[pulumi.Input[str]] = None,
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
            __props__ = ServerSecurityAlertPolicyArgs.__new__(ServerSecurityAlertPolicyArgs)

            __props__.__dict__["disabled_alerts"] = disabled_alerts
            __props__.__dict__["email_account_admins"] = email_account_admins
            __props__.__dict__["email_addresses"] = email_addresses
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            __props__.__dict__["retention_days"] = retention_days
            if server_name is None and not opts.urn:
                raise TypeError("Missing required property 'server_name'")
            __props__.__dict__["server_name"] = server_name
            if state is None and not opts.urn:
                raise TypeError("Missing required property 'state'")
            __props__.__dict__["state"] = state
            __props__.__dict__["storage_account_access_key"] = storage_account_access_key
            __props__.__dict__["storage_endpoint"] = storage_endpoint
        super(ServerSecurityAlertPolicy, __self__).__init__(
            'azure:mssql/serverSecurityAlertPolicy:ServerSecurityAlertPolicy',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            disabled_alerts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            email_account_admins: Optional[pulumi.Input[bool]] = None,
            email_addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            retention_days: Optional[pulumi.Input[int]] = None,
            server_name: Optional[pulumi.Input[str]] = None,
            state: Optional[pulumi.Input[str]] = None,
            storage_account_access_key: Optional[pulumi.Input[str]] = None,
            storage_endpoint: Optional[pulumi.Input[str]] = None) -> 'ServerSecurityAlertPolicy':
        """
        Get an existing ServerSecurityAlertPolicy resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] disabled_alerts: Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        :param pulumi.Input[bool] email_account_admins: Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] email_addresses: Specifies an array of email addresses to which the alert is sent.
        :param pulumi.Input[str] resource_group_name: The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[int] retention_days: Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        :param pulumi.Input[str] server_name: Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        :param pulumi.Input[str] state: Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        :param pulumi.Input[str] storage_account_access_key: Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        :param pulumi.Input[str] storage_endpoint: Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ServerSecurityAlertPolicyState.__new__(_ServerSecurityAlertPolicyState)

        __props__.__dict__["disabled_alerts"] = disabled_alerts
        __props__.__dict__["email_account_admins"] = email_account_admins
        __props__.__dict__["email_addresses"] = email_addresses
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["retention_days"] = retention_days
        __props__.__dict__["server_name"] = server_name
        __props__.__dict__["state"] = state
        __props__.__dict__["storage_account_access_key"] = storage_account_access_key
        __props__.__dict__["storage_endpoint"] = storage_endpoint
        return ServerSecurityAlertPolicy(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="disabledAlerts")
    def disabled_alerts(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Specifies an array of alerts that are disabled. Allowed values are: `Sql_Injection`, `Sql_Injection_Vulnerability`, `Access_Anomaly`, `Data_Exfiltration`, `Unsafe_Action`.
        """
        return pulumi.get(self, "disabled_alerts")

    @property
    @pulumi.getter(name="emailAccountAdmins")
    def email_account_admins(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean flag which specifies if the alert is sent to the account administrators or not. Defaults to `false`.
        """
        return pulumi.get(self, "email_account_admins")

    @property
    @pulumi.getter(name="emailAddresses")
    def email_addresses(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Specifies an array of email addresses to which the alert is sent.
        """
        return pulumi.get(self, "email_addresses")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group that contains the MS SQL Server. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="retentionDays")
    def retention_days(self) -> pulumi.Output[Optional[int]]:
        """
        Specifies the number of days to keep in the Threat Detection audit logs. Defaults to `0`.
        """
        return pulumi.get(self, "retention_days")

    @property
    @pulumi.getter(name="serverName")
    def server_name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the MS SQL Server. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "server_name")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        Specifies the state of the policy, whether it is enabled or disabled or a policy has not been applied yet on the specific database server. Allowed values are: `Disabled`, `Enabled`.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="storageAccountAccessKey")
    def storage_account_access_key(self) -> pulumi.Output[Optional[str]]:
        """
        Specifies the identifier key of the Threat Detection audit storage account. This is mandatory when you use `storage_endpoint` to specify a storage account blob endpoint.
        """
        return pulumi.get(self, "storage_account_access_key")

    @property
    @pulumi.getter(name="storageEndpoint")
    def storage_endpoint(self) -> pulumi.Output[Optional[str]]:
        """
        Specifies the blob storage endpoint (e.g. https://example.blob.core.windows.net). This blob storage will hold all Threat Detection audit logs.
        """
        return pulumi.get(self, "storage_endpoint")

