from __future__ import annotations

from os import environ
from typing import Dict, Optional, Tuple
from unittest import mock

import coiled
import dask
import pytest
import structlog
from coiled.core import Cloud, _parse_gcp_creds
from coiled.exceptions import (
    AccountConflictError,
    AWSCredentialsParameterError,
    GCPCredentialsError,
    GCPCredentialsParameterError,
    RegistryParameterError,
    UnsupportedBackendError,
)
from django.conf import settings

from api_tokens.models import ApiToken
from backends import types
from backends.utils import parse_gcp_location
from software_environments.type_defs import ContainerRegistryType

from ..errors import ServerError
from ..exceptions import ParseIdentifierError

pytestmark = [
    pytest.mark.django_db(transaction=True),
]

logger = structlog.get_logger(__name__)

DASKDEV_IMAGE = environ.get("DASKDEV_IMAGE", "daskdev/dask:latest")
DASKDEV_IMAGE = "daskdev/dask:latest"


@pytest.mark.asyncio
async def test_version_error(
    base_user, remote_access_url, monkeypatch, base_user_token
):
    with dask.config.set(
        {
            "coiled.user": base_user.user.username,
            "coiled.token": base_user_token,
            "coiled.server": remote_access_url,
            "coiled.account": base_user.account.name,
            "coiled.no-minimum-version-check": False,
        }
    ):
        monkeypatch.setattr(coiled.core, "COILED_VERSION", "0.0.14")
        with pytest.raises(ServerError, match="Coiled now requires"):
            async with coiled.Cloud(asynchronous=True):
                pass


@pytest.mark.asyncio
async def test_basic(sample_user):
    async with coiled.Cloud(
        asynchronous=True,
    ) as cloud:

        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts
        assert cloud.default_account == sample_user.user.username


@pytest.mark.asyncio
async def test_trailing_slash(remote_access_url, sample_user):
    async with coiled.Cloud(
        server=remote_access_url + "/",
        asynchronous=True,
    ):
        pass


@pytest.mark.asyncio
async def test_server_input(remote_access_url, sample_user):
    async with coiled.Cloud(
        server=remote_access_url.split("://")[-1],
        asynchronous=True,
    ) as cloud:
        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts
        assert cloud.default_account == sample_user.user.username


@pytest.mark.asyncio
async def test_informative_error_org(remote_access_url, sample_user):
    with pytest.raises(PermissionError) as info:
        async with coiled.Cloud(
            server=remote_access_url.split("://")[-1],
            account="does-not-exist",
            asynchronous=True,
        ):
            pass

    assert sample_user.account.slug in str(info.value)
    assert "does-not-exist" in str(info.value)


@pytest.mark.asyncio
async def test_config(remote_access_url, sample_user, sample_user_token):
    async with coiled.Cloud(
        user=sample_user.user.username,
        token=sample_user_token,
        server=remote_access_url,
        asynchronous=True,
    ) as cloud:
        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts
        assert cloud.default_account == sample_user.user.username


def test_config_attribute():
    assert coiled.config == dask.config.get("coiled")


@pytest.mark.asyncio
async def test_repr(remote_access_url, sample_user):
    async with coiled.Cloud(asynchronous=True) as cloud:
        for func in [str, repr]:
            assert sample_user.user.username in func(cloud)
            assert remote_access_url in func(cloud)


@pytest.mark.asyncio
async def test_normalize_name(cloud, cleanup):
    assert cloud._normalize_name(name="foo/bar") == ("foo", "bar")
    assert cloud._normalize_name(name="bar") == (cloud.default_account, "bar")
    assert cloud._normalize_name(name="bar", context_account="baz") == ("baz", "bar")

    # Invalid name raises
    with pytest.raises(ParseIdentifierError):
        cloud._normalize_name(name="foo/bar/baz")

    # Will throw error if we tell it that only one
    # account makes sense.
    with pytest.raises(AccountConflictError):
        cloud._normalize_name(
            name="foo/bar", context_account="baz", raise_on_account_conflict=True
        )
    # Doesn't raise if account over-specified but there's not conflict
    assert cloud._normalize_name(
        name="foo/bar", context_account="foo", raise_on_account_conflict=True
    )


