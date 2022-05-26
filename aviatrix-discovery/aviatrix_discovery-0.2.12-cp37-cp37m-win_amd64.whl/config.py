# -*- coding: utf-8 -*-
import ipaddress
import json
import logging
import pathlib
import typing as t
from pprint import pformat

import pydantic
from pydantic import constr  # Constrained string type.
from pydantic import Field

from generator.common import serializers

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
CIDRList = t.List[ipaddress.IPv4Network]
Tag = t.Dict[str, str]
Tags = t.List[Tag]
_str = constr(strip_whitespace=True)

log = logging.getLogger(__name__)


def _default_network() -> CIDRList:
    return [ipaddress.IPv4Network("0.0.0.0/0")]


class _BaseModel(pydantic.BaseModel):
    class Config:
        json_encoders = {
            ipaddress.IPv4Address: str,
            ipaddress.IPv4Network: str,
        }


class ControllerConfig(_BaseModel):
    ip: ipaddress.IPv4Address
    username: _str


class DefaultsConfig(_BaseModel):
    """The defaults settings for Accounts and VPCs.

    Attributes:
        add_vpc_cidr:
        hpe: Enable high performance encryption on spoke gateways.
            Defaults to True.
        managed_tgw:
        filter_cidrs: Filters out any route within specified CIDR when copying
            the route table. No need to add RFC1918 routes in the list; they
            are filtered by default. Set it to empty list [] if no filtering required.
        spoke_gw_size: Spoke gateway instance size.
        role_name: IAM role assumed to execute API calls.
        gw_zones: Zone letters to deploy spoke gateways in. Discovery will
            deduce the zones if an empty list [] is used.
            Defaults to [].
        spoke_gw_tags: A list of tags applied to the spoke gateway.
        domain:
        encrypt:
        inspection:
        transit_gw_name: Name of the transit gateway.
    """

    add_vpc_cidr: bool = True
    hpe: bool = True
    role_name: _str = "aviatrix-role-app"
    filter_cidrs: t.Optional[CIDRList] = None
    gw_zones: t.Optional[t.List[_str]] = None
    managed_tgw: t.Optional[bool] = None
    spoke_gw_size: t.Optional[_str] = None
    domain: t.Optional[_str] = None
    encrypt: t.Optional[bool] = None
    inspection: t.Optional[bool] = None
    transit_gw_name: t.Optional[bool] = None


class GeneratorConfig(_BaseModel):
    """Settings for generating a discovery config."""

    account_ids: t.List[constr(strip_whitespace=True, regex=r"^[0-9]+$")]  # noqa: F722
    controller: ControllerConfig
    aws_regions: t.Optional[t.List[RegionName]] = None
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)


def load_from_dict(config_dict: t.Dict) -> GeneratorConfig:
    """Load discovery generation settings from a python dictionary.

    Args:
        config_dict: Python dictionary in which to load configuration
            settings from.

    Returns:
        Parsed discovery generator settings.
    """
    return GeneratorConfig(**config_dict)


def export_to_dict(config: GeneratorConfig) -> t.Dict:
    """Export discovery generator settings to a python dictionary.

    Args:
        config: Discovery generator settings.

    Returns:
        Configuration dictionary.
    """
    json_data = config.json()
    data = json.loads(json_data)

    return data


def load_config(path: pathlib.Path) -> GeneratorConfig:
    """Load discovery generator settings from a file.

    Args:
        path: Path to location of discovery generator yaml.

    Returns:
        Parsed discovery generator settings.
    """
    log.debug("Loading config from '%s'", path)
    data = serializers.load_from_path(path)
    log.debug("Configuration dictionary:\n%s", pformat(data))

    config = load_from_dict(data)
    log.debug("Parsed configuration:\n%s", pformat(config.dict()))
    return config


def export_config(config: GeneratorConfig, dest_path: pathlib.Path) -> None:
    """Export discovery generator settings to a file.

    Args:
        config: Discovery generator settings.
        dest_path: Path to destination location of discovery generator yaml.

    Returns:
        Path to destination location of discovery generator settings file.
    """
    config_dict = export_to_dict(config)
    serializers.export_to_path(config_dict, dest_path)
