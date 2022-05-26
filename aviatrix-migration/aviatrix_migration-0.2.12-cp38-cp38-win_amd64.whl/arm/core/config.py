# -*- coding: utf-8 -*-
"""Configuration options for Azure discovery migration."""
import ipaddress
import json
import pathlib
import typing as t

import yaml
from pydantic import constr  # Constrained string type.
from pydantic import Field, ValidationError, validator, root_validator

from dm.core.config import BackupConfig, CIDRList, Tags, _BaseModel, _str

if not hasattr(t, "Literal"):
    from typing_extensions import Literal

    t.Literal = Literal


AzureRegionName = t.Literal[
    "westus",
    "eastus",
    "centralus",
    "westus2",
    "northeurope",
    "westeurope",
    "southeastasia",
    "japaneast",
    "chinaeast2",
    "chinanorth2",
]
CleanupResources = t.Literal[
    "PEERING",
    "VNG_ER",
]


def _default_network() -> CIDRList:
    return [ipaddress.IPv4Network("0.0.0.0/0")]

class TfControllerAccessConfig(_BaseModel):
    """
    Attributes:
        mode: if "ENV" is used, AVIATRIX_USERNAME and AVIATRIX_PASSWORD should be set for terraform use.
    """
    alias: _str = "us_west_2"
    mode: t.Literal["ENV", "SSM"] = "ENV"
    region: _str = "us-west-2"
    password_store: _str = "avx-admin-password"
    ssm_role: _str = ""
    username: _str = "admin"
    account_id: constr(strip_whitespace=True, regex=r"^[0-9]*$") = ""

    @root_validator(pre=True)
    def check_mode(cls, values):
        """
        Avoid confusion, do not allow other attributes if ENV is used.
        """
        if 'mode' in values and values['mode'] == "ENV":
            if len(values) > 1:
                lvalues = dict(values)
                del lvalues['mode']
                raise ValueError(
                    f"When aviatrix.tf_controller_access.mode is 'ENV', "
                    f"the following attribute(s) {lvalues} should be removed."
                )

        # if ssm_role is defined, account_id is mandatory
        if 'mode' in values and values['mode'] == "SSM":
            if 'ssm_role' in values and len(values["ssm_role"]) > 0 and \
                (not 'account_id' in values or not len(values["account_id"]) > 0):
                raise ValueError(
                    f"missing account_id"
                )
        return values

class TfCloudConfig(_BaseModel):
    organization: t.Optional[_str] = None
    workspace_name: t.Optional[_str] = None
    tags: t.Optional[t.List[_str]] = None

    @root_validator(pre=True)
    def check_required_attributes(cls, values):
        """
        check required attributes are there:
        - organization attribute is mandatory;
        - only one of workspace_name and tags attributes is allowed and required.
        check if
        """
        if "organization" not in values or not values["organization"]:
            raise ValueError("Missing organization name")
        if "workspace_name" not in values and "tags" not in values:
            raise ValueError(
                "Required workspace_name or tags atttribute to be defined"
            )
        if "workspace_name" in values and "tags" in values:
            raise ValueError("Either workspace_name or tags is allowed")
        return values

    @validator ("workspace_name")
    def check_not_empty(cls, val):
        if not val:
            raise ValueError("Missing workspace_name")            
        return val

    @validator("tags")
    def check_and_rewrite_tags(cls, v):
        """
        1. If tags list is empty, raise error
        2. Convert input tags (list of string), e.g., ['abc', 'dec'] into
           a string tags with double quote, e.g., '["abc", "dec"]'.
           This will facilitate terraform tags generation, which requires a list
           of double quote string.

           Performing the conversion here seems to be pretty clean; otherwise,
           it can be done inside common.readGlobalConfigOption.

           *** Of course, we are changing the tags type in such conversion,
           *** seems to be allowed by pydantic.
        """
        if v == None:
            raise ValueError("Empty tag not allowed")

        if len(v) == 0:
            raise ValueError("tags list cannot be empty")

        if not all([x for x in v ]):
            raise ValueError("Empty tag not allowed")

        return json.dumps(v)


