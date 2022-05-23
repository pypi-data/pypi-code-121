import json
from typing import Optional

from data_engineering_pulumi_components.utils import Tagger

from pulumi import ComponentResource, ResourceOptions
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment


class CreateListBucketRole(ComponentResource):
    def __init__(
        self,
        name: str,
        tagger: Tagger,
        bucket_name: str,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Role to allow lambda to list databases and tables in an s3 bucket.

        name : str
            The name of the resource.
        tagger : Tagger
            A tagger resource.
        bucket_name: str,
            Name of the bucket to enble upload permission
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """

        super().__init__(
            t="data-engineering-pulumi-components:aws:CreateListRole",
            name=name,
            props=None,
            opts=opts,
        )

        self._bucketname = bucket_name
        self.lambdarole = Role(
            resource_name=f"{name}-lambda-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
            name=f"{name}-lambda-role",
            path="/service-role/",
            tags=tagger.create_tags(name=f"{name}-lambda-role"),
            opts=ResourceOptions(parent=self),
        )

        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-list-policy",
            name=f"{name}-lambda-list-policy",
            policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": [
                                "s3:ListBucket",
                            ],
                            "Resource": f"arn:aws:s3:::{self._bucketname}",
                            "Effect": "Allow",
                        }
                    ],
                }
            ),
            role=self.lambdarole.id,
            opts=ResourceOptions(parent=self.lambdarole),
        )
        self._rolePolicyAttachment = RolePolicyAttachment(
            resource_name=f"{name}-role-policy-attachment",
            policy_arn=(
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            ),
            role=self.lambdarole.name,
        )
