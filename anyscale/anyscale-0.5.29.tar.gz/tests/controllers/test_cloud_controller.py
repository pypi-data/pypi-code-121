from typing import Any, Dict, Iterator, List, Optional, Tuple
from unittest.mock import Mock, patch

from click import ClickException
import pytest

from anyscale.aws_iam_policies import (
    AMAZON_ECR_READONLY_ACCESS_POLICY_ARN,
    AMAZON_S3_FULL_ACCESS_POLICY_ARN,
)
from anyscale.client.openapi_client.models import (
    AnyscaleAWSAccount,
    AnyscaleawsaccountResponse,
    Cloud,
    CloudConfig,
    CloudResponse,
)
from anyscale.controllers.cloud_controller import CloudController


@pytest.fixture()
def mock_api_client(cloud_test_data: Cloud) -> Mock:
    mock_api_client = Mock()
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        return_value=CloudResponse(result=cloud_test_data)
    )
    mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=CloudResponse(result=cloud_test_data)
    )
    mock_api_client.delete_cloud_api_v2_clouds_cloud_id_delete = Mock(return_value={})
    mock_api_client.update_cloud_config_api_v2_clouds_cloud_id_config_put = Mock(
        return_value={}
    )

    return mock_api_client


@pytest.fixture(autouse=True)
def mock_auth_api_client(
    mock_api_client: Mock, base_mock_anyscale_api_client: Mock
) -> Iterator[None]:
    mock_auth_api_client = Mock(
        api_client=mock_api_client, anyscale_api_client=base_mock_anyscale_api_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_get_available_regions() -> Iterator[None]:
    with patch(
        "anyscale.controllers.cloud_controller.get_available_regions",
        return_value=["us-west-2"],
        autospec=True,
    ):
        yield


def mock_role(document: Optional[Dict[str, Any]] = None) -> Mock:
    if document is None:
        document = {}
    mock_role = Mock()

    mock_role.arn = "ARN"
    mock_role.attach_policy = Mock()
    mock_role.assume_role_policy_document = document

    return mock_role


def test_setup_cloud_aws() -> None:
    with patch.object(
        CloudController, "setup_aws", return_value=None
    ) as mock_setup_aws:
        cloud_controller = CloudController()
        cloud_controller.setup_cloud(
            is_k8s=False, provider="aws", region=None, name="test-aws", yes=False,
        )

        mock_setup_aws.assert_called_once_with(
            region="us-west-2", name="test-aws", yes=False
        )


def test_setup_cloud_aws_k8s() -> None:
    with patch.object(
        CloudController, "setup_aws_k8s_cloud", return_value=None
    ) as mock_setup_aws_k8s_cloud:
        cloud_controller = CloudController()
        cloud_controller.setup_cloud(
            is_k8s=True, provider="aws", region=None, name="test-aws", yes=False,
        )

        mock_setup_aws_k8s_cloud.assert_called_once_with(
            region="us-west-2", name="test-aws", yes=False
        )


def test_setup_cloud_gcp() -> None:
    mock_launch_gcp_cloud_setup = Mock(return_value=None)
    with patch.multiple(
        "anyscale.controllers.cloud_controller",
        launch_gcp_cloud_setup=mock_launch_gcp_cloud_setup,
    ):
        cloud_controller = CloudController()
        cloud_controller.setup_cloud(
            is_k8s=True, provider="gcp", region=None, name="test-gcp", yes=True,
        )

        mock_launch_gcp_cloud_setup.assert_called_once_with(
            region="us-west1",
            name="test-gcp",
            folder_id=None,
            vpc_peering_ip_range=None,
            vpc_peering_target_project_id=None,
            vpc_peering_target_vpc_id=None,
        )

        mock_launch_gcp_cloud_setup.reset_mock()

        cloud_controller.setup_cloud(
            is_k8s=True,
            provider="gcp",
            region=None,
            name="test-gcp",
            yes=True,
            folder_id=1234,
        )

        mock_launch_gcp_cloud_setup.assert_called_once_with(
            region="us-west1",
            name="test-gcp",
            folder_id=1234,
            vpc_peering_ip_range=None,
            vpc_peering_target_project_id=None,
            vpc_peering_target_vpc_id=None,
        )


@pytest.mark.parametrize(
    "vpc_peering_options",
    [
        ("10.0.0.0/12", "project_id", "vpc_id"),
        ("10.0.0.0/12", None, "vpc_id"),
        ("10.0.0.0/12", "project_id", None),
    ],
)
def test_setup_cloud_gcp_vpc_peering(
    vpc_peering_options: Tuple[str, Optional[str], Optional[str]]
) -> None:
    (
        vpc_peering_ip_range,
        vpc_peering_target_project_id,
        vpc_peering_target_vpc_id,
    ) = vpc_peering_options
    mock_launch_gcp_cloud_setup = Mock(return_value=None)
    with patch.multiple(
        "anyscale.controllers.cloud_controller",
        launch_gcp_cloud_setup=mock_launch_gcp_cloud_setup,
    ):
        cloud_controller = CloudController()
        if vpc_peering_target_project_id is None or vpc_peering_target_vpc_id is None:
            with pytest.raises(ClickException):
                cloud_controller.setup_cloud(
                    is_k8s=True,
                    provider="gcp",
                    region=None,
                    name="test-gcp",
                    yes=True,
                    vpc_peering_ip_range=vpc_peering_ip_range,
                    vpc_peering_target_project_id=vpc_peering_target_project_id,
                    vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
                )
        else:
            cloud_controller.setup_cloud(
                is_k8s=True,
                provider="gcp",
                region=None,
                name="test-gcp",
                yes=True,
                vpc_peering_ip_range=vpc_peering_ip_range,
                vpc_peering_target_project_id=vpc_peering_target_project_id,
                vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
            )

        if vpc_peering_target_project_id is None or vpc_peering_target_vpc_id is None:
            return

        mock_launch_gcp_cloud_setup.assert_called_once_with(
            region="us-west1",
            name="test-gcp",
            folder_id=None,
            vpc_peering_ip_range=vpc_peering_ip_range,
            vpc_peering_target_project_id=vpc_peering_target_project_id,
            vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
        )

        mock_launch_gcp_cloud_setup.reset_mock()

        cloud_controller.setup_cloud(
            is_k8s=True,
            provider="gcp",
            region=None,
            name="test-gcp",
            yes=True,
            folder_id=1234,
            vpc_peering_ip_range=vpc_peering_ip_range,
            vpc_peering_target_project_id=vpc_peering_target_project_id,
            vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
        )

        mock_launch_gcp_cloud_setup.assert_called_once_with(
            region="us-west1",
            name="test-gcp",
            folder_id=1234,
            vpc_peering_ip_range=vpc_peering_ip_range,
            vpc_peering_target_project_id=vpc_peering_target_project_id,
            vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
        )


@pytest.mark.parametrize(
    "vpc_peering_options,error_output",
    [
        (
            ("not_an_ip_address", "project_id", "vpc_id"),
            "not_an_ip_address is not a valid IP address.",
        ),
        (
            ("10.0.0.0/20", "project_id", "vpc_id"),
            "10.0.0.0/20 is not a valid IP range. The minimum size is /16",
        ),
        (
            ("42.0.0.0/10", "project_id", "vpc_id"),
            "42.0.0.0/10 is not a allowed private IP address range for GCP",
        ),
    ],
)
def test_setup_cloud_gcp_vpc_peering_validation(
    vpc_peering_options: Tuple[str, str, str], error_output: str
) -> None:
    (
        vpc_peering_ip_range,
        vpc_peering_target_project_id,
        vpc_peering_target_vpc_id,
    ) = vpc_peering_options
    mock_launch_gcp_cloud_setup = Mock(return_value=None)
    with patch.multiple(
        "anyscale.controllers.cloud_controller",
        launch_gcp_cloud_setup=mock_launch_gcp_cloud_setup,
    ):
        cloud_controller = CloudController()

        with pytest.raises(ClickException) as e:
            cloud_controller.setup_cloud(
                is_k8s=True,
                provider="gcp",
                region=None,
                name="test-gcp",
                yes=True,
                vpc_peering_ip_range=vpc_peering_ip_range,
                vpc_peering_target_project_id=vpc_peering_target_project_id,
                vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
            )

        assert error_output in e.value.message


def test_setup_cloud_gcp_bad_region() -> None:
    mock_confirm = Mock(side_effect=ClickException("aborted"))
    with patch.multiple(
        "anyscale.controllers.cloud_controller", confirm=mock_confirm,
    ):
        cloud_controller = CloudController()
        # NOTE: GCP regions are [cont]-[local][number], not [cont]-[local]-[number]
        with pytest.raises(ClickException):
            cloud_controller.setup_cloud(
                is_k8s=True, provider="gcp", region="us-west-2", name="test-gcp",
            )

        mock_confirm.assert_called()


@pytest.mark.parametrize("is_k8s", [True, False])
def test_setup_cloud_invalid_provider(is_k8s: bool) -> None:
    cloud_controller = CloudController()
    with pytest.raises(ClickException):
        cloud_controller.setup_cloud(
            is_k8s=is_k8s,
            provider="azure",
            region="azure-west-1",
            name="invalid cloud provider",
            yes=False,
        )


def test_delete_cloud_by_name(cloud_test_data: Cloud) -> None:
    cloud_controller = CloudController()
    success = cloud_controller.delete_cloud(
        cloud_id=None, cloud_name=cloud_test_data.name, skip_confirmation=True
    )
    assert success

    cloud_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post.assert_called_once_with(
        cloud_name_options={"name": cloud_test_data.name}
    )
    cloud_controller.api_client.delete_cloud_api_v2_clouds_cloud_id_delete(
        cloud_id=cloud_test_data.id
    )


def test_delete_cloud_by_id(cloud_test_data: Cloud) -> None:
    cloud_controller = CloudController()
    success = cloud_controller.delete_cloud(
        cloud_id=cloud_test_data.id, cloud_name=None, skip_confirmation=True
    )
    assert success

    cloud_controller.api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
        cloud_id=cloud_test_data.id
    )
    cloud_controller.api_client.delete_cloud_api_v2_clouds_cloud_id_delete(
        cloud_id=cloud_test_data.id
    )


