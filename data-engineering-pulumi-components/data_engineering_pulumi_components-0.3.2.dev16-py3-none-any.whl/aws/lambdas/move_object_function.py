import json
from pathlib import Path
from typing import Optional, Union

from data_engineering_pulumi_components.aws.buckets.bucket import Bucket
from data_engineering_pulumi_components.aws.lambdas.lambda_handlers.move import move
from data_engineering_pulumi_components.utils import Tagger, BucketDetails
from pulumi import AssetArchive, ComponentResource, FileArchive, Output, ResourceOptions
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, Permission
from pulumi_aws.s3 import BucketNotification, BucketNotificationLambdaFunctionArgs


class MoveObjectFunction(ComponentResource):
    def __init__(
        self,
        destination_bucket: Union[Bucket, str],
        name: str,
        source_bucket: Bucket,
        tagger: Tagger,
        prefix: str = None,
        opts: Optional[ResourceOptions] = None,
        create_notification: bool = True,
    ) -> None:
        """
        Provides a Lambda function that copies objects from a source bucket to a
        destination bucket and then deletes the original object.

        Parameters
        ----------
        destination_bucket : Bucket, str
            The bucket to move data to, if created in this stack. Or if the bucket
            already exists, its name as a string.
        name : str
            The name of the resource.
        source_bucket : Bucket
            The bucket to move data from.
        tagger : Tagger
            A tagger resource.
        prefix : str, optional
            If included, only move files from this 'folder'.
            Don't include the trailing slash: 'project-name', not 'project-name/'
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        create_notification : bool
            If True, create a BucketNotification to run the Lambda when an object is
            created in the source bucket. If False, don't create a BucketNotification.
            If you have separate Lambdas for different prefixes in the same bucket,
            you'll need to set this to False and create a combined BucketNotification
            separately.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:MoveObjectFunction",
            name=name,
            props=None,
            opts=opts,
        )

        # If destination bucket already exists, create a BucketDetails from its name
        if isinstance(destination_bucket, str):
            destination_bucket = BucketDetails(destination_bucket)

        self._role = Role(
            resource_name=f"{name}-role",
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
            name=f"{name}-move",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-move"),
            opts=ResourceOptions(parent=self),
        )
        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-role-policy",
            name="s3-access",
            policy=Output.all(source_bucket.arn, destination_bucket.arn, prefix).apply(
                lambda args: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "GetDeleteSourceBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[0]}/{args[2]}/*"]
                                if args[2]
                                else [f"{args[0]}/*"],
                                "Action": ["s3:GetObject*", "s3:DeleteObject*"],
                            },
                            {
                                "Sid": "PutDestinationBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[1]}/*"],
                                "Action": ["s3:PutObject*"],
                            },
                        ],
                    }
                )
            ),
            role=self._role.id,
            opts=ResourceOptions(parent=self._role),
        )
        self._rolePolicyAttachment = RolePolicyAttachment(
            resource_name=f"{name}-role-policy-attachment",
            policy_arn=(
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            ),
            role=self._role.name,
            opts=ResourceOptions(parent=self._role),
        )
        self._function = Function(
            resource_name=f"{name}-function",
            code=AssetArchive(
                assets={
                    ".": FileArchive(path=str(Path(move.__file__).absolute().parent))
                }
            ),
            description=Output.all(source_bucket.name, destination_bucket.name).apply(
                lambda args: f"Moves data from {args[0]} to {args[1]}"
            ),
            environment=Output.all(destination_bucket.name).apply(
                lambda args: FunctionEnvironmentArgs(
                    variables={"DESTINATION_BUCKET": args[0]}
                )
            ),
            handler="move.handler",
            name=f"{name}-move",
            role=self._role.arn,
            runtime="python3.8",
            tags=tagger.create_tags(f"{name}-move"),
            timeout=300,
            opts=ResourceOptions(parent=self),
        )
        self._permission = Permission(
            resource_name=f"{name}-permission",
            action="lambda:InvokeFunction",
            function=self._function.arn,
            principal="s3.amazonaws.com",
            source_arn=source_bucket.arn,
            opts=ResourceOptions(parent=self._function),
        )
        if create_notification:
            self._bucketNotification = BucketNotification(
                resource_name=f"{name}-bucket-notification",
                bucket=source_bucket.id,
                lambda_functions=[
                    BucketNotificationLambdaFunctionArgs(
                        events=["s3:ObjectCreated:*"],
                        lambda_function_arn=self._function.arn,
                        filter_prefix=f"{prefix}/" if prefix else None,
                    )
                ],
                opts=ResourceOptions(parent=self._permission),
            )
