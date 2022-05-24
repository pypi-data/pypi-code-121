from __future__ import annotations  # this means we get FutureRefs

from typing import List, Optional, TypedDict

from ..utils import validate_type


class FirewallOptions(TypedDict):
    # if there's firewall options, then ports and cidr are both required
    ports: List[int]
    cidr: str


class BackendOptions(TypedDict, total=False):
    region_name: Optional[str]
    zone_name: Optional[str]
    firewall: Optional[FirewallOptions]


class AWSOptions(BackendOptions, total=False):
    keypair_name: Optional[str]
    # future: add stuff like "spot" when supported


class GCPOptions(BackendOptions, total=False):
    worker_accelerator_count: Optional[int]
    worker_accelerator_type: Optional[str]


BackendOptionTypes = [AWSOptions, GCPOptions]


def test_aws_options_validation():
    assert validate_type(AWSOptions, AWSOptions())
    assert validate_type(AWSOptions, AWSOptions(region_name="foo", keypair_name="bar"))


def test_aws_nested_options_validation():
    assert validate_type(
        AWSOptions,
        AWSOptions(
            region_name="foo", firewall=FirewallOptions(ports=[123], cidr="0.0.0.0/0")
        ),
    )


def test_aws_dict_validation():
    assert validate_type(AWSOptions, dict())
    assert validate_type(AWSOptions, dict(region_name="foo"))


def test_aws_nested_dict_validation():
    assert validate_type(
        AWSOptions,
        dict(region_name="foo", firewall=dict(ports=[123], cidr="0.0.0.0/0")),
    )


def test_aws_invalid_options_validation():
    assert not validate_type(AWSOptions, dict(foo="foo"))
    assert not validate_type(AWSOptions, dict(region_name="foo", foo="foo"))


def test_gcp_options_validation():
    assert validate_type(GCPOptions, GCPOptions())
    assert validate_type(GCPOptions, GCPOptions(region_name="foo"))


def test_gcp_nested_options_validation():
    assert validate_type(
        GCPOptions,
        GCPOptions(
            region_name="foo", firewall=FirewallOptions(ports=[123], cidr="0.0.0.0/0")
        ),
    )

    assert not validate_type(
        GCPOptions, AWSOptions(region_name="foo", keypair_name="bar")
    )


def test_any_option_validation():
    opts = dict(region_name="foo", firewall=dict(ports=[123], cidr="0.0.0.0/0"))
    assert any((validate_type(t, opts) for t in BackendOptionTypes))

    opts = {
        "region_name": "us-east1",
        "zone_name": "us-east1-d",
        "firewall": {"ports": [8787, 8786, 22], "cidr": "0.0.0.0/0"},
    }
    assert any((validate_type(t, opts) for t in BackendOptionTypes))


def test_invalid_firewall_options_validation():
    assert not validate_type(
        AWSOptions, dict(region_name="foo", firewall=dict(cidr="0.0.0.0/0"))
    )
