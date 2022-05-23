'''
# static-site

Easily deploy a static site backed by s3 and CloudFront

## Usage

```python
import { pwed_static_site } from 'pwed-cdk';
import * as path from 'path';

const website = new pwed_static_site.StaticSite(this, 'PwedDotMe', {
  domain: 'pwed.me',
  path: path.join(__dirname, 'static'),
});
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk.aws_route53
import constructs


class StaticSite(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_static_site.StaticSite",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        path: builtins.str,
        hosted_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain: 
        :param path: 
        :param hosted_zone: 

        :stability: experimental
        '''
        props = StaticSiteProps(domain=domain, path=path, hosted_zone=hosted_zone)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_static_site.StaticSiteProps",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain", "path": "path", "hosted_zone": "hostedZone"},
)
class StaticSiteProps:
    def __init__(
        self,
        *,
        domain: builtins.str,
        path: builtins.str,
        hosted_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
    ) -> None:
        '''
        :param domain: 
        :param path: 
        :param hosted_zone: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "path": path,
        }
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone

    @builtins.property
    def domain(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticSiteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "StaticSite",
    "StaticSiteProps",
]

publication.publish()
