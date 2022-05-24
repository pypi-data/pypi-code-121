"""
Fetches data required and formats output for `anyscale cloud` commands.
"""

import ipaddress
import json
import os
import time
from typing import Any, Dict, Optional

import boto3
import botocore.exceptions
from click import ClickException, INT, prompt

from anyscale.aws_iam_policies import (
    AMAZON_CLOUDWATCH_FULL_ACCESS_POLICY_ARN,
    AMAZON_EC2_FULL_ACCESS_POLICY_ARN,
    AMAZON_ECR_READONLY_ACCESS_POLICY_ARN,
    AMAZON_IAM_FULL_ACCESS_POLICY_ARN,
    AMAZON_ROUTE53_FULL_ACCESS_POLICY_ARN,
    AMAZON_S3_FULL_ACCESS_POLICY_ARN,
    AMAZON_VPC_FULL_ACCESS_POLICY_ARN,
    ANYSCALE_IAM_ACCESS_POLICY_DOCUMENT,
    ANYSCALE_IAM_ACCESS_POLICY_NAME,
    EKS_FULL_ACCESS_POLICY_DOCUMENT,
    EKS_FULL_ACCESS_POLICY_NAME,
)
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import (
    Cloud,
    CloudConfig,
    CloudProviders,
    CloudResponse,
    WriteCloud,
)
from anyscale.cloud import get_cloud_id_and_name, get_cloud_json_from_id
from anyscale.conf import ANYSCALE_IAM_ROLE_NAME
from anyscale.controllers.base_controller import BaseController
from anyscale.formatters import clouds_formatter
from anyscale.util import (  # pylint:disable=private-import
    _CACHED_GCP_REGIONS,
    _get_role,
    _resource,
    _update_external_ids_for_policy,
    confirm,
    get_available_regions,
    launch_gcp_cloud_setup,
    number_of_external_ids_in_policy,
)


ROLE_CREATION_RETRIES = 30
ROLE_CREATION_INTERVAL_SECONDS = 1


