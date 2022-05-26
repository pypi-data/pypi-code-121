import sys
from typing import Tuple

import aiohttp
import pytest
from coiled.exceptions import (
    AccountFormatError,
    CidrInvalidError,
    GPUTypeError,
    ParseIdentifierError,
    PortValidationError,
)
from coiled.utils import (
    bytes_to_mb,
    get_account_membership,
    get_platform,
    handle_credentials,
    has_program_quota,
    is_gcp,
    normalize_server,
    parse_backend_options,
    parse_gcp_region_zone,
    parse_identifier,
    parse_requested_memory,
    parse_wait_for_workers,
    validate_account,
    validate_cidr_block,
    validate_gpu_type,
    validate_ports,
)


@pytest.mark.parametrize(
    "identifier,expected",
    [
        ("coiled/xgboost:1efd34", ("coiled", "xgboost", "1efd34")),
        ("xgboost:1efd34", (None, "xgboost", "1efd34")),
        ("coiled/xgboost", ("coiled", "xgboost", None)),
        ("xgboost", (None, "xgboost", None)),
        ("coiled/xgboost-py37", ("coiled", "xgboost-py37", None)),
        ("xgboost_py38", (None, "xgboost_py38", None)),
    ],
)
def test_parse_good_names(identifier, expected: Tuple[str, str]):
    account, name, revision = parse_identifier(
        identifier, property_name="name_that_would_be_printed_in_error"
    )
    assert (account, name, revision) == expected


@pytest.mark.parametrize(
    "identifier",
    [
        "coiled/dan/xgboost",
        "coiled/dan?xgboost",
        "dan\\xgboost",
        "jimmy/xgbóst",
        "My-Test-Env",
        "My Test Env",
        "coiled/My-Test-Env:abc123",
        "coiled/my-test-env!",
        "Coiled/my-test-env",
        "",
    ],
)
def test_parse_bad_names(identifier):
    with pytest.raises(ParseIdentifierError, match="software_environment"):
        parse_identifier(identifier, property_name="software_environment")


def test_parse_cluster_uppercase_names():
    cluster_name = "BobTheBuilder-1j850d-b"
    account, name, revision = parse_identifier(cluster_name, allow_uppercase=True)

    assert name == cluster_name
    assert account is None
    assert revision is None


def test_get_platform(monkeypatch):
    with monkeypatch.context() as m:
        monkeypatch.setattr(sys, "platform", "linux")
        assert get_platform() == "linux"

    with monkeypatch.context() as m:
        m.setattr(sys, "platform", "darwin")
        assert get_platform() == "osx"

    with monkeypatch.context() as m:
        m.setattr(sys, "platform", "win32")
        assert get_platform() == "windows"

    with monkeypatch.context() as m:
        m.setattr(sys, "platform", "bad-platform")
        with pytest.raises(ValueError) as result:
            assert get_platform() == "windows"

        err_msg = str(result).lower()
        assert "invalid" in err_msg
        assert "bad-platform" in err_msg


def test_normalize_server():
    assert normalize_server("http://beta.coiledhq.com") == "https://cloud.coiled.io"
    assert normalize_server("https://beta.coiled.io") == "https://cloud.coiled.io"


def test_get_account_membership():

    assert get_account_membership({}, account=None) is None

    response = {"membership_set": []}
    assert get_account_membership(response, account=None) is None

    membership = {
        "account": {"slug": "coiled"},
    }
    response = {"membership_set": [membership], "username": "not-coiled"}
    assert get_account_membership(response, account="coiled") == membership
    assert get_account_membership(response, account="test_user") != membership

    response["username"] = "coiled"
    assert get_account_membership(response) == membership


def test_get_account_membership_uppercase_account():

    assert get_account_membership({}, account=None) is None

    response = {"membership_set": []}
    assert get_account_membership(response, account=None) is None

    membership = {
        "account": {"slug": "coiled"},
    }
    response = {"membership_set": [membership], "username": "not-coiled"}
    assert get_account_membership(response, account="coiled") == membership
    assert get_account_membership(response, account="test_user") != membership

    response["username"] = "Coiled"
    assert get_account_membership(response) == membership