class TerraformConfig(_BaseModel):
    """Terraform configuration.

    Attributes:
        terraform_output: Absolute path to the TF files created.
        terraform_version: Terraform version in terraform version syntax
        aviatrix_provider: Aviatrix terraform provider version in
            terraform version syntax
        aws_provider: AWS terraform provider version in terraform version syntax
        enable_s3_backend: Generate terraform S3 backend config.
            Default to True.
        module_source:  Override the module source in `vpc.tf`. If this is
            omitted or "", we use the included TF module source.
            Defaults to "".
    """

    DEFAULT_MODULE_SOURCE: t.ClassVar[_str] = "../module_azure_brownfield_spoke_vnet"

    regenerate_common_tf: bool = True
    account_folder: t.Literal["name", "id"] = "id"
    terraform_output: _str
    terraform_version: _str  # = ">= 0.14"
    aviatrix_provider: _str  # "= 2.19.3"
    aws_provider: _str  # "~> 3.43.0"
    arm_provider: _str  # "~> 2.89.0"
    enable_s3_backend: bool = False
    module_source: t.Optional[_str] = DEFAULT_MODULE_SOURCE
    tf_cloud: t.Optional[TfCloudConfig] = None

    @validator("tf_cloud")
    def check_tfcloud_for_none(cls, val, values):
        """
        handle tfcloud None case where none of its attributes are defined.
        """
        if val is None:
            raise ValueError("missing organization, workspace_name, tags attributes")
        return val


class AviatrixConfig(_BaseModel):
    """Aviatrix config for onboarding.

    Attributes:
        controller_ip: Aviatrix controller IP address.
        tf_controller_access: terraform attributes for accessing controller password, via AWS SSM or ENV
    """

    controller_ip: ipaddress.IPv4Address
    tf_controller_access: TfControllerAccessConfig = Field(default_factory=TfControllerAccessConfig)


class AlertConfig(_BaseModel):
    """Alert configuration."""

    vnet_name_length: int = 31
    vnet_peering: bool = True
    vcpu_limit: bool = True  # Requires Microsoft.Capacity registration, see README


class ScriptConfig(_BaseModel):
    """Configuration for script features.

    Attributes:
        allow_vnet_cidrs: List of allowed VPC CIDRs. Only the allowed CIDRs will
            be copied to vpc_cidr and passed to the brownfield spoke VPC
            terraform module. Set it to [“0.0.0.0/0”] to allow any CIDR.
        configure_gw_name:
        configure_spoke_advertisement:
        enable_spoke_egress:
        route_table_tags: List of tags to be added to the route table(s). Omit
            this section if no tags required.
            Defaults to [].
        subnet_tags: List of tags to be added to the subnet(s). Omit this
            section if no tags required.
            Defaults to [].
    """

    allow_vnet_cidrs: CIDRList = Field(default_factory=_default_network)
    configure_gw_name: bool = True
    configure_spoke_advertisement: bool = False
    # enable_spoke_egress: bool = False
    route_table_tags: Tags = Field(default_factory=list)
    # subnet_tags: Tags = Field(default_factory=list)


# class TGWConfig(_BaseModel):
#     """Transit gateways.
#
#     Attributes:
#         tgw_account: TGW account number.
#         tgw_role: TGW account access role.
#         tgw_by_region: Dictionary of TGW Regions to TGW ID.
#             e.g.: {"us-east-1": "tgw-020a8339660950770"}
#     """
#
#     tgw_account: _str
#     tgw_role: _str
#     tgw_by_region: t.Dict[AzureRegionName, _str] = Field(default_factory=dict)


GWName = constr(strip_whitespace=True, max_length=29)

class VWanConfig(_BaseModel):
    subscription_id: _str
    resource_group: _str
    vhub: _str

class VNetConfig(_BaseModel):
    """Settings for VPC migration.

    Attributes:
    """

    vnet_name: _str
    avtx_cidr: _str
    use_azs: bool = True
    inspection: t.Optional[bool] = None
    spoke_advertisement: t.Optional[t.List[_str]] = None
    spoke_routes: t.Optional[CIDRList] = None
    spoke_gw_name: t.Optional[GWName] = None
    transit_gw_name: t.Optional[GWName] = None
    spoke_gw_tags: Tags = Field(default_factory=list)


class AccountInfo(_BaseModel):
    """Information about spoke VPCs.

    Attributes:
        subscription_id: Azure Subscription ID.
        account_name: Name of the VNet account owner.
        hpe: Enable high performance encryption on spoke gateways.
            Defaults to True.
        filter_cidrs: Filters out any route within specified CIDR when copying
            the route table. No need to add RFC1918 routes in the list; they
            are filtered by default. Set it to empty list [] if no filtering required.
        spoke_gw_size: Spoke gateway instance size.
        add_account:
        onboard_account:
        vnets:
    """

    subscription_id: _str
    account_name: _str
    vnets: t.List[VNetConfig]
    tf_provider_alias: t.Optional[_str] = None
    hpe: bool = True
    filter_cidrs: CIDRList = Field(default_factory=list)
    spoke_gw_size: _str = "Standard_D3_v2"
    onboard_account: bool = False
    vwan: t.Optional[VWanConfig] = None

class AzureCredentials(_BaseModel):
    """Settings used for Azure credentials."""

    arm_directory_id: _str
    arm_application_id: _str
    arm_application_secret_env: _str
    arm_application_secret_data_src: _str = "avx-azure-client-secret"
    arm_subscription_id: t.Optional[t.List[_str]]