class CloudController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.log.open_block("Output")

    def delete_cloud(
        self,
        cloud_name: Optional[str],
        cloud_id: Optional[str],
        skip_confirmation: bool,
    ) -> bool:
        """
        Deletes a cloud by name or id.
        """

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        confirm(
            f"You'll lose access to existing sessions created with cloud {cloud_id} if you drop it.\nContinue?",
            skip_confirmation,
        )

        self.api_client.delete_cloud_api_v2_clouds_cloud_id_delete(cloud_id=cloud_id)

        self.log.info(f"Deleted cloud {cloud_name}")

        return True

    def list_clouds(self, cloud_name: Optional[str], cloud_id: Optional[str]) -> str:
        if cloud_id is not None:
            clouds = [
                self.api_client.get_cloud_api_v2_clouds_cloud_id_get(cloud_id).result
            ]
        elif cloud_name is not None:
            clouds = [
                self.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post(
                    {"name": cloud_name}
                ).result
            ]
        else:
            clouds = self.api_client.list_clouds_api_v2_clouds_get().results
        output = clouds_formatter.format_clouds_output(clouds=clouds, json_format=False)

        return str(output)

    def verify_vpc_peering(
        self,
        yes: bool,
        vpc_peering_ip_range: Optional[str],
        vpc_peering_target_project_id: Optional[str],
        vpc_peering_target_vpc_id: Optional[str],
    ) -> None:
        if (
            vpc_peering_ip_range
            or vpc_peering_target_project_id
            or vpc_peering_target_vpc_id
        ):
            if not vpc_peering_ip_range:
                raise ClickException("Please specify a VPC peering IP range.")
            if not vpc_peering_target_project_id:
                raise ClickException("Please specify a VPC peering target project ID.")
            if not vpc_peering_target_vpc_id:
                raise ClickException("Please specify a VPC peering target VPC ID.")
        else:
            return

        try:
            valid_ip_network = ipaddress.IPv4Network(vpc_peering_ip_range)
        except ValueError:
            raise ClickException(f"{vpc_peering_ip_range} is not a valid IP address.")
        # https://cloud.google.com/vpc/docs/vpc#valid-ranges
        allowed_ip_ranges = [
            ipaddress.IPv4Network("10.0.0.0/8"),
            ipaddress.IPv4Network("172.16.0.0/12"),
            ipaddress.IPv4Network("192.168.0.0/16"),
        ]

        for allowed_ip_range in allowed_ip_ranges:
            if valid_ip_network.subnet_of(allowed_ip_range):
                break
        else:
            raise ClickException(
                f"{vpc_peering_ip_range} is not a allowed private IP address range for GCP. The allowed IP ranges are 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16. For more info, see https://cloud.google.com/vpc/docs/vpc#valid-ranges"
            )

        if (
            valid_ip_network.num_addresses
            < ipaddress.IPv4Network("192.168.0.0/16").num_addresses
        ):
            raise ClickException(
                f"{vpc_peering_ip_range} is not a valid IP range. The minimum size is /16"
            )

        if not yes:
            confirm(
                f"\nYou selected to create a VPC peering connection to VPC {vpc_peering_target_vpc_id} in GCP project {vpc_peering_target_project_id}."
                f"This will create a VPC peering connection from your Anyscale GCP project to the target project ({vpc_peering_target_project_id})."
                "You will need to manually create the peering connection from the target project to your Anyscale GCP project after the anyscale cloud is created.\n"
                "Continue cloud setup?",
                False,
            )

    def setup_cloud(
        self,
        is_k8s: bool,
        provider: str,
        region: Optional[str],
        name: str,
        yes: bool = False,
        folder_id: Optional[int] = None,
        vpc_peering_ip_range: Optional[str] = None,
        vpc_peering_target_project_id: Optional[str] = None,
        vpc_peering_target_vpc_id: Optional[str] = None,
    ) -> None:
        """
        Sets up a cloud provider
        """
        if provider == "aws":
            # If the region is blank, change it to the default for AWS.
            if region is None:
                region = "us-west-2"
            regions_available = get_available_regions()
            if region not in regions_available:
                raise ClickException(
                    f"Region '{region}' is not available. Regions available are: "
                    f"{', '.join(map(repr, regions_available))}"
                )
            if is_k8s:
                self.setup_aws_k8s_cloud(region=region, name=name, yes=yes)
            else:
                self.setup_aws(region=region, name=name, yes=yes)
        elif provider == "gcp":
            # If the region is blank, change it to the default for GCP.
            if region is None:
                region = "us-west1"
            # Warn the user about a bad region before the cloud configuration begins.
            # GCP's `list regions` API requires a project, meaning true verification
            # happens in the middle of the flow.
            if region not in _CACHED_GCP_REGIONS and not yes:
                confirm(
                    f"You selected the region: {region}, but it is not in"
                    f"the cached list of GCP regions:\n\n{_CACHED_GCP_REGIONS}.\n"
                    "Continue cloud setup with this region?",
                    False,
                )
            if not yes and not folder_id:
                folder_id = prompt(
                    "Please select the GCP Folder ID where the 'Anyscale' folder will be created.\n"
                    "\tYour GCP account must have permissions to create sub-folders in the specified folder.\n"
                    "\tView your organization's folder layout here: https://console.cloud.google.com/cloud-resource-manager\n"
                    "\tIf not specified, the 'Anyscale' folder will be created directly under the organization.\n"
                    "Folder ID (numerals only)",
                    default="",
                    type=INT,
                    show_default=False,
                )

            self.verify_vpc_peering(
                yes,
                vpc_peering_ip_range,
                vpc_peering_target_project_id,
                vpc_peering_target_vpc_id,
            )
            # TODO: interactive setup process through the CLI?
            launch_gcp_cloud_setup(
                name=name,
                region=region,
                folder_id=folder_id,
                vpc_peering_ip_range=vpc_peering_ip_range,
                vpc_peering_target_project_id=vpc_peering_target_project_id,
                vpc_peering_target_vpc_id=vpc_peering_target_vpc_id,
            )
        else:
            raise ClickException(
                f"Invalid Cloud provider: {provider}. Available providers are [aws, gcp]."
            )

    def setup_aws(self, region: str, name: str, yes: bool = False) -> None:
        from ray.autoscaler._private.aws.config import DEFAULT_RAY_IAM_ROLE

        os.environ["AWS_DEFAULT_REGION"] = region

        confirm(
            "\nYou are about to give anyscale full access to EC2 and IAM, as well as readonly access to ECR, all in your AWS account.\n\n"
            "Continue?",
            yes,
        )

        self.setup_aws_cross_account_role(region, name)
        self.setup_aws_ray_role(region, DEFAULT_RAY_IAM_ROLE)

        self.log.info("AWS credentials setup complete!")
        self.log.info(
            "You can revoke the access at any time by deleting anyscale IAM user/role in your account."
        )
        self.log.info(
            "Head over to the web UI to create new sessions in your AWS account!"
        )

    def setup_aws_cross_account_role(self, region: str, name: str) -> None:
        response = (
            self.api_client.get_anyscale_aws_account_api_v2_clouds_anyscale_aws_account_get()
        )

        anyscale_aws_account = response.result.anyscale_aws_account
        anyscale_aws_iam_role_policy: Dict[str, Any] = {
            "Version": "2012-10-17",
            "Statement": {
                "Sid": "1",
                "Effect": "Allow",
                "Principal": {"AWS": anyscale_aws_account},
                "Action": "sts:AssumeRole",
            },
        }

        role = _get_role(ANYSCALE_IAM_ROLE_NAME, region)

        role_exists = role is not None
        if role is None:
            iam = _resource("iam", region)
            iam.create_role(
                RoleName=ANYSCALE_IAM_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(anyscale_aws_iam_role_policy),
            )
            role = _get_role(ANYSCALE_IAM_ROLE_NAME, region)

        assert role is not None, "Failed to create IAM role!"

        role.attach_policy(PolicyArn=AMAZON_EC2_FULL_ACCESS_POLICY_ARN)
        role.attach_policy(PolicyArn=AMAZON_IAM_FULL_ACCESS_POLICY_ARN)

        self.log.info(f"Using IAM role {role.arn}")

        created_cloud = self.api_client.create_cloud_api_v2_clouds_post(
            write_cloud=WriteCloud(
                provider="AWS", region=region, credentials=role.arn, name=name,
            )
        )

        # NOTE: If we are modifying an existing Role that does not have External IDs, we
        # cannot add an ExternalID check to the policy because it could break old clouds.
        if (
            role_exists
            and number_of_external_ids_in_policy(role.assume_role_policy_document) == 0
        ):
            return

        # NOTE: We update this _after_ cloud creation because this External ID MUST
        # come from Anyscale, not the customer. We are using the `cloud_id` as it is unique per cloud.
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html
        new_policy = _update_external_ids_for_policy(
            role.assume_role_policy_document, created_cloud.result.id
        )

        role.AssumeRolePolicy().update(PolicyDocument=json.dumps(new_policy))

    def setup_aws_ray_role(self, region: str, role_name: str) -> None:
        iam = boto3.resource("iam", region_name=region)

        role = _get_role(role_name, region)
        if role is None:
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": {
                            "Effect": "Allow",
                            "Principal": {"Service": ["ec2.amazonaws.com"]},
                            "Action": "sts:AssumeRole",
                        },
                    }
                ),
            )

            role = _get_role(role_name, region)

        role.attach_policy(PolicyArn=AMAZON_ECR_READONLY_ACCESS_POLICY_ARN)
        # Modified permissions from Ray (no EC2FullAccess)
        role.attach_policy(PolicyArn=AMAZON_S3_FULL_ACCESS_POLICY_ARN)

    def setup_aws_k8s_cloud(self, region: str, name: str, yes: bool) -> None:
        confirm(
            "\nYou are about to give Anyscale access to EC2, EKS, and IAM "
            "in your AWS account.\n\nContinue?",
            yes,
        )

        # Create cloud in DB.
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        cloud_response: CloudResponse = self.api_client.create_cloud_api_v2_clouds_post(
            write_cloud=WriteCloud(
                name=name,
                provider=CloudProviders.AWS,
                region=region,
                credentials=account_id,
                is_k8s=True,
                is_aioa=False,
            )
        )
        created_cloud: Cloud = cloud_response.result

        # Grant Anyscale access.
        cloud_credentials = json.loads(created_cloud.credentials)
        # TODO: this should ideally be a model, but we don't expose this one in the client.
        if not isinstance(cloud_credentials, dict):
            raise TypeError("unable to interpret credentials of created cloud")
        access_role_arn = cloud_credentials.get("customer_cloud_access_role_arn")
        if not isinstance(access_role_arn, str):
            raise TypeError(f"invalid access role in created cloud: {access_role_arn}")
        _, _, access_role_name = access_role_arn.partition("/")
        if not access_role_name:
            raise ValueError("no access role name in credentials for created cloud")
        anyscale_role_arn = cloud_credentials.get("anyscale_cloud_access_role_arn")
        if not isinstance(anyscale_role_arn, str):
            raise TypeError(
                f"invalid Anyscale role in created cloud: {anyscale_role_arn}"
            )
        iam = _resource(name="iam", region=region)
        for _ in range(ROLE_CREATION_RETRIES):
            try:
                role = iam.create_role(
                    RoleName=access_role_name,
                    AssumeRolePolicyDocument=json.dumps(
                        {
                            "Version": "2012-10-17",
                            "Statement": {
                                "Sid": "1",
                                "Effect": "Allow",
                                "Principal": {"AWS": anyscale_role_arn},
                                "Action": "sts:AssumeRole",
                                "Condition": {
                                    "StringEquals": {"sts:ExternalId": created_cloud.id}
                                },
                            },
                        }
                    ),
                )
            except botocore.exceptions.ClientError:
                time.sleep(ROLE_CREATION_INTERVAL_SECONDS)
                continue
            else:
                break
        anyscale_iam_policy = iam.Policy(
            arn=f"arn:aws:iam::{account_id}:policy/{ANYSCALE_IAM_ACCESS_POLICY_NAME}"
        )
        try:
            anyscale_iam_policy.load()
        except botocore.exceptions.ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "NoSuchEntity":
                raise
            anyscale_iam_policy = iam.create_policy(
                PolicyName="AnyscaleIAMAccess",
                PolicyDocument=json.dumps(ANYSCALE_IAM_ACCESS_POLICY_DOCUMENT),
            )
        eks_full_access_policy = iam.Policy(
            arn=f"arn:aws:iam::{account_id}:policy/{EKS_FULL_ACCESS_POLICY_NAME}"
        )
        try:
            eks_full_access_policy.load()
        except botocore.exceptions.ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "NoSuchEntity":
                raise
            eks_full_access_policy = iam.create_policy(
                PolicyName="EKSFullAccess",
                PolicyDocument=json.dumps(EKS_FULL_ACCESS_POLICY_DOCUMENT),
                Description="This policy gives the role full access to EKS.",
            )
        role.attach_policy(PolicyArn=anyscale_iam_policy.arn)
        role.attach_policy(PolicyArn=eks_full_access_policy.arn)
        role.attach_policy(PolicyArn=AMAZON_VPC_FULL_ACCESS_POLICY_ARN)
        role.attach_policy(PolicyArn=AMAZON_EC2_FULL_ACCESS_POLICY_ARN)
        role.attach_policy(PolicyArn=AMAZON_CLOUDWATCH_FULL_ACCESS_POLICY_ARN)
        role.attach_policy(PolicyArn=AMAZON_ROUTE53_FULL_ACCESS_POLICY_ARN)

        self.log.info(
            "Cloud creation in progress. Your cloud should be available in 20-30 minutes."
        )
        self.log.info(
            f"If you want to remove this cloud, run `anyscale cloud delete -n {name}."
        )
        self.log.warning(
            f"If you delete the role {access_role_name} without deleting the cloud, there "
            "might remain resources running in your account."
        )

    def update_cloud_config(
        self,
        cloud_name: Optional[str],
        cloud_id: Optional[str],
        max_stopped_instances: int,
    ) -> None:
        """Updates a cloud's configuration by name or id.

        Currently the only supported option is "max_stopped_instances."
        """

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        self.api_client.update_cloud_config_api_v2_clouds_cloud_id_config_put(
            cloud_id=cloud_id,
            cloud_config=CloudConfig(max_stopped_instances=max_stopped_instances),
        )

        self.log.info(f"Updated config for cloud '{cloud_name}' to:")
        self.log.info(self.get_cloud_config(cloud_name=None, cloud_id=cloud_id))

    def get_cloud_config(
        self, cloud_name: Optional[str] = None, cloud_id: Optional[str] = None,
    ) -> str:
        """Get a cloud's current JSON configuration."""

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        return str(get_cloud_json_from_id(cloud_id, self.api_client)["config"])

    def set_default_cloud(
        self, cloud_name: Optional[str], cloud_id: Optional[str],
    ) -> None:
        """
        Sets default cloud for caller's organization. This operation can only be performed
        by organization admins, and the default cloud must have organization level
        permissions.
        """

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        self.api_client.update_default_cloud_api_v2_organizations_update_default_cloud_post(
            cloud_id=cloud_id
        )

        self.log.info(f"Updated default cloud to {cloud_name}")
