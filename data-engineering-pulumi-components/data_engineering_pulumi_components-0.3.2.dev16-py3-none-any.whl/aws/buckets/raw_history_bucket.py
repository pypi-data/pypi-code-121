from typing import Optional

from data_engineering_pulumi_components.aws.buckets.bucket import Bucket
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ResourceOptions


class RawHistoryBucket(Bucket):
    def __init__(
        self, name: str, tagger: Tagger, opts: Optional[ResourceOptions] = None
    ) -> None:
        super().__init__(
            name=name + "-raw-history",
            tagger=tagger,
            t="data-engineering-pulumi-components:aws:RawHistoryBucket",
            versioning={"enabled": True},
            opts=opts,
        )