def test_missing_name_and_id() -> None:
    cloud_controller = CloudController()

    with pytest.raises(ClickException):
        cloud_controller.delete_cloud(None, None, True)

    with pytest.raises(ClickException):
        cloud_controller.update_cloud_config(None, None, 0)

    with pytest.raises(ClickException):
        cloud_controller.get_cloud_config(None, None)


def test_setup_cross_region(cloud_test_data: Cloud) -> None:
    mock_get_aws_account = Mock(
        return_value=AnyscaleawsaccountResponse(
            result=AnyscaleAWSAccount(anyscale_aws_account="aws_account_type")
        )
    )
    mock_create_cloud = Mock(return_value=CloudResponse(result=cloud_test_data))
    mocked_role = mock_role(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "1",
                    "Effect": "Allow",
                    "Principal": {"AWS": ["ARN"]},
                    "Action": "sts:AssumeRole",
                    "Condition": {"StringEquals": {"sts:ExternalId": "extid"}},
                }
            ],
        }
    )

    with patch.multiple(
        "anyscale.controllers.cloud_controller",
        _get_role=Mock(return_value=mocked_role),
    ):
        cloud_controller = CloudController()
        cloud_controller.api_client.get_anyscale_aws_account_api_v2_clouds_anyscale_aws_account_get = (
            mock_get_aws_account
        )
        cloud_controller.api_client.create_cloud_api_v2_clouds_post = mock_create_cloud
        cloud_controller.setup_aws_cross_account_role("us-west-2", "name")

    cloud_controller.api_client.get_anyscale_aws_account_api_v2_clouds_anyscale_aws_account_get.assert_called_once()
    mocked_role.attach_policy.assert_called()
    mocked_role.AssumeRolePolicy.assert_called()