@pytest.mark.asyncio
async def test_normalize_name_uppercase_account(cloud, cleanup):
    # Users that have uppercase characters in the name will get cluster
    # name with <account>-<identifier>
    cluster_name = "BobTheBuilder-940a3351-b"
    assert cloud._normalize_name(name=cluster_name, allow_uppercase=True) == (
        cloud.default_account,
        cluster_name,
    )

    assert cloud._normalize_name(name="bar", context_account="baz") == ("baz", "bar")

    # Invalid name raises
    with pytest.raises(ParseIdentifierError):
        cloud._normalize_name(name="foo/bar/baz")

    # Will throw error if we tell it that only one
    # account makes sense.
    with pytest.raises(AccountConflictError):
        cloud._normalize_name(
            name="foo/bar", context_account="baz", raise_on_account_conflict=True
        )
    # Doesn't raise if account over-specified but there's not conflict
    assert cloud._normalize_name(
        name="foo/bar", context_account="foo", raise_on_account_conflict=True
    )


@pytest.mark.asyncio
async def test_default_account(sample_user):
    async with coiled.Cloud(
        asynchronous=True,
    ) as cloud:
        assert cloud.accounts
        assert cloud.default_account == sample_user.user.username


@pytest.mark.asyncio
async def test_cloud_repr_html(cloud, cleanup):
    text = cloud._repr_html_()
    assert cloud.user in text
    assert cloud.server in text
    assert cloud.default_account in text


@pytest.mark.asyncio
async def test_default_org_username(second_user):
    async with coiled.Cloud(asynchronous=True) as cloud:
        assert cloud.default_account == second_user.user.username


@pytest.mark.asyncio
async def test_account_config(sample_user, second_account):
    with dask.config.set({"coiled.account": second_account.account.slug}):
        async with coiled.Cloud(
            asynchronous=True,
        ) as cloud:
            assert cloud.default_account == second_account.account.slug


@pytest.mark.test_group("core-slow-group-9")
def test_public_api_software_environments(sample_user):
    results = coiled.list_software_environments()
    assert not results

    name = "foo"
    coiled.create_software_environment(name=name, container=DASKDEV_IMAGE)
    results = coiled.list_software_environments()
    assert len(results) == 1
    expected_env_name = f"{sample_user.account.name}/foo"
    assert expected_env_name in results
    assert results[expected_env_name]["container"] == DASKDEV_IMAGE

    coiled.delete_software_environment(name)
    results = coiled.list_software_environments()
    assert not results


@pytest.mark.django_db
def test_public_api_depagination_with_api_token(sample_user, software_env):

    # create 101 api tokens
    ApiToken.objects.bulk_create(
        [
            ApiToken(
                user=sample_user.user,
                token_hash="aaa",
            )
            for i in range(101)
        ]
    )

    results = coiled.list_api_tokens()
    expected_num_results = ApiToken.objects.filter(user=sample_user.user).count()

    assert len(results) == expected_num_results

    # create another 101 api tokens
    ApiToken.objects.bulk_create(
        [
            ApiToken(
                user=sample_user.user,
                token_hash="aaa",
            )
            for i in range(101, 202)
        ]
    )

    results = coiled.list_api_tokens()
    expected_num_results = ApiToken.objects.filter(user=sample_user.user).count()
    logger.info(
        f"checking depaginated results from list_api_tokens, expected: "
        f"{expected_num_results}, found: {len(results)}"
    )
    assert len(results) == expected_num_results


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_public_api_depagination(sample_user, software_env):

    cloud_client = Cloud(sample_user.account.slug)
    PAGE_SIZE = 100
    NUM_PAGES = 8

    async def mock_page_func(page, account=None) -> Tuple[Dict, Optional[str]]:
        assert account == sample_user.account.slug
        start = ((page - 1) * PAGE_SIZE) + 1
        end = page * PAGE_SIZE
        page_result = {i: i for i in range(start, end + 1)}
        next_url = "dummy_url" if page < NUM_PAGES else None
        return page_result, next_url

    results = await cloud_client._depaginate(
        mock_page_func, account=sample_user.account.slug
    )
    expected_num_results = PAGE_SIZE * NUM_PAGES

    assert len(results) == expected_num_results
    assert len(set(results.keys())) == expected_num_results


def test_public_api_list_core_usage_json(sample_user):
    result = coiled.list_core_usage()

    assert result["core_limit_account"] == 10
    assert result["core_limit_user"] == 10
    assert result["num_running_cores_user"] == 0
    assert result["num_running_cores_account"] == 0


