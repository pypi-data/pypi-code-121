from typing import Optional

from data_engineering_pulumi_components.aws.buckets.bucket import Bucket
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ResourceOptions
import pulumi_aws as aws


class FailBucket(Bucket):
    def __init__(
        self, name: str, tagger: Tagger, opts: Optional[ResourceOptions] = None
    ) -> None:
        super().__init__(
            name=name + "-fail",
            tagger=tagger,
            t="data-engineering-pulumi-components:aws:FailBucket",
            lifecycle_rules=[
                aws.s3.BucketLifecycleRuleArgs(
                    enabled=True,
                    abort_incomplete_multipart_upload_days=14,
                    expiration=aws.s3.BucketLifecycleRuleExpirationArgs(
                        expired_object_delete_marker=True
                    ),
                    noncurrent_version_expiration=(
                        aws.s3.BucketLifecycleRuleNoncurrentVersionExpirationArgs(
                            days=14,
                        )
                    ),
                )
            ],
            opts=opts,
        )