def test_has_program_quota():
    assert has_program_quota({}) is False

    membership = {"account": {"active_program": {"has_quota": True}}}
    assert has_program_quota(membership) is True


def test_gcp_region_zone():
    region, zone = parse_gcp_region_zone(region="us-central1")

    assert region == "us-central1"
    assert zone == "us-central1-c"

    region, zone = parse_gcp_region_zone(zone="us-east1-c")

    assert region == "us-east1"
    assert zone == "us-east1-c"

    region, zone = parse_gcp_region_zone(region="test-region", zone="test-zone")

    assert region == "test-region"
    assert zone == "test-zone"

    region, zone = parse_gcp_region_zone(region="us-central1", zone="b")

    assert region == "us-central1"
    assert zone == "us-central1-b"

    region, zone = parse_gcp_region_zone(zone="a")

    assert region == "us-east1"
    assert zone == "us-east1-a"


def test_validate_gpu_type():
    is_valid = validate_gpu_type("nvidia-tesla-t4")
    assert is_valid

    with pytest.raises(GPUTypeError) as e:
        validate_gpu_type("T100")

    assert "GPU type 'T100' is not a supported GPU type" in e.value.args[0]


@pytest.mark.parametrize(
    "account,backend,provider_name,expected",
    [
        ("alice", "vm_gcp", "gcp", True),
        ("alice", "vm", "gcp", True),
        ("alice", "vm_aws", "aws", False),
        ("alice", "vm", "aws", False),
    ],
)
def test_is_gcp(account, backend, provider_name, expected):
    accounts = {
        "alice": {"backend": backend, "options": {"provider_name": provider_name}}
    }
    assert is_gcp(account, accounts) == expected


@pytest.mark.parametrize(
    "backend_options,account,backend,provider_name,worker_gpu,expected",
    [
        ({"preemptible": False}, "alice", "vm_gcp", "gcp", None, {"spot": False}),
        ({"preemptible": False}, "alice", "vm", "aws", None, {"preemptible": False}),
        ({"preemptible": False}, "bob", "vm", "gcp", None, {"spot": False}),
        ({"preemptible": False}, "bob", "k8s", None, None, {"preemptible": False}),
        ({}, "bob", "k8s", None, None, {}),
        ({}, "bob", "vm", "gcp", 0, {}),
        ({}, "bob", "vm", "gcp", 1, {"spot": False}),
    ],
)
def test_parse_backend_options(
    backend_options, account, backend, provider_name, worker_gpu, expected
):
    accounts = {"alice": {"backend": backend}, "bob": {"backend": backend}}
    if provider_name is not None:
        accounts["alice"]["options"] = {"provider_name": provider_name}
        accounts["bob"]["options"] = {"provider_name": provider_name}
    parsed_backend_options = parse_backend_options(
        backend_options, account, accounts, worker_gpu
    )
    assert parsed_backend_options == expected


@pytest.mark.parametrize(
    "backend_options,account,backend,provider_name,worker_gpu,expected",
    [
        (
            {"firewall": {"ports": [12, 34, 59]}},
            "alice",
            "vm_gcp",
            "gcp",
            None,
            {"firewall": {"ports": [12, 34, 59]}},
        ),
        (
            {"firewall": {"cidr": "0.1.2.3/45"}},
            "bobthebuilder",
            "vm",
            "aws",
            None,
            {"firewall": {"cidr": "0.1.2.3/45"}},
        ),
    ],
)
def test_parse_backend_options_firewall(
    backend_options, account, backend, provider_name, worker_gpu, expected
):
    accounts = {
        "alice": {"backend": backend},
        "hi!": {"backend": backend},
        "bobthebuilder": {"backend": backend},
    }
    parsed_backend_options = parse_backend_options(
        backend_options, account, accounts, worker_gpu
    )
    assert parsed_backend_options == expected