def test_public_api_diagnostics(sample_user):
    result = coiled.diagnostics()

    assert result["health_check"]
    assert result["local_versions"]
    assert result["coiled_configuration"]


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_default_coiled(
    cloud,
    sample_user,
):
    account = sample_user.account
    assert account.options == {"aws_region_name": "us-east-1"}

    if environ.get("TEST_BACKEND") == "in_process":
        assert account.container_registry == {
            "type": ContainerRegistryType.CONDA,
        }
    else:
        assert account.container_registry == {
            "type": ContainerRegistryType.ECR,
            "credentials": {},
            "public_ecr": False,
            "region": settings.AWS_DEFAULT_USER_REGION,
        }
    assert account.backend == settings.DEFAULT_CLUSTER_BACKEND

    coiled.set_backend_options(use_coiled_defaults=True)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_invalid_args(
    cloud,
    sample_user,
):
    with pytest.raises(UnsupportedBackendError) as e_info:
        coiled.set_backend_options(backend="vm_geocities")  # type: ignore
    assert "Supplied backend: vm_geocities not in supported types: " in str(e_info)
    assert "aws" in str(e_info)
    assert "gcp" in str(e_info)


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_aws_vm(
    cloud,
    sample_user,
):
    account = sample_user.account

    # set region
    coiled.set_backend_options(backend="aws", region=settings.AWS_DEFAULT_USER_REGION)
    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS

    # set no region
    coiled.set_backend_options(backend="aws")

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_aws_vm_customer_hosted(cloud, sample_user, mocker):

    mocker.patch("coiled.utils.boto3")
    account = sample_user.account

    # mock this _configure_backend method as we don't want to test this here
    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )

    # create VPC requires have aws_* creds
    with pytest.raises(AWSCredentialsParameterError) as e_info:
        coiled.set_backend_options(backend="aws", customer_hosted=True)
    assert (
        "Creating an AWS VPC requires params: aws_access_key_id and aws_secret_access_key."
        in str(e_info)
    )

    credentials = {
        "aws_access_key_id": "test-aws_access_key_id",
        "aws_secret_access_key": "test-aws_secret_access_key",
    }

    # set region
    coiled.set_backend_options(
        backend="aws",
        aws_region=settings.AWS_DEFAULT_USER_REGION,
        customer_hosted=True,
        **credentials,
    )
    account.refresh_from_db()

    options = {
        "aws_region_name": settings.AWS_DEFAULT_USER_REGION,
        "credentials": {
            "aws_access_key": "test-aws_access_key_id",
            "aws_secret_key": "test-aws_secret_access_key",
        },
        # these are optional, but default values will be reflected
        "firewall": {},
        "network": {},
        "provider_name": "aws",
        "type": "aws_cloudbridge_backend_options",
    }

    assert account.options == options

    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {
            "aws_access_key_id": "test-aws_access_key_id",
            "aws_secret_access_key": "test-aws_secret_access_key",
        },
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]
    assert kwargs_options.aws_region_name == options["aws_region_name"]


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gcp_vm_coiled_hosted(cloud, sample_user):

    account = sample_user.account

    # set region
    coiled.set_backend_options(
        backend="gcp",
        zone=settings.GCP_DEFAULT_USER_ZONE,
    )
    account.refresh_from_db()

    default_region, default_zone = parse_gcp_location(settings.GCP_DEFAULT_USER_ZONE)
    assert account.options == {
        "gcp_region_name": default_region,
        "gcp_zone_name": default_zone,
    }
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_GCP

    # set no region or zone
    coiled.set_backend_options(backend="gcp")

    account.refresh_from_db()

    assert account.options == {
        "gcp_region_name": default_region,
        "gcp_zone_name": default_zone,
    }
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_GCP

    # make sure region makes it through
    coiled.set_backend_options(
        backend="gcp",
        gcp_region="us-central1",
    )
    account.refresh_from_db()
    assert account.options == {
        "gcp_region_name": "us-central1",
        # For now we add zone "c" to the end
        "gcp_zone_name": "us-central1-c",
    }


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gcp_vm_customer_hosted(cloud, sample_user, mocker):

    account = sample_user.account

    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )

    reqed_keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    coiled.set_backend_options(
        backend="gcp",
        customer_hosted=True,
        gcp_service_creds_dict=gcp_service_creds_dict,
        gcp_project_id="test-project-name",
        gcp_region="gcp_region_name",
    )
    account.refresh_from_db()

    options = {
        "provider_name": "gcp",
        "type": "gcp_cloudbridge_backend_options",
        "gcp_project_name": "test-project-name",
        "gcp_region_name": "gcp_region_name",
        "gcp_zone_name": "gcp_region_name-c",
        "gcp_service_creds_dict": gcp_service_creds_dict,
        "firewall": {},
        "network": {},
        "instance_service_account": None,
    }
    assert account.options == options
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]
    assert kwargs_options.gcp_region_name == options["gcp_region_name"]


