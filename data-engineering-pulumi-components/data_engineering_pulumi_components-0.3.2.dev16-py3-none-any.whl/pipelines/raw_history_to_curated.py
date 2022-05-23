from typing import Optional
from data_engineering_pulumi_components.aws.glue.glue_job import GlueComponent
from data_engineering_pulumi_components.aws import (
    BucketPutPermissionsArgs,
    CopyObjectFunction,
    CuratedBucket,
    RawHistoryBucket,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions
from pulumi_aws import Provider
from pulumi_aws.glue import CatalogDatabase
import os
from pathlib import Path


class RawHistoryToCuratedPipeline(ComponentResource):
    def __init__(
        self,
        name: str,
        raw_history_bucket: RawHistoryBucket,
        tagger: Tagger,
        add_tables_to_db: bool = False,
        default_provider: Optional[Provider] = None,
        stack_provider: Optional[Provider] = None,
        opts: Optional[ResourceOptions] = None,
        db_refresh_schedule: bool = True,
        db_refresh_on_create: bool = False,
        block_access: bool = True,
        multiple_db_in_bucket: str = "False",
    ) -> None:
        super().__init__(
            t=(
                "data-engineering-pulumi-components:pipelines:"
                "RawHistoryToCuratedPipeline"
            ),
            name=name,
            props=None,
            opts=opts,
        )
        self._curatedBucket = CuratedBucket(
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self, provider=stack_provider),
        )
        if not add_tables_to_db:
            self._copyObjectFunction = CopyObjectFunction(
                destination_bucket=self._curatedBucket,
                name=name,
                source_bucket=raw_history_bucket,
                tagger=tagger,
                opts=ResourceOptions(parent=self),
            )

            self._curatedBucket.add_permissions(
                put_permissions=[
                    BucketPutPermissionsArgs(
                        principal=self._copyObjectFunction._role.arn
                    )
                ],
                block_access=block_access,
            )
        else:
            # create database of multiple_db_in_bucket option is not true
            if multiple_db_in_bucket == "False":
                db_name = name.replace("-", "_")
                self._database = CatalogDatabase(
                    resource_name=f"{name}-database",
                    description=f"A Glue Database for tables from {name}",
                    name=f"{db_name}",
                    opts=ResourceOptions(provider=default_provider),
                )

            self._glueMoveJob = GlueComponent(
                destination_bucket=self._curatedBucket,
                name=name,
                source_bucket=raw_history_bucket,
                tagger=tagger,
                glue_script=(
                    os.path.join(
                        Path(__file__).parents[1],
                        "aws/glue/glue_move_script.py",
                    )
                ),
                glue_inputs={
                    "--source_bucket": raw_history_bucket._name,
                    "--destination_bucket": self._curatedBucket._name,
                    "--stack_name": name,
                    "--multiple_db_in_bucket": multiple_db_in_bucket,
                },
                default_provider=default_provider,
                stack_provider=stack_provider,
                opts=ResourceOptions(
                    parent=self,
                    depends_on=[self._curatedBucket],
                ),
                trigger_on_demand=db_refresh_on_create,
                trigger_on_schedule=db_refresh_schedule,
            )

            raw_history_bucket.add_permissions(
                put_permissions=[
                    BucketPutPermissionsArgs(principal=self._glueMoveJob._role.arn)
                ],
                glue_permissions=True,
            )

            self._curatedBucket.add_permissions(
                put_permissions=[
                    BucketPutPermissionsArgs(principal=self._glueMoveJob._role.arn)
                ],
                glue_permissions=True,
            )
