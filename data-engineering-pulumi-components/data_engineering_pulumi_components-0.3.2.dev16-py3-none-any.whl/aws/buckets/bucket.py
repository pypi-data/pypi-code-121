import json
import re
from typing import Optional, Sequence, Union

import pulumi_aws.s3 as s3
from pulumi_aws.s3 import BucketCorsRuleArgs
from data_engineering_pulumi_components.utils import (
    Tagger,
    validate_principal,
    is_anonymous_user,
)
from pulumi import ComponentResource, ResourceOptions, Output


class InvalidBucketNameError(Exception):
    pass


class AnonymousUserError(Exception):
    pass


class BucketPutPermissionsArgs:
    def __init__(
        self,
        principal: Union[str, Output],
        paths: Optional[Sequence[str]] = None,
        allow_anonymous_users: Optional[bool] = True,
    ) -> None:
        # We can't validate principals passed as Output types – these will always only
        # come from Pulumi resources so they should always be valid and shouldn't be
        # anonymous users
        if not isinstance(principal, Output):
            validate_principal(principal)
            if is_anonymous_user(principal) and not allow_anonymous_users:
                raise AnonymousUserError("anonymous users are not allowed")
        self.principal = principal
        if paths:
            if not isinstance(paths, list):
                raise TypeError("paths must be of type list")
            for path in paths:
                if not isinstance(path, str):
                    raise TypeError("Each path must be of type str")
                if not path.startswith("/") or not path.endswith("/"):
                    raise ValueError("Each path must start and end with '/'")
        self.paths = paths


def _bucket_name_is_valid(name: str) -> bool:
    """
    Checks if an S3 bucket name is valid.

    See https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html

    Parameters
    ----------
    name : str
        The name of the bucket.

    Returns
    -------
    bool
        If the name is valid.
    """
    match = re.match(
        pattern=(
            # ensure name is between 3 and 63 characters long
            r"(?=^.{3,63}$)"
            # ensure name is not formatted like an IP address
            r"(?!^(\d+\.)+\d+$)"
            # match zero or more labels followed by a single period
            r"(^(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*"
            # ensure final label doesn't end in a period or dash
            r"([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$)"
        ),
        string=name,
    )
    if match:
        return True
    else:
        return False