@pytest.mark.parametrize(
    "roles",
    [
        pytest.param([None, mock_role()], id="role_doesnt_exist"),
        pytest.param([mock_role()], id="role_already_exists"),
    ],
)
def test_setup_aws_ray_role(roles: List[Optional[Mock]]) -> None:
    assert roles[-1] is not None, "roles must end with a real role"

    mock_iam = Mock()
    mock_iam.create_role = Mock()

    with patch.multiple(
        "anyscale.controllers.cloud_controller", _get_role=Mock(side_effect=roles),
    ), patch.multiple(
        "boto3", resource=Mock(return_value=mock_iam),
    ):
        cloud_controller = CloudController()
        cloud_controller.setup_aws_ray_role("us-west-2", "ray-autoscaler-v1")

    if roles[0] is None:
        # Role didn't exist at the start and had to be "created"
        mock_iam.create_role.assert_called_once()

    # Assert we actually attached the base policies
    roles[-1].attach_policy.assert_any_call(PolicyArn=AMAZON_S3_FULL_ACCESS_POLICY_ARN)
    roles[-1].attach_policy.assert_any_call(
        PolicyArn=AMAZON_ECR_READONLY_ACCESS_POLICY_ARN
    )
    assert 2 == roles[-1].attach_policy.call_count