AzureCredentialConfig = t.Dict[str, AzureCredentials]


class PrestageConfig(_BaseModel):
    """Settings used during prestage."""

    default_route_table: _str = "dummy_rt"


class SwitchTrafficConfig(_BaseModel):
    """Settings used during `switch_traffic.

    Attributes:
        transit_peerings: Dictionary of azure transit peered to aws transit
             e.g.: {"azure-transit-useast-1": "aws-transit-us-east-1"}
        default_route_table: _str
        delete_vnet_lock: bool
    """

    transit_peerings: t.Dict[_str, _str] = Field(default_factory=dict)
    delete_vnet_lock: bool = True


class CleanupConfig(_BaseModel):
    """Resources to cleanup.

    Attributes:
        delete_vnet_lock:
        resources: Delete resources like `VGW` or `VIF` in a VPC.
    """

    delete_vnet_lock: bool = True
    resources: t.List[CleanupResources] = Field(default_factory=list)


GW_NAME_KEYS = ["spoke_gw_name", "transit_gw_name"]


class DiscoveryConfiguration(_BaseModel):
    """Discovery Migration Configuration.

    Attributes:
        aviatrix: Generate terraform resource for onboarding an Aviatrix account.
        alert: Alerts configuration.
        config: Script feature configuration.
        tgw: List of TGWs used, assuming all TGWs are defining within one account.
        account_info: Spoke VPC info.
        switch_traffic: Configuration during switch_traffic.
        cleanup: Resources to cleanup.
        aws: Use AWS S3 to backup the generated account folder.
        terraform: Mark the beginning of terraform info.
    """

    label: t.Literal["AZURE", "MGMT_VNET_CIDR"]
    terraform: TerraformConfig
    aviatrix: AviatrixConfig
    azure_cred: AzureCredentialConfig
    account_info: t.List[AccountInfo]
    alert: AlertConfig = Field(default_factory=AlertConfig)
    cleanup: CleanupConfig = Field(default_factory=CleanupConfig)
    config: ScriptConfig = Field(default_factory=ScriptConfig)
    prestage: PrestageConfig = Field(default_factory=PrestageConfig)
    switch_traffic: SwitchTrafficConfig = Field(default_factory=SwitchTrafficConfig)
    aws: t.Optional[BackupConfig] = None
    # tgw: t.Optional[TGWConfig] = None

    @validator("config")
    def check_gw_names(cls, val, values):
        """Validate gateway names.

        Args:
            val: The account_info dictionary.
            values: All values passed to DiscoveryConfiguration init.

        returns:
            The account_info dictionary.
        """
        config = val
        errors = []
        account_info = values.get("account_info", [])

        if config.configure_gw_name:
            for account in account_info:
                for vnet in account.vnets:
                    if any(getattr(vnet, key) is None for key in GW_NAME_KEYS):
                        errors.append((account.subscription_id, vnet.vnet_name))
        if errors:
            error_vpc_str = "\n".join(
                f"account: {account_id}, vnet: {vnet_name}"
                for account_id, vnet_name in errors
            )
            raise ValueError(
                "'config.configure_gw_name' is True, both 'spoke_gw_name' and"
                " 'transit_gw_name' must be set in all VPCs."
                "\nList of nonconforming VPCs:\n"
                f"{error_vpc_str}"
            )

        return config


def load_from_dict(config_dict: t.Dict) -> DiscoveryConfiguration:
    """Load discovery migration settings from a python dictionary.

    Args:
        config_dict: Python dictionary in which to load configuration
            settings from.

    Returns:
        Parsed discovery migration settings.
    """
    try:
        config = DiscoveryConfiguration(**config_dict)
    except ValidationError as e:
        print(e.json())
        raise SystemExit(1) from e
    return config


def dump_to_dict(config: DiscoveryConfiguration) -> t.Dict:
    """Dump discovery migration settings to a python dictionary.

    Args:
        config: Discovery migration settings.

    Returns:
        Configuration dictionary.
    """
    json_data = config.json()
    data = json.loads(json_data)

    return data


def load_from_yaml(yml_path: pathlib.Path) -> DiscoveryConfiguration:
    """Load discovery migration settings from a yaml.

    Args:
        yml_path: Path to location of discovery migration yaml.

    Returns:
        Parsed discovery migration settings.
    """
    with open(yml_path, "r") as fh:
        data = yaml.load(fh, Loader=yaml.FullLoader)

    return load_from_dict(data)


def dump_to_yaml(config: DiscoveryConfiguration, dest: pathlib.Path) -> pathlib.Path:
    """Dump discovery migration settings to a yaml file.

    Args:
        config: Discovery migration settings.
        dest: Path to destination location of discovery migration yaml.

    Returns:
        Path to destination location of discovery migration yaml.
    """
