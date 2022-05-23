from pathlib import Path
from typing import Optional
from data_engineering_pulumi_components.aws.lambdas.lambda_handlers.upload_ import (
    upload_,
)

from data_engineering_pulumi_components.utils import Tagger

from pulumi import AssetArchive, ComponentResource, FileArchive, ResourceOptions
import pulumi_aws as aws
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, Permission


class UploadObjectFunction(ComponentResource):
    def __init__(
        self,
        name: str,
        tagger: Tagger,
        bucket_name: str,
        accountid: str,
        region: str,
        api: aws.apigateway,
        resource_path: str,
        lambda_role_arn: str,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provides a Lambda function that allows file upload
        using presigned url
        Parameters
        ----------
        name : str
            The name of the resource.
        tagger : Tagger
            A tagger resource.
        bucket_name: str, : Bucket
            The bucket to upload data to.
        api :aws.apigateway,
                The Api which use the lambda to upload
        accountid: str,
            The account number for creation of resource
        region: str,
            Region the resources to be created
        resource_path: str,
            Api Resource path
        lambda_role_arn:str
            Upload Lambda role arn
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:UploadObjectFunction",
            name=name,
            props=None,
            opts=opts,
        )

        self._bucketname = bucket_name
        self._region = region
        self._accountid = accountid
        self._resource_path = resource_path
        self._lambda_role_arn = lambda_role_arn

        self.function = Function(
            resource_name=f"{name}-function",
            code=AssetArchive(
                assets={
                    ".": FileArchive(path=str(Path(upload_.__file__).absolute().parent))
                }
            ),
            description="Generates presigned url and allows object upload to bucket ",
            role=self._lambda_role_arn,
            handler="upload_.handler",
            environment=FunctionEnvironmentArgs(
                variables={
                    "bucketname": f"{bucket_name}",
                }
            ),
            runtime="python3.8",
            tags=tagger.create_tags(f"{name}-upload"),
            timeout=300,
            opts=ResourceOptions(parent=self),
        )

        self._permission = Permission(
            resource_name=f"{name}-permission",
            principal="apigateway.amazonaws.com",
            action="lambda:InvokeFunction",
            function=self.function.arn,
            source_arn=api.id.apply(
                lambda api_id: f"arn:aws:execute-api:{self._region}:"
                + f"{self._accountid}:{api_id}/*/GET/{self._resource_path}"
            ),
            opts=ResourceOptions(parent=self.function),
        )