def test_update_cloud_config_by_name(cloud_test_data: Cloud) -> None:
    cloud_controller = CloudController()
    cloud_controller.update_cloud_config(
        cloud_id=None, cloud_name=cloud_test_data.name, max_stopped_instances=100,
    )

    cloud_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post.assert_called_once_with(
        cloud_name_options={"name": cloud_test_data.name}
    )
    cloud_controller.api_client.update_cloud_config_api_v2_clouds_cloud_id_config_put.assert_called_once_with(
        cloud_id=cloud_test_data.id,
        cloud_config=CloudConfig(max_stopped_instances=100),
    )


def test_update_cloud_config_by_id(cloud_test_data: Cloud) -> None:
    cloud_controller = CloudController()
    cloud_controller.update_cloud_config(
        cloud_id=cloud_test_data.id, cloud_name=None, max_stopped_instances=100,
    )

    cloud_controller.api_client.update_cloud_config_api_v2_clouds_cloud_id_config_put.assert_called_once_with(
        cloud_id=cloud_test_data.id,
        cloud_config=CloudConfig(max_stopped_instances=100),
    )


@pytest.mark.parametrize("cloud_id", [None, "cloud_id_1"])
@pytest.mark.parametrize("cloud_name", [None, "cloud_name_1"])
def test_set_default_cloud(cloud_id: Optional[str], cloud_name: Optional[str]) -> None:
    cloud_controller = CloudController()
    if not (cloud_id or cloud_name) or (cloud_id and cloud_name):
        # Error if neither or both of cloud_id and cloud_name provided
        with pytest.raises(ClickException):
            cloud_controller.set_default_cloud(
                cloud_id=cloud_id, cloud_name=cloud_name,
            )
    else:
        cloud_controller.set_default_cloud(
            cloud_id=cloud_id, cloud_name=cloud_name,
        )
        cloud_controller.api_client.update_default_cloud_api_v2_organizations_update_default_cloud_post.assert_called_once_with(
            cloud_id="cloud_id_1"
        )


@pytest.mark.parametrize("cloud_id", [None, "cloud_id_1"])
@pytest.mark.parametrize("cloud_name", [None, "cloud_name_1"])
def test_list_cloud(cloud_id: Optional[str], cloud_name: Optional[str]) -> None:
    cloud_controller = CloudController()
    cloud_controller.api_client.list_clouds_api_v2_clouds_get = Mock(
        return_value=Mock(results=[Mock()])
    )
    cloud_controller.list_clouds(cloud_name, cloud_id)

    if cloud_id is not None:
        cloud_controller.api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
            cloud_id
        )
    elif cloud_name is not None:
        cloud_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post.assert_called_once_with(
            {"name": cloud_name}
        )
    else:
        cloud_controller.api_client.list_clouds_api_v2_clouds_get.assert_called_once_with()
