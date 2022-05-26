# -*- coding: utf-8 -*-
"""Configuration options for discovery migration."""
import ipaddress
import json
import pathlib
import typing as t

import pydantic
import yaml
from pydantic import constr  # Constrained string type.
from pydantic import Field, ValidationError, root_validator, validator

if not hasattr(t, "Literal"):
    from typing_extensions import Literal

    t.Literal = Literal


RegionName = t.Literal[
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ca-central-1",
    "eu-central-1",
    "eu-north-1",
    "eu-south-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "me-south-3",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]
CleanupResources = t.Literal[
    "INTERNAL_LB",
    "NAT",
    "TGW_ATTACHMENT",
    "VGW",
]
CIDRList = t.List[ipaddress.IPv4Network]
Tag = t.Dict[str, str]
Tags = t.List[Tag]
_str = constr(strip_whitespace=True)


def _default_network() -> CIDRList:
    return [ipaddress.IPv4Network("0.0.0.0/0")]


class _BaseModel(pydantic.BaseModel):
    class Config:
        json_encoders = {
            ipaddress.IPv4Address: str,
            ipaddress.IPv4Network: str,
        }
        extra = "forbid"


class BackupConfig(_BaseModel):
    """Backup account folder.

    Uses cloud storage to backup the generated account folder.
    Omit this section if backup is not required.

    Note:
        Currently only S3 backup is supported.

    Attributes:
        s3: S3 backup configuration.
    """

    class S3Config(_BaseModel):
        """Setup S3 for storing the terraform output files.

        Attributes:
            account: S3 bucket account number.
            role_name: S3 bucket access permission.
            name: S3 bucket name.
            region: S3 bucket region.
        """

        account: _str
        role_name: _str
        name: _str
        region: _str

    s3: S3Config


class TfControllerAccessConfig(_BaseModel):
    """
    Attributes:
        mode: if "ENV" is used, AVIATRIX_USERNAME and AVIATRIX_PASSWORD should be set for terraform use.
        ssm_role: role with SSM:getParameter permission, e.g., aviatrix-role-app. If it is set to empty string,
                  NO assume_role statement is generated in the AWS provider.
    """

    alias: _str = "us_west_2"
    mode: t.Literal["ENV", "SSM"] = "ENV"
    password_store: _str = "avx-admin-password"
    region: _str = "us-west-2"
    ssm_role: _str = ""
    username: _str = "admin"

    @root_validator(pre=True)
    def check_mode(cls, values):
        """
        Avoid confusion, do not allow other attributes if ENV is used.
        """
        if "mode" in values and values["mode"] == "ENV":
            if len(values) > 1:
                lvalues = dict(values)
                del lvalues["mode"]
                raise ValueError(
                    f"When aviatrix.tf_controller_access.mode is 'ENV', "
                    f"the following attribute(s) {lvalues} should be removed."
                )

        return values


class TfCloudConfig(_BaseModel):
    organization: _str = None
    workspace_name: _str = None
    tags: t.Optional[t.List[_str]] = None

    @classmethod
    def valid_str_attribute(cls, val):
        if val is None or len(val) == 0:
            return False
        return True

    @root_validator(pre=True)
    def check_required_attributes(cls, values):
        """
        check required attributes are there:
        - organization attribute is mandatory;
        - only one of workspace_name and tags attributes is allowed and required.
        check if
        """
        if "organization" not in values or not cls.valid_str_attribute(
            values["organization"]
        ):
            raise ValueError("Missing organization name")
        if "workspace_name" not in values and "tags" not in values:
            raise ValueError(
                "Required workspace_name or tags atttribute to be defined"
            )
        if "workspace_name" in values and "tags" in values:
            raise ValueError("Either workspace_name or tags is allowed")
        if "workspace_name" in values and not cls.valid_str_attribute(
            values["workspace_name"]
        ):
            raise ValueError("Missing workspace_name")
        if "tags" in values and not all(
            [cls.valid_str_attribute(x) for x in values["tags"]]
        ):
            raise ValueError("Empty tag not allowed")
        return values

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
        if v is not None:
            if len(v) == 0:
                raise ValueError("tags list cannot be empty")
            return json.dumps(v)
        return v


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

    DEFAULT_MODULE_SOURCE: t.ClassVar[_str] = "../module_aws_brownfield_spoke_vpc"

    terraform_output: _str
    terraform_version: _str  # = ">= 0.14"
    aviatrix_provider: _str  # "= 2.19.3"
    aws_provider: _str  # "~> 3.43.0"
    enable_s3_backend: bool = False
    module_source: t.Optional[_str] = DEFAULT_MODULE_SOURCE
    tf_cloud: TfCloudConfig = None

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
        controller_account: The AWS Account # where the controller resides.
        ctrl_role_app: Controller app role name in the SPOKE account.
        ctrl_role_ec2: Controller EC2 role name in the CONTROLLER account
        gateway_role_app: Gateway role name in the SPOKE account
        gateway_role_ec2: Gateway instance profile name in the SPOKE account
        tf_controller_access: terraform attributes for accessing controller password, via AWS SSM or ENV
    """

    controller_ip: ipaddress.IPv4Address
    controller_account: _str
    ctrl_role_app: _str = "aviatrix-role-app"
    ctrl_role_ec2: _str = "aviatrix-role-ec2"
    gateway_role_app: _str = "aviatrix-role-app"
    gateway_role_ec2: _str = "aviatrix-role-ec2"
    tf_controller_access: TfControllerAccessConfig = Field(
        default_factory=TfControllerAccessConfig
    )


class AlertConfig(_BaseModel):
    """Alert configuration.

    Attributes:
        expect_dest_cidrs: Alert IP not fall within the given CIDR list. Turn
            off this alert using [“0.0.0.0/0”].
        expect_vpc_prefixes: Alert VPC prefix not fall within given CIDR
            ranges. Turn off this alert using [“0.0.0.0/0”].
    """

    expect_dest_cidrs: CIDRList = Field(default_factory=_default_network)
    expect_vpc_prefixes: CIDRList = Field(default_factory=_default_network)


class SnatPoliciesConfig(_BaseModel):
    src_ip: _str = None
    connection: _str = None
    new_src_ip: _str = None
    protocol: _str = "all"


class ScriptConfig(_BaseModel):
    """Configuration for script features.

    Attributes:
        add_vpc_cidr:
        allow_vpc_cidrs: List of allowed VPC CIDRs. Only the allowed CIDRs will
            be copied to vpc_cidr and passed to the brownfield spoke VPC
            terraform module. Set it to [“0.0.0.0/0”] to allow any CIDR.
        configure_gw_name:
        configure_spoke_advertisement:
        enable_spoke_egress:
        filter_tgw_attachment_subnet: enable tgw attachment subnet filtering.
            Skip subnet used by TGW vpc attachement.
        route_table_tags: List of tags to be added to the route table(s). Omit
            this section if no tags required.
            Defaults to [].
        subnet_tags: List of tags to be added to the subnet(s). Omit this
            section if no tags required.
            Defaults to [].
    """

    add_vpc_cidr: bool = True
    allow_vpc_cidrs: CIDRList = Field(default_factory=_default_network)
    configure_gw_name: bool = True
    configure_spoke_advertisement: bool = False
    enable_spoke_egress: bool = False
    filter_tgw_attachment_subnet: bool = False
    route_table_tags: Tags = Field(default_factory=list)
    subnet_tags: Tags = Field(default_factory=list)
    snat_policies: t.List[SnatPoliciesConfig] = []


class TGWConfig(_BaseModel):
    """Transit gateways.

    Attributes:
        tgw_account: TGW account number.
        tgw_role: TGW account access role.
        tgw_by_region: Dictionary of TGW Regions to TGW ID.
            e.g.: {"us-east-1": "tgw-020a8339660950770"}
    """

    tgw_account: _str
    tgw_role: _str
    tgw_by_region: t.Dict[RegionName, _str] = Field(default_factory=dict)


GWName = constr(strip_whitespace=True, max_length=29)


class VPCConfig(_BaseModel):
    """Settings for VPC migration.

    Attributes:
        vpc_id: VPC ID to be migrated
        avtx_cidr: Sets the Aviatrix CIDR used in `vpc-id.tf`.
        gw_zones: Zone letters to deploy spoke gateways in. Discovery will
            deduce the zones if an empty list [] is used.
            Defaults to [].
        spoke_gw_tags: A list of tags applied to the spoke gateway.
        domain:
        encrypt:
        inspection:
        spoke_advertisement:
        spoke_routes:
        spoke_gw_name: Name of the spoke gateway.
        transit_gw_name: Name of the transit gateway.
    """

    vpc_id: _str
    avtx_cidr: _str
    gw_zones: t.List[_str] = Field(default_factory=list)
    spoke_gw_tags: Tags = Field(default_factory=list)
    domain: t.Optional[_str] = None
    encrypt: t.Optional[bool] = None
    inspection: t.Optional[bool] = None
    spoke_advertisement: t.Optional[t.List[_str]] = None
    spoke_routes: t.Optional[CIDRList] = None
    spoke_gw_name: t.Optional[GWName] = None
    transit_gw_name: t.Optional[GWName] = None
    enable_spoke_egress: t.Optional[bool] = None


class Region(_BaseModel):
    """Region config container.

    Attributes:
        region: Name of the region.
        vpcs: List of vpcs in the region.
    """

    region: RegionName
    vpcs: t.List[VPCConfig]


class AccountInfo(_BaseModel):
    """Information about spoke VPCs.

    Attributes:
        account_id: AWS Account number.
        account_name: Name of the VPC account owner.
        hpe: Enable high performance encryption on spoke gateways.
            Defaults to True.
        managed_tgw:
        filter_cidrs: Filters out any route within specified CIDR when copying
            the route table. No need to add RFC1918 routes in the list; they
            are filtered by default. Set it to empty list [] if no filtering required.
        spoke_gw_size: Spoke gateway instance size.
        role_name: IAM role assumed to execute API calls.
        add_account:
        onboard_account:
        regions: Dictionary of region names to a list of VPC configurations.
    """

    account_id: constr(strip_whitespace=True, regex=r"^[0-9]+$")  # noqa: F722
    account_name: _str
    regions: t.List[Region]
    hpe: bool = True
    managed_tgw: bool = False
    filter_cidrs: CIDRList = Field(default_factory=list)
    spoke_gw_size: _str = "t3.micro"
    role_name: _str = "aviatrix-role-app"
    add_account: bool = False
    onboard_account: bool = False
    enable_spoke_egress: bool = False


class SwitchTrafficConfig(_BaseModel):
    """Settings used during `switch_traffic.

    Attributes:
        delete_tgw_route_delay: Specifiy the delay between
            spoke-gw-advertize-cidr and tgw-route-removal in seconds.
            Defaults to 5.
    """

    delete_tgw_route_delay: _str = "5"


class CleanupConfig(_BaseModel):
    """Resources to cleanup.

    Attributes:
        vpc_cidrs: CIDR's to be deleted from VPC.
        resources: Delete resources like `VGW`, `TGW_ATTACHMENT`, 'NAT' in a VPC.
    """

    vpc_cidrs: CIDRList = Field(default_factory=list)
    resources: t.List[CleanupResources] = Field(default_factory=list)
    report_only: bool = False


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

    terraform: TerraformConfig
    aviatrix: AviatrixConfig
    account_info: t.List[AccountInfo]
    alert: AlertConfig = Field(default_factory=AlertConfig)
    cleanup: CleanupConfig = Field(default_factory=CleanupConfig)
    config: ScriptConfig = Field(default_factory=ScriptConfig)
    switch_traffic: SwitchTrafficConfig = Field(default_factory=SwitchTrafficConfig)
    aws: t.Optional[BackupConfig] = None
    tgw: t.Optional[TGWConfig] = Field(default_factory=dict)

    @validator("tgw")
    def check_tgw_for_none(cls, val, values):
        """
        handle tgw None case where none of its attributes are defined.
        """
        if val is None:
            raise ValueError(
                "missing tgw_account, tgw_role and tgw_by_region attributes"
            )
        return val

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
                for region in account.regions:
                    for vpc in region.vpcs:
                        if any(getattr(vpc, key) is None for key in GW_NAME_KEYS):
                            errors.append(
                                (account.account_id, region.region, vpc.vpc_id)
                            )
        if errors:
            error_vpc_str = "\n".join(
                f"account: {account_id}, region: {region}, vpc: {vpc_id}"
                for account_id, region, vpc_id in errors
            )
            raise ValueError(
                f"'config.configure_gw_name' is {config.configure_gw_name}, "
                "both 'spoke_gw_name' and 'transit_gw_name' must be set in all VPCs."
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