@pytest.mark.parametrize(
    "backend_options,account,backend,provider_name,worker_gpu",
    [
        (
            {"firewall": {"ports": "12,45,67"}},
            "alice",
            "vm_gcp",
            "gcp",
            None,
        ),
        (
            {"firewall": {"ports": [12, 345, "hi"]}},
            "bobthebuilder",
            "vm",
            "aws",
            None,
        ),
    ],
)
def test_parse_backend_options_firewall_port_validation_raises(
    backend_options, account, backend, provider_name, worker_gpu
):
    accounts = {
        "alice": {"backend": backend},
        "hi!": {"backend": backend},
        "bobthebuilder": {"backend": backend},
    }
    with pytest.raises(PortValidationError):
        parse_backend_options(backend_options, account, accounts, worker_gpu)


@pytest.mark.parametrize(
    "backend_options,account,backend,provider_name,worker_gpu",
    [
        (
            {"firewall": {"cidr": "1234.1.0.0/0"}},
            "alice",
            "vm_gcp",
            "gcp",
            None,
        ),
        (
            {"firewall": {"cidr": "1"}},
            "bobthebuilder",
            "vm",
            "aws",
            None,
        ),
    ],
)
def test_parse_backend_options_firewall_cidr_validation_raises(
    backend_options, account, backend, provider_name, worker_gpu
):
    accounts = {
        "alice": {"backend": backend},
        "hi!": {"backend": backend},
        "bobthebuilder": {"backend": backend},
    }
    with pytest.raises(CidrInvalidError):
        parse_backend_options(backend_options, account, accounts, worker_gpu)


@pytest.mark.parametrize(
    "cidr",
    [
        "1",
        "12.12.0/1",
        "0 0 0 0/0",
        "2364.985.1.0/193",
        "0.0.0.00/1234",
    ],
)
def test_validate_cidr_block_raises(cidr):
    with pytest.raises(
        CidrInvalidError, match="CIDR block should follow the '0.0.0.0/0' pattern."
    ):
        validate_cidr_block(cidr)


@pytest.mark.parametrize(
    "cidr",
    [0, ["0.0.0.0/0"], {}, 1049032],
)
def test_validate_cidr_not_string(cidr):
    with pytest.raises(CidrInvalidError, match="CIDR needs to be of type string"):
        validate_cidr_block(cidr)


@pytest.mark.parametrize(
    "cidr",
    ["0.0.0.0/0", "123.456.789.101/112", "12.2.0.123/9", "98.1.0.9/984"],
)
def test_validate_cidr_block(cidr):
    is_valid = validate_cidr_block(cidr)

    assert is_valid


@pytest.mark.parametrize("ports", [[1, 234, 56, 9], [1], [22, 86787]])
def test_validate_ports(ports):
    is_valid = validate_ports(ports)
    assert is_valid


@pytest.mark.parametrize("ports", ["a", 123, 11.2])
def test_validate_ports_invalid(ports):
    with pytest.raises(PortValidationError):
        validate_ports(ports)


@pytest.mark.parametrize(
    "account",
    ["CapitalAccount", "ñjúnicode", "$?ac13", "test--account", "test-account-"],
)
def test_validate_account_errors(account):
    with pytest.raises(AccountFormatError, match="Bad account format"):
        validate_account(account)


@pytest.mark.parametrize(
    "account", ["capitalaccount", "good-account", "should_work_too", "mix-and_match"]
)
def test_validate_account(account):
    result = validate_account(account)
    assert result is None


@pytest.mark.parametrize(
    "n_workers, wait_for_workers,expected",
    [
        (4, False, 0),
        (200, 0.50, 100),
        (200, 50, 50),
        (10, True, 10),
        (100, 0, 0),
        (100, None, 30),
        (1, 0, 0),
        (1, 0.3, 1),
    ],
)
def test_parse_wait_for_workers(n_workers, wait_for_workers, expected):
    to_wait = parse_wait_for_workers(n_workers, wait_for_workers)
    assert to_wait == expected


