from typing import Optional

from data_engineering_pulumi_components.aws.buckets.bucket import Bucket
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ResourceOptions
from pulumi_aws.s3 import (
    BucketLifecycleRuleArgs,
    BucketLifecycleRuleExpirationArgs,
    BucketLifecycleRuleNoncurrentVersionExpirationArgs,
    BucketLifecycleRuleNoncurrentVersionTransitionArgs,
)


class PulumiBackendBucket(Bucket):
    def __init__(
        self, name: str, tagger: Tagger, opts: Optional[ResourceOptions] = None
    ) -> None:
        super().__init__(
            name=name + "-pulumi-backend",
            t="data-engineering-pulumi-components:aws:PulumiBackendBucket",
            tagger=tagger,
            lifecycle_rules=[
                BucketLifecycleRuleArgs(
                    enabled=True,
                    expiration=BucketLifecycleRuleExpirationArgs(days=30),
                    id="pulumi-backups",
                    noncurrent_version_expiration=(
                        BucketLifecycleRuleNoncurrentVersionExpirationArgs(days=60)
                    ),
                    noncurrent_version_transitions=[
                        BucketLifecycleRuleNoncurrentVersionTransitionArgs(
                            storage_class="GLACIER", days=0
                        )
                    ],
                    prefix=".pulumi/backups/",
                ),
                BucketLifecycleRuleArgs(
                    enabled=True,
                    expiration=BucketLifecycleRuleExpirationArgs(days=30),
                    id="pulumi-history",
                    noncurrent_version_expiration=(
                        BucketLifecycleRuleNoncurrentVersionExpirationArgs(days=60)
                    ),
                    noncurrent_version_transitions=[
                        BucketLifecycleRuleNoncurrentVersionTransitionArgs(
                            storage_class="GLACIER", days=0
                        )
                    ],
                    prefix=".pulumi/history/",
                ),
            ],
            versioning={"enabled": True},
            opts=ResourceOptions(protect=True),
        )