@pytest.mark.test_group("core-slow-group-12")
def test__parse_gcp_creds_missing_project_id(cloud, sample_user, mocker):
    reqed_keys = [
        "type",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    with pytest.raises(GCPCredentialsError) as e:
        _parse_gcp_creds(
            gcp_service_creds_file=None, gcp_service_creds_dict=gcp_service_creds_dict
        )
    error_message = e.value.args[0]
    assert error_message.startswith(
        "Unable to find 'project_id' in 'gcp_service_creds_dict'"
    )


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gcp_vm_customer_hosted_gar_registry(
    cloud, sample_user, mocker
):

    account = sample_user.account

    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )
    mocker.patch(
        "software_environments.registry.gcp",
        mock.AsyncMock(),
    )

    reqed_keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    coiled.set_backend_options(
        backend="gcp",
        customer_hosted=True,
        gcp_service_creds_dict=gcp_service_creds_dict,
        gcp_project_name="test-project-name",
        gcp_region="gcp_region_name",
        gcp_zone="gcp_zone_name",
        registry_type="gar",
    )
    account.refresh_from_db()

    options = {
        "provider_name": "gcp",
        "type": "gcp_cloudbridge_backend_options",
        "gcp_project_name": "test-project-name",
        "gcp_region_name": "gcp_region_name",
        "gcp_zone_name": "gcp_zone_name",
        "gcp_service_creds_dict": gcp_service_creds_dict,
        "firewall": {},  # These are added at the account level regarless
        "network": {},
        "instance_service_account": None,
    }
    assert account.options == options
    assert account.container_registry == {
        "type": ContainerRegistryType.GAR,
        "credentials": gcp_service_creds_dict,
        "project_id": "test-project-name",
        "location": "gcp_region_name",
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]
    assert kwargs_options.gcp_region_name == options["gcp_region_name"]


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gar_registry_validation(cloud, mocker):
    mocker.patch("coiled.utils.boto3")
    mocker.patch("backends.cloudbridge.cloudbridge.ClusterManager._configure_backend")
    credentials = {
        "aws_access_key_id": "test-aws_access_key_id",
        "aws_secret_access_key": "test-aws_secret_access_key",
    }
    reqed_keys = [
        "type",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    with pytest.raises(GCPCredentialsError) as e:
        coiled.set_backend_options(
            gcp_service_creds_dict=gcp_service_creds_dict,
            # These are required for GAR
            # gcp_project_name="test-project-name",
            # gcp_region_name="gcp_region_name",
            registry_type="gar",
            **credentials,
        )
    error_message = e.value.args[0]
    assert error_message.startswith(
        "Unable to find 'project_id' in 'gcp_service_creds_dict'"
    )

    with pytest.raises(GCPCredentialsParameterError) as e:
        coiled.set_backend_options(
            backend="gcp",
            customer_hosted=True,
            # Required for GAR, but error is different because
            # it happens earlier.
            # gcp_service_creds_dict=gcp_service_creds_dict,
            gcp_project_name="test-project-name",
            gcp_region="gcp_region_name",
            registry_type="gar",
            **credentials,
        )
    error_message = e.value.args[0]
    assert (
        "Parameter 'gcp_service_creds_file' or 'gcp_service_creds_dict' must be supplied"
        in error_message
    )


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_handle_exception_in_configure_backend(
    cloud, sample_user, mocker
):

    account = sample_user.account

    assert account.options == {"aws_region_name": "us-east-1"}

    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == settings.DEFAULT_CLUSTER_BACKEND

    configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )
    configure_backend_mock.side_effect = Exception("boom something broke")

    rollback_failed_configure_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager.rollback_failed_configure"
    )

    reqed_keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    with pytest.raises(ServerError):
        coiled.set_backend_options(
            backend="gcp",
            customer_hosted=True,
            gcp_service_creds_dict=gcp_service_creds_dict,
            gcp_project_name="test-project-name",
            gcp_region="gcp_region_name",
        )
    account.refresh_from_db()
    assert account.options == {"aws_region_name": "us-east-1"}

    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == settings.DEFAULT_CLUSTER_BACKEND
    assert rollback_failed_configure_mock.called