@pytest.mark.parametrize(
    "n_workers, wait_for_workers,",
    [(4, 50), (200, 3.50), (200, "hi mom!"), (10, "10"), (1, -1)],
)
def test_parse_wait_for_workers_raises(n_workers, wait_for_workers):
    with pytest.raises(ValueError, match="Received invalid value"):
        parse_wait_for_workers(n_workers, wait_for_workers)


@pytest.mark.parametrize(
    "memory, min_memory, expected",
    [
        (["12 Gib", "16 Gib"], None, {"memory__gte": 11468, "memory__lte": 18898}),
        ("12 Gib", None, {"memory__gte": 11468, "memory__lte": 14173}),
        (None, "18 Gib", {"memory__gte": 19327}),
        (24e9, None, {"memory__gte": 21360, "memory__lte": 26400}),
        (24000000000, None, {"memory__gte": 21360, "memory__lte": 26400}),
        (None, 24e9, {"memory__gte": 24000}),
        # If both `memory` annd `min_memory` is used, we use memory
        (["1Gib", "8 GiB"], "5 Gib", {"memory__gte": 956, "memory__lte": 9449}),
    ],
)
def test_parse_requested_memory(memory, min_memory, expected):
    parsed_memory = parse_requested_memory(memory, min_memory)

    assert parsed_memory == expected


@pytest.mark.parametrize(
    "bytes, expected",
    [(24000000000, 24000), (24000000000.0, 24000), (-24000000000, 24000)],
)
def test_bytes_to_mb(bytes, expected):
    assert bytes_to_mb(bytes) == expected


@pytest.mark.asyncio
async def test_handle_credentials(mocker):
    aiohttp_error = aiohttp.ContentTypeError(None, None)  # type: ignore
    bad_request = mocker.AsyncMock()
    bad_request.status = 502
    bad_request.json = mocker.AsyncMock(side_effect=aiohttp_error)

    good_request = mocker.AsyncMock()
    good_request.status = 202
    good_request.json = mocker.AsyncMock()
    good_request.json.return_value = {
        "id": 0,
        "username": "bobthebuilder",
        "email": "bob@bob.io",
        "first_name": "",
        "last_name": "",
        "membership_set": [
            {
                "is_admin": True,
                "account": {
                    "can_use_gpus": False,
                    "backend": "vm_aws",
                    "coiled_rate": 100,
                    "environment_variables": {},
                    "members_limit": 1,
                    "container_registry": {
                        "type": "ecr",
                        "has_credentials": False,
                        "public_ecr": False,
                        "region": "us-east-1",
                    },
                    "active_program": {
                        "usage_percent": 0.0,
                        "quota": 0.0,
                        "spent": 0.36,
                        "has_quota": True,
                        "start_date": "2022-02-14T13:57:41Z",
                        "end_date": "2022-03-14T13:57:41Z",
                        "tier": "enterprise",
                    },
                    "options": {"aws_region_name": "us-east-1"},
                    "id": 1,
                    "slug": "bobthebuilder",
                    "name": "bobthebuilder",
                    "limit": 150,
                    "user_limit": 150,
                    "has_quota": True,
                    "avatar_url": "",
                    "private": False,
                    "early_adopter": False,
                },
                "limit": 150,
            },
        ],
    }

    from coiled.utils import handle_credentials

    mocked_session = mocker.patch("aiohttp.ClientSession")

    mocked_session.return_value.__aenter__.return_value.request = mocker.AsyncMock(
        side_effect=[bad_request, good_request]
    )

    credentials = await handle_credentials(token="123", save=False)

    assert "bobthebuilder" in credentials
    assert "123" in credentials


@pytest.mark.asyncio
async def test_handle_credentials_no_username(mocker):
    request = mocker.AsyncMock()
    request.status = 202
    request.json = mocker.AsyncMock(return_value={})

    mocked_session = mocker.patch("aiohttp.ClientSession")

    mocked_session.return_value.__aenter__.return_value.request = mocker.AsyncMock(
        return_value=request
    )

    with pytest.raises(ValueError, match="username"):
        await handle_credentials(token="123", save=False)
