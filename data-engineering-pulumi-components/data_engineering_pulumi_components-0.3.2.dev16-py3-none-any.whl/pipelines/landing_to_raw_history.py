from typing import Optional

from data_engineering_pulumi_components.aws import (
    LandingBucket,
    RawHistoryBucket,
    FailBucket,
    ValidateMoveObjectFunction,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions


class LandingToRawHistoryPipeline(ComponentResource):
    def __init__(
        self,
        name: str,
        aws_arn_for_put_permission: str,
        tagger: Tagger,
        slack_channel: str,
        slack_webhook_url: str,
        move_on_object_create: bool = True,
        move_on_schedule: bool = True,
        schedule: str = None,
        cors_allowed_headers: list = None,
        cors_allowed_origins: list = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            t=(
                "data-engineering-pulumi-components:pipelines:"
                "LandingToRawHistoryPipeline"
            ),
            name=name,
            props=None,
            opts=opts,
        )

        self._landing_bucket = LandingBucket(
            name=name,
            aws_arn_for_put_permission=aws_arn_for_put_permission,
            tagger=tagger,
            cors_allowed_headers=cors_allowed_headers,
            cors_allowed_origins=cors_allowed_origins,
            opts=ResourceOptions(parent=self),
        )

        self._raw_history_bucket = RawHistoryBucket(
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self),
        )

        self._fail_bucket = FailBucket(
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self),
        )

        self._validate_move_object_function = ValidateMoveObjectFunction(
            pass_bucket=self._raw_history_bucket,
            fail_bucket=self._fail_bucket,
            name=name,
            source_bucket=self._landing_bucket,
            opts=ResourceOptions(
                parent=self,
                depends_on=[
                    self._raw_history_bucket,
                    self._fail_bucket,
                    self._landing_bucket,
                ],
            ),
            trigger_on_object_create=move_on_object_create,
            trigger_on_schedule=move_on_schedule,
            schedule=schedule,
            tagger=tagger,
            slack_channel=slack_channel,
            slack_webhook_url=slack_webhook_url,
        )