### TEST backend_options_registries


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_ecr_no_credentials(
    cloud,
    sample_user,
):
    # TODO What am I missing for set up?
    account = sample_user.account

    credentials = {}

    coiled.set_backend_options(registry_type="ecr", **credentials)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": credentials,
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_ecr(cloud, sample_user, mocker):
    # pytest installs the coiled client
    mocker.patch("coiled.utils.boto3")
    account = sample_user.account

    coiled.set_backend_options(registry_type="ecr")

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_dockerhub(
    cloud,
    sample_user,
):
    account = sample_user.account

    registry = {
        "type": ContainerRegistryType.DOCKER_HUB,
        "namespace": "registry_namespace",
        "access_token": "registry_access_token",
        "uri": "registry_uri",
        "username": "registry_username",
    }
    kwargs = {f"registry_{k}": v for k, v in registry.items()}

    coiled.set_backend_options(**kwargs)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}

    registry["account"] = registry["namespace"]
    registry["password"] = registry["access_token"]
    del registry["namespace"]
    del registry["access_token"]

    assert account.container_registry == registry
    assert account.backend == types.BackendChoices.VM_AWS

    ## test use register_username if not registry_namespace
    registry = {
        "type": ContainerRegistryType.DOCKER_HUB,
        "access_token": "registry_access_token",
        "uri": "registry_uri",
        "username": "registry_username",
    }
    kwargs = {f"registry_{k}": v for k, v in registry.items()}

    coiled.set_backend_options(**kwargs)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}

    registry["account"] = registry["username"]
    registry["password"] = registry["access_token"]
    del registry["access_token"]
    assert account.container_registry == registry
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_dockerhub_required_fields(
    cloud,
    sample_user,
):

    registry = {
        "type": ContainerRegistryType.DOCKER_HUB,
        "namespace": "registry_namespace",
        "access_token": "registry_access_token",
        "uri": "registry_uri",
    }
    kwargs = {f"registry_{k}": v for k, v in registry.items()}

    with pytest.raises(RegistryParameterError) as e_info:
        coiled.set_backend_options(**kwargs, registry_username="UpperCasedUserName")
    assert "Your dockerhub [registry_username] must be lowercase" in str(e_info)

    with pytest.raises(RegistryParameterError) as e_info:
        coiled.set_backend_options(**kwargs)
    assert (
        "For setting your registry credentials, these fields cannot be empty: ['registry_username']"
        in str(e_info)
    )


def test_parse_gcp_creds_parameter_missing():
    with pytest.raises(GCPCredentialsParameterError):
        _parse_gcp_creds(gcp_service_creds_dict=None, gcp_service_creds_file="")


def test_parse_gcp_creds_not_file():
    with pytest.raises(GCPCredentialsError):
        _parse_gcp_creds(
            gcp_service_creds_dict=None, gcp_service_creds_file="non_existent"
        )


def test_parse_gcp_creds_bad_file(mocker, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")
    mocker.mock_open(read_data="test").return_value = ""
    with pytest.raises(GCPCredentialsError):
        result = _parse_gcp_creds(
            gcp_service_creds_dict=None, gcp_service_creds_file=test_file
        )
        assert "not a valid JSON file" in result


def test_parse_gcp_creds_missing_all_keys(mocker, tmp_path):
    test_file = tmp_path / "test.json"
    test_file.write_text("test")
    mocker.patch("json.load").return_value = {}

    with pytest.raises(GCPCredentialsError) as error:
        _parse_gcp_creds(gcp_service_creds_dict=None, gcp_service_creds_file=test_file)

    assert "is missing the keys" in str(error.value)


def test_parse_gcp_creds_missing_project_id(mocker, tmp_path):
    test_file = tmp_path / "test.json"
    test_file.write_text("test")
    mocker.patch("json.load").return_value = {
        "type": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_x509_cert_url": "",
    }

    with pytest.raises(GCPCredentialsError) as error:
        _parse_gcp_creds(gcp_service_creds_dict=None, gcp_service_creds_file=test_file)

    assert "is missing the keys" in str(error.value)
    assert "project_id" in str(error.value)


def test_list_gpu_types(sample_user, capfd):
    gpu_type = coiled.list_gpu_types()

    assert "nvidia-tesla-t4" in gpu_type.values()


def test_public_api_get_billing_activity(sample_user):
    result = coiled.get_billing_activity()

    assert result["count"] == 2
    assert result["next"] is None
    assert result["page_size"] == 15
    for res in result["results"]:
        assert (res["kind"] in ["program_change", "monthly_grant"]) is True
        if res["kind"] == "monthly_grant":
            assert res["amount_credits"] == "150.0000"
