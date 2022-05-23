from typing import Optional

from data_engineering_pulumi_components.aws.buckets.bucket import (
    Bucket,
    BucketPutPermissionsArgs,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ResourceOptions


class LandingBucket(Bucket):
    def __init__(
        self,
        name: str,
        aws_arn_for_put_permission: str,
        tagger: Tagger,
        cors_allowed_headers: list = None,
        cors_allowed_origins: list = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            name=name + "-landing",
            t="data-engineering-pulumi-components:aws:LandingBucket",
            put_permissions=[
                BucketPutPermissionsArgs(
                    aws_arn_for_put_permission, allow_anonymous_users=False
                )
            ],
            cors_rules=self.add_cors_rules(
                cors_allowed_headers=cors_allowed_headers,
                cors_allowed_origins=cors_allowed_origins,
            )
            if (cors_allowed_headers and cors_allowed_origins) is not None
            else None,
            tagger=tagger,
            opts=opts,
        )
