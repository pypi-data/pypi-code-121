'''
# AWS ELBv2 Redirection CDK Construct Library

This library makes it easy to creation redirection rules on Application Load Balancers.

## Usage

### Base redirection construct (Typescript)

```python
// create a vpc
const vpc = new ec2.Vpc(stack, 'vpc');

// create an alb in that vpc
const alb = new elbv2.ApplicationLoadBalancer(stack, 'alb', {
  internetFacing: true,
  vpc,
});

// create a redirect from 8080 to 8443
new Redirect(stack, 'redirect', {
  alb,
  sourcePort: 8080,
  sourceProtocol: elbv2.ApplicationProtocol.HTTP,
  targetPort: 8443,
  targetProtocol: elbv2.ApplicationProtocol.HTTPS,
});
```

### Using the pre-build HTTP to HTTPS construct (Typescript)

```python
// create a vpc
const vpc = new ec2.Vpc(stack, 'vpc');

// create an alb in that vpc
const alb = new elbv2.ApplicationLoadBalancer(stack, 'alb', {
  internetFacing: true,
  vpc,
});

// use the pre-built construct for HTTP to HTTPS
new RedirectHttpHttps(stack, 'redirectHttpHttps', {
  alb,
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

from ._jsii import *

import aws_cdk.aws_elasticloadbalancingv2
import constructs


class Redirect(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.Redirect",
):
    '''A base redirect construct that takes source and destination ports and protocols.

    Common use cases can be built from this construct
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alb: aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer,
        source_port: jsii.Number,
        source_protocol: aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol,
        target_port: jsii.Number,
        target_protocol: aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alb: The application load balancer this redirect applies to.
        :param source_port: The source port to redirect from.
        :param source_protocol: The source protocol to redirect from.
        :param target_port: The target port to redirect to.
        :param target_protocol: The target protocol to redirect to.
        '''
        props = RedirectProps(
            alb=alb,
            source_port=source_port,
            source_protocol=source_protocol,
            target_port=target_port,
            target_protocol=target_protocol,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class RedirectHttpHttps(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.RedirectHttpHttps",
):
    '''A construct that redirects HTTP to HTTPS for the given application load balancer.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alb: aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alb: The application load balancer this redirect applies to.
        '''
        props = RedirectHttpHttpsProps(alb=alb)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.RedirectHttpHttpsProps",
    jsii_struct_bases=[],
    name_mapping={"alb": "alb"},
)
class RedirectHttpHttpsProps:
    def __init__(
        self,
        *,
        alb: aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer,
    ) -> None:
        '''Properties for the RedirectHttpHttps construct.

        :param alb: The application load balancer this redirect applies to.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alb": alb,
        }

    @builtins.property
    def alb(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer:
        '''The application load balancer this redirect applies to.'''
        result = self._values.get("alb")
        assert result is not None, "Required property 'alb' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedirectHttpHttpsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.RedirectProps",
    jsii_struct_bases=[],
    name_mapping={
        "alb": "alb",
        "source_port": "sourcePort",
        "source_protocol": "sourceProtocol",
        "target_port": "targetPort",
        "target_protocol": "targetProtocol",
    },
)
class RedirectProps:
    def __init__(
        self,
        *,
        alb: aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer,
        source_port: jsii.Number,
        source_protocol: aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol,
        target_port: jsii.Number,
        target_protocol: aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol,
    ) -> None:
        '''The properties for the base redirect construct.

        :param alb: The application load balancer this redirect applies to.
        :param source_port: The source port to redirect from.
        :param source_protocol: The source protocol to redirect from.
        :param target_port: The target port to redirect to.
        :param target_protocol: The target protocol to redirect to.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alb": alb,
            "source_port": source_port,
            "source_protocol": source_protocol,
            "target_port": target_port,
            "target_protocol": target_protocol,
        }

    @builtins.property
    def alb(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer:
        '''The application load balancer this redirect applies to.'''
        result = self._values.get("alb")
        assert result is not None, "Required property 'alb' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, result)

    @builtins.property
    def source_port(self) -> jsii.Number:
        '''The source port to redirect from.'''
        result = self._values.get("source_port")
        assert result is not None, "Required property 'source_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def source_protocol(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol:
        '''The source protocol to redirect from.'''
        result = self._values.get("source_protocol")
        assert result is not None, "Required property 'source_protocol' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol, result)

    @builtins.property
    def target_port(self) -> jsii.Number:
        '''The target port to redirect to.'''
        result = self._values.get("target_port")
        assert result is not None, "Required property 'target_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target_protocol(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol:
        '''The target protocol to redirect to.'''
        result = self._values.get("target_protocol")
        assert result is not None, "Required property 'target_protocol' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocol, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedirectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Redirect",
    "RedirectHttpHttps",
    "RedirectHttpHttpsProps",
    "RedirectProps",
]

publication.publish()
