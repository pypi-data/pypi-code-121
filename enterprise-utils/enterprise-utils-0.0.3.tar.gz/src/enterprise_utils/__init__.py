'''
# replace this
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


class PythonLambdaWithPrivatePypi(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@professionalaf/enterprise-utils.PythonLambdaWithPrivatePypi",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        code_path: builtins.str,
        index_url: builtins.str,
        trusted_host: builtins.str,
        handler: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code_path: Relative path to function code.
        :param index_url: --index-url for private pypi repo.
        :param trusted_host: --trusted-host for private repo.
        :param handler: Handler location. Default: - 'index.handler'
        '''
        props = PythonLambdaWithPrivatePypiProps(
            code_path=code_path,
            index_url=index_url,
            trusted_host=trusted_host,
            handler=handler,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codePath")
    def code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "codePath"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="indexUrl")
    def index_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustedHost")
    def trusted_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trustedHost"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "handler"))


@jsii.data_type(
    jsii_type="@professionalaf/enterprise-utils.PythonLambdaWithPrivatePypiProps",
    jsii_struct_bases=[],
    name_mapping={
        "code_path": "codePath",
        "index_url": "indexUrl",
        "trusted_host": "trustedHost",
        "handler": "handler",
    },
)
class PythonLambdaWithPrivatePypiProps:
    def __init__(
        self,
        *,
        code_path: builtins.str,
        index_url: builtins.str,
        trusted_host: builtins.str,
        handler: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param code_path: Relative path to function code.
        :param index_url: --index-url for private pypi repo.
        :param trusted_host: --trusted-host for private repo.
        :param handler: Handler location. Default: - 'index.handler'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "code_path": code_path,
            "index_url": index_url,
            "trusted_host": trusted_host,
        }
        if handler is not None:
            self._values["handler"] = handler

    @builtins.property
    def code_path(self) -> builtins.str:
        '''Relative path to function code.'''
        result = self._values.get("code_path")
        assert result is not None, "Required property 'code_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_url(self) -> builtins.str:
        '''--index-url for private pypi repo.'''
        result = self._values.get("index_url")
        assert result is not None, "Required property 'index_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def trusted_host(self) -> builtins.str:
        '''--trusted-host for private repo.'''
        result = self._values.get("trusted_host")
        assert result is not None, "Required property 'trusted_host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def handler(self) -> typing.Optional[builtins.str]:
        '''Handler location.

        :default: - 'index.handler'
        '''
        result = self._values.get("handler")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonLambdaWithPrivatePypiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PythonLambdaWithPrivatePypi",
    "PythonLambdaWithPrivatePypiProps",
]

publication.publish()