class Bucket(ComponentResource):
    def __init__(
        self,
        name: str,
        tagger: Tagger,
        cors_rules: BucketCorsRuleArgs = None,
        t: Optional[str] = None,
        lifecycle_rules: Sequence[s3.BucketLifecycleRuleArgs] = None,
        put_permissions: Optional[Sequence[BucketPutPermissionsArgs]] = None,
        versioning: Optional[s3.BucketVersioningArgs] = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        if t is None:
            t = "data-engineering-pulumi-components:aws:Bucket"
        super().__init__(
            t=t,
            name=name,
            props=None,
            opts=opts,
        )
        if not isinstance(name, str):
            raise TypeError("name must be of type str")
        if not isinstance(tagger, Tagger):
            raise TypeError("tagger must be of type Tagger")

        if not _bucket_name_is_valid(name=name):
            raise InvalidBucketNameError("name is not valid")

        self._name = name

        self._bucket = s3.Bucket(
            resource_name=f"{name}-bucket",
            acl=s3.CannedAcl.PRIVATE,
            cors_rules=cors_rules,
            bucket=name,
            force_destroy=True,
            lifecycle_rules=lifecycle_rules,
            server_side_encryption_configuration={
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": "AES256"
                    }
                }
            },
            tags=tagger.create_tags(name=name),
            versioning=versioning,
            opts=ResourceOptions(parent=self),
        )
        self._bucketPublicAccessBlock = s3.BucketPublicAccessBlock(
            resource_name=f"{name}-bucket-public-access-block",
            bucket=self._bucket.id,
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True,
            opts=ResourceOptions(parent=self._bucket),
        )

        if put_permissions:
            self.add_permissions(put_permissions=put_permissions)

        outputs = {
            "arn": self._bucket.arn,
            "id": self._bucket.id,
            "name": self._bucket.bucket,
        }

        for name, value in outputs.items():
            setattr(self, name, value)

        self.register_outputs(outputs)

    def _get_policy(self, args):
        bucket_arn = args.pop("bucket_arn")
        block_access = args.pop("block_access")

        all_principals = []
        statements = []
        for item in args.values():
            principal = item["principal"]
            paths = item["paths"]
            all_principals.append(principal)
            statements.append(
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": [principal]},
                    "Action": ["s3:PutObject", "s3:PutObjectAcl"],
                    "Resource": [bucket_arn + path + "*" for path in paths]
                    if paths
                    else [bucket_arn + "/*"],
                }
            )
        statements.extend(
            [
                {
                    "Effect": "Deny",
                    "Principal": {"AWS": all_principals},
                    "Action": ["s3:PutObject"],
                    "Resource": [bucket_arn + "/*"],
                    "Condition": {
                        "StringNotEquals": {
                            "s3:x-amz-acl": ["bucket-owner-full-control"],
                        },
                    },
                },
                {
                    "Effect": "Deny",
                    "Principal": {"AWS": all_principals},
                    "Action": ["s3:PutObject"],
                    "Resource": [bucket_arn + "/*"],
                    "Condition": {
                        "StringNotEquals": {
                            "s3:x-amz-server-side-encryption": ["AES256"],
                        },
                    },
                },
                {
                    "Effect": "Deny",
                    "Principal": {"AWS": all_principals},
                    "Action": ["s3:PutObject"],
                    "Resource": [bucket_arn + "/*"],
                    "Condition": {
                        "Null": {"s3:x-amz-server-side-encryption": ["true"]},
                    },
                },
            ]
        )
        if block_access:
            statements.extend(
                [
                    {
                        "Effect": "Deny",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:*",
                        "Resource": [bucket_arn + path for path in paths]
                        + [bucket_arn + path + "*" for path in paths]
                        if paths
                        else [bucket_arn, bucket_arn + "/*"],
                        "Condition": {"StringLike": {"aws:PrincipalArn": "*/alpha_*"}},
                    }
                ]
            )

        return json.dumps({"Version": "2012-10-17", "Statement": statements})

    def _get_policy_glue(self, args):
        bucket_arn = args.pop("bucket_arn")

        all_principals = []
        statements = []
        for item in args.values():
            principal = item["principal"]
            paths = item["paths"]
            all_principals.append(principal)
            statements.append(
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": [principal]},
                    "Action": [
                        "s3:Get*",
                        "s3:Put*",
                        "s3:Delete*",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListBucketVersions",
                        "s3:ListMultipartUploadParts",
                    ],
                    "Resource": [bucket_arn + path for path in paths]
                    + [bucket_arn + path + "*" for path in paths]
                    if paths
                    else [bucket_arn, bucket_arn + "/*"],
                }
            )

        return json.dumps({"Version": "2012-10-17", "Statement": statements})

    def add_permissions(
        self,
        put_permissions: Sequence[BucketPutPermissionsArgs],
        glue_permissions: bool = False,
        block_access: bool = False,
    ):
        if not getattr(self, "_put_permissions", None):
            self._put_permissions = put_permissions
            if glue_permissions:
                policy = Output.all(
                    bucket_arn=self._bucket.arn,
                    **{str(i): item.__dict__ for i, item in enumerate(put_permissions)},
                ).apply(self._get_policy_glue)
            else:
                policy = Output.all(
                    bucket_arn=self._bucket.arn,
                    block_access=block_access,
                    **{str(i): item.__dict__ for i, item in enumerate(put_permissions)},
                ).apply(self._get_policy)

            self._bucketPolicy = s3.BucketPolicy(
                resource_name=f"{self._name}-bucket-policy",
                bucket=self._bucket.id,
                policy=policy,
                opts=ResourceOptions(parent=self._bucket),
            )
        else:
            raise Exception("put_permissions are already set")

    def add_cors_rules(
        self,
        cors_allowed_headers: list,
        cors_allowed_origins: list,
    ):
        return [
            BucketCorsRuleArgs(
                allowed_headers=cors_allowed_headers,
                allowed_methods=[
                    "PUT",
                    "POST",
                ],
                allowed_origins=cors_allowed_origins,
                expose_headers=[
                    "x-amz-server-side-encryption",
                    "x-amz-request-id",
                    "x-amz-id-2",
                ],
                max_age_seconds=3000,
            )
        ]
