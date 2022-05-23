import json
from pathlib import Path
from typing import Optional
from data_engineering_pulumi_components.aws.lambdas.lambda_handlers.authorise_ import (
    authorise_,
)

from data_engineering_pulumi_components.utils import Tagger
from pulumi import AssetArchive, ComponentResource, FileArchive, ResourceOptions
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment
import pulumi_aws as aws
from pulumi_aws.apigateway import Authorizer
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, Permission


class AuthorisationFunction(ComponentResource):
    def __init__(
        self,
        name: str,
        tagger: Tagger,
        api: aws.apigateway,
        authorisationToken: str,
        accountid: str,
        region: str,
        resource_path: str,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provides a Lambda function that validates, authorises token
        passed from api call and grants permission to invoke
        and execute specified API

        Parameters
        ----------
        destination_bucket : Bucket
            The bucket to copy data to.
        name : str
            The name of the resource.
        source_bucket : Bucket
            The bucket to copy data from.
        tagger : Tagger
            A tagger resource.
        api :aws.apigateway,
            The Api which use the lambda to authorise
        accountid: str,
            The account number for creation of resource
        region: str,
            Region the resources to be created
        resource_path: str,
            Api Resource path
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:AuthorisationObjectFunction",
            name=name,
            props=None,
            opts=opts,
        )

        self._authorisationToken = authorisationToken
        self._region = region
        self._accountid = accountid
        self._resource_path = resource_path

        self._lambdarole = Role(
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
            name=f"{name}-assume-lambda-role",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-assume-lambda-role"),
            opts=ResourceOptions(parent=self),
        )

        self._function = Function(
            resource_name=f"{name}-function",
            code=AssetArchive(
                assets={
                    ".": FileArchive(
                        path=str(Path(authorise_.__file__).absolute().parent)
                    )
                }
            ),
            description="Validates and authorises the header token",
            role=self._lambdarole.arn,
            handler="authorise_.handler",
            environment=FunctionEnvironmentArgs(
                variables={
                    "authorisationToken": f"{authorisationToken}",
                    "api_link": api.id.apply(
                        lambda apid_id: f"arn:aws:execute-api:{self._region}:"
                        + f"{self._accountid}:{apid_id}/*/GET/{self._resource_path}"
                    ),
                }
            ),
            runtime="python3.8",
            tags=tagger.create_tags(f"{name}-function"),
            timeout=300,
            opts=ResourceOptions(parent=self),
        )

        self._invocation_role = Role(
            resource_name=f"{name}-invocation_role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Principal": {"Service": "apigateway.amazonaws.com"},
                            "Effect": "Allow",
                            "Sid": "",
                        },
                    ],
                }
            ),
            name=f"{name}-api-invocation-role",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-api-invocation-role"),
            opts=ResourceOptions(parent=self),
        )

        # ARN of the function which is allowed to be invoked
        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-role-policy",
            name=f"{name}-lambda-invoke",
            policy=self._function.arn.apply(
                lambda arn: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Action": "lambda:InvokeFunction",
                                "Effect": "Allow",
                                "Resource": f"{arn}",
                            }
                        ],
                    }
                )
            ),
            role=self._invocation_role.id,
            opts=ResourceOptions(parent=self._invocation_role),
        )

        self._rolePolicyAttachment = RolePolicyAttachment(
            resource_name=f"{name}-role-policy-attachment",
            policy_arn=(
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            ),
            role=self._invocation_role.name,
            opts=ResourceOptions(parent=self._invocation_role),
        )

        self.authorizer = Authorizer(
            resource_name=f"{name}-authoriser",
            rest_api=api.id,
            authorizer_uri=self._function.invoke_arn,
            type="REQUEST",
            authorizer_credentials=self._invocation_role.arn,
            authorizer_result_ttl_in_seconds=0,
            identity_source="method.request.header.authorisationToken",
        )

        # Allow source_arn to invoke lambda
        self._permission = Permission(
            resource_name=f"{name}-permission",
            principal="apigateway.amazonaws.com",
            action="lambda:InvokeFunction",
            function=self._function.arn,
            source_arn=api.id.apply(
                lambda api_id: f"arn:aws:execute-api:{self._region}:"
                + f"{self._accountid}:{api_id}/*/GET/{self._resource_path}"
            ),
            opts=ResourceOptions(parent=self._function),
        )
