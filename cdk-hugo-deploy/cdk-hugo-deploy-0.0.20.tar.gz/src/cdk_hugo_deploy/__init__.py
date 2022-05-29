'''
# CDK-Hugo-Deploy

This is an AWS CDK Construct for easily deploying [Hugo](https://gohugo.io/) Static websites to AWS S3 behind SSL/Cloudfront.

## Usage

Before deploying, run the `hugo` command in your Hugo project to generate a built site in the `public` directory.

## Typescript

```python
import { App, Stack, StackProps } from 'aws-cdk-lib';
import { HugoDeploy } from 'cdk-hugo-deploy';

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    new HugoDeploy(this, 'HugoDeploy', {
      publicDir: 'path/to/hugo-project/public',
      domainName: 'example.com'  // Domain you already have a hosted zone for
    });
}
```

## Python

```python
from constructs import Construct
from aws_cdk import Stack
from cdk_hugo_deploy import HugoDeploy

class MyStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        HugoDeploy(self, "HugoDeploy",
            public_dir="path/to/hugo-project/public",
            domain_name="example.com"
        )
```

## Prerequisites

Assumes that there is already a Route53 hosted zone for `domainName` that can be [looked up](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_route53.HostedZone.html#static-fromwbrlookupscope-id-query)

## Why this construct?

Other constructs for deploying Single Page Applicationis (SPA) such as [CDK-SPA-Deploy](https://github.com/nideveloper/CDK-SPA-Deploy) don't account for how Hugo handles paths that end in `/`.

This construct includes a [Cloudfront Function](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html) to [rewrite paths](src/hugoPaths.js) to ensure `/path/to/page/` will request `/path/to/page/index.html` from the S3 Origin.

## Contributing

Please open an [issue](https://github.com/maafk/cdk-hugo-deploy/issues) with any updates/features you'd like on this
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import constructs


class HugoDeploy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-hugo-deploy.HugoDeploy",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        public_dir: builtins.str,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: Domain name of the site deploying to. You should already have a hosted zone in the account you're deploying to with this domain name
        :param public_dir: Path to Hugo public directory, which is generated after running the ``hugo`` command. By default, this will be the ``public`` directory in your hugo project
        :param region: Region deploying to. Default: - us-east-1
        '''
        props = HugoDeployProps(
            domain_name=domain_name, public_dir=public_dir, region=region
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicDir")
    def public_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))


@jsii.data_type(
    jsii_type="cdk-hugo-deploy.HugoDeployProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "public_dir": "publicDir",
        "region": "region",
    },
)
class HugoDeployProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        public_dir: builtins.str,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain_name: Domain name of the site deploying to. You should already have a hosted zone in the account you're deploying to with this domain name
        :param public_dir: Path to Hugo public directory, which is generated after running the ``hugo`` command. By default, this will be the ``public`` directory in your hugo project
        :param region: Region deploying to. Default: - us-east-1
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "public_dir": public_dir,
        }
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Domain name of the site deploying to.

        You should already have a hosted zone in the account you're deploying to with this domain name
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def public_dir(self) -> builtins.str:
        '''Path to Hugo public directory, which is generated after running the ``hugo`` command.

        By default, this will be the ``public`` directory in your hugo project
        '''
        result = self._values.get("public_dir")
        assert result is not None, "Required property 'public_dir' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region deploying to.

        :default: - us-east-1
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HugoDeployProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HugoDeploy",
    "HugoDeployProps",
]

publication.publish()
